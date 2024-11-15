import os
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from anthropic_client import AnthropicClient
from email_sender import EmailSender
from airtable_client import AirtableClient
from clickup_client import ClickUpClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outreach_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class OutreachConfig:
    """Configuration class for the outreach agent system."""
    anthropic_api_key: str
    airtable_api_key: str
    airtable_base_id: str
    airtable_table_name: str
    clickup_api_key: str
    clickup_list_id: str
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    from_email: str
    client_info: dict[str, str]
    offer: str

class OutreachAgent:
    """Advanced outreach agent that orchestrates multi-platform lead generation and follow-up."""
    
    def __init__(self, config: OutreachConfig):
        self.config = config
        self._initialize_clients()
        self.performance_metrics = {
            'total_processing_time': 0,
            'message_generation_time': 0,
            'email_sending_time': 0,
            'task_creation_time': 0
        }
        
    def _initialize_clients(self) -> None:
        """Initialize all API clients with proper error handling."""
        try:
            self.anthropic_client = AnthropicClient(api_key=self.config.anthropic_api_key)
            self.email_sender = EmailSender(
                self.config.smtp_server, 
                self.config.smtp_port, 
                self.config.smtp_username, 
                self.config.smtp_password
            )
            self.airtable_client = AirtableClient(
                self.config.airtable_base_id, 
                self.config.airtable_table_name, 
                api_key=self.config.airtable_api_key
            )
            self.clickup_client = ClickUpClient(api_key=self.config.clickup_api_key)
            logger.info("All clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")
            raise
    
    def _validate_lead_data(self, lead: dict) -> bool:
        """Validate lead data completeness and format."""
        required_fields = ['Name', 'Company', 'Email']
        missing_fields = [field for field in required_fields if not lead.get(field)]
        
        if missing_fields:
            logger.warning(f"Lead missing required fields: {missing_fields}")
            return False
            
        if '@' not in lead.get('Email', ''):
            logger.warning(f"Invalid email format for lead: {lead.get('Name')}")
            return False
            
        return True
    
    def _generate_personalized_message(self, lead: dict) -> str | None:
        """Generate personalized outreach message using AI."""
        start_time = time.time()
        try:
            lead_dict = {
                "name": lead['Name'],
                "company": lead['Company']
            }
            message = self.anthropic_client.generate_outreach_message(
                lead_dict, 
                self.config.client_info, 
                self.config.offer
            )
            processing_time = time.time() - start_time
            self.performance_metrics['message_generation_time'] += processing_time
            logger.info(f"Generated personalized message for {lead['Name']} at {lead['Company']} in {processing_time:.2f}s")
            return message
        except Exception as e:
            logger.error(f"Failed to generate message for {lead.get('Name', 'Unknown')}: {e}")
            return None
    
    def _send_outreach_email(self, lead: dict, message: str) -> bool:
        """Send outreach email with proper error handling."""
        start_time = time.time()
        try:
            subject = f"Let's help {lead['Company']} grow!"
            self.email_sender.send_email(
                lead['Email'], 
                subject, 
                message, 
                from_email=self.config.from_email
            )
            processing_time = time.time() - start_time
            self.performance_metrics['email_sending_time'] += processing_time
            logger.info(f"Successfully sent email to {lead['Name']} <{lead['Email']}> in {processing_time:.2f}s")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {lead.get('Name', 'Unknown')}: {e}")
            return False
    
    def _create_followup_task(self, lead: dict, message: str) -> bool:
        """Create follow-up task in ClickUp."""
        start_time = time.time()
        try:
            task_name = f"Follow up with {lead['Name']} at {lead['Company']}"
            self.clickup_client.create_task(
                self.config.clickup_list_id, 
                task_name, 
                description=message
            )
            processing_time = time.time() - start_time
            self.performance_metrics['task_creation_time'] += processing_time
            logger.info(f"Created ClickUp task for {lead['Name']} at {lead['Company']} in {processing_time:.2f}s")
            return True
        except Exception as e:
            logger.error(f"Failed to create ClickUp task for {lead.get('Name', 'Unknown')}: {e}")
            return False
    
    def process_lead(self, lead: dict) -> dict[str, bool]:
        """Process a single lead through the complete outreach workflow."""
        results = {
            'validation': False,
            'message_generation': False,
            'email_sent': False,
            'task_created': False
        }
        
        if not self._validate_lead_data(lead):
            return results
        
        results['validation'] = True
        
        message = self._generate_personalized_message(lead)
        if not message:
            return results
        
        results['message_generation'] = True
        
        if self._send_outreach_email(lead, message):
            results['email_sent'] = True
        
        if self._create_followup_task(lead, message):
            results['task_created'] = True
        
        return results
    
    def run_outreach_campaign(self) -> dict[str, int]:
        """Execute the complete outreach campaign with comprehensive reporting."""
        campaign_start = time.time()
        logger.info("Starting outreach campaign")
        
        campaign_stats = {
            'total_leads': 0,
            'validated_leads': 0,
            'messages_generated': 0,
            'emails_sent': 0,
            'tasks_created': 0,
            'failed_leads': 0
        }
        
        try:
            leads = self.airtable_client.get_leads()
            campaign_stats['total_leads'] = len(leads)
            logger.info(f"Retrieved {len(leads)} leads from Airtable")
            
            for record in leads:
                lead = record['fields']
                results = self.process_lead(lead)
                
                if results['validation']:
                    campaign_stats['validated_leads'] += 1
                if results['message_generation']:
                    campaign_stats['messages_generated'] += 1
                if results['email_sent']:
                    campaign_stats['emails_sent'] += 1
                if results['task_created']:
                    campaign_stats['tasks_created'] += 1
                if not any(results.values()):
                    campaign_stats['failed_leads'] += 1
                    
        except Exception as e:
            logger.error(f"Campaign execution failed: {e}")
            raise
        
        total_time = time.time() - campaign_start
        self.performance_metrics['total_processing_time'] = total_time
        
        logger.info(f"Campaign completed in {total_time:.2f}s. Stats: {campaign_stats}")
        return campaign_stats
    
    def get_performance_metrics(self, campaign_stats: dict[str, int]) -> dict[str, float]:
        """Get detailed performance metrics for the campaign."""
        return {
            'total_processing_time': self.performance_metrics['total_processing_time'],
            'message_generation_time': self.performance_metrics['message_generation_time'],
            'email_sending_time': self.performance_metrics['email_sending_time'],
            'task_creation_time': self.performance_metrics['task_creation_time'],
            'average_message_time': self.performance_metrics['message_generation_time'] / max(campaign_stats.get('messages_generated', 1), 1),
            'average_email_time': self.performance_metrics['email_sending_time'] / max(campaign_stats.get('emails_sent', 1), 1),
            'average_task_time': self.performance_metrics['task_creation_time'] / max(campaign_stats.get('tasks_created', 1), 1)
        }

def load_configuration() -> OutreachConfig:
    """Load and validate all configuration from environment variables."""
    required_vars = {
        'ANTHROPIC_API_KEY': os.getenv("ANTHROPIC_API_KEY"),
        'AIRTABLE_API_KEY': os.getenv("AIRTABLE_API_KEY"),
        'AIRTABLE_BASE_ID': os.getenv("AIRTABLE_BASE_ID"),
        'AIRTABLE_TABLE_NAME': os.getenv("AIRTABLE_TABLE_NAME"),
        'CLICKUP_API_KEY': os.getenv("CLICKUP_API_KEY"),
        'CLICKUP_LIST_ID': os.getenv("CLICKUP_LIST_ID"),
        'SMTP_SERVER': os.getenv("SMTP_SERVER"),
        'SMTP_USERNAME': os.getenv("SMTP_USERNAME"),
        'SMTP_PASSWORD': os.getenv("SMTP_PASSWORD"),
        'FROM_EMAIL': os.getenv("FROM_EMAIL")
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return OutreachConfig(
        anthropic_api_key=required_vars['ANTHROPIC_API_KEY'],
        airtable_api_key=required_vars['AIRTABLE_API_KEY'],
        airtable_base_id=required_vars['AIRTABLE_BASE_ID'],
        airtable_table_name=required_vars['AIRTABLE_TABLE_NAME'],
        clickup_api_key=required_vars['CLICKUP_API_KEY'],
        clickup_list_id=required_vars['CLICKUP_LIST_ID'],
        smtp_server=required_vars['SMTP_SERVER'],
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=required_vars['SMTP_USERNAME'],
        smtp_password=required_vars['SMTP_PASSWORD'],
        from_email=required_vars['FROM_EMAIL'],
        client_info={"name": "SuperGrowth Agency"},
        offer="cutting-edge digital marketing solutions that increase qualified leads by 30% in 90 days"
    )

def main():
    """Main entry point with comprehensive error handling and logging."""
    try:
        logger.info("Initializing outreach agent system")
        config = load_configuration()
        
        agent = OutreachAgent(config)
        campaign_stats = agent.run_outreach_campaign()
        
        performance_metrics = agent.get_performance_metrics(campaign_stats)
        
        logger.info("Outreach campaign completed successfully")
        print(f"\nCampaign Summary:")
        print(f"Total Leads: {campaign_stats['total_leads']}")
        print(f"Validated: {campaign_stats['validated_leads']}")
        print(f"Messages Generated: {campaign_stats['messages_generated']}")
        print(f"Emails Sent: {campaign_stats['emails_sent']}")
        print(f"Tasks Created: {campaign_stats['tasks_created']}")
        print(f"Failed: {campaign_stats['failed_leads']}")
        
        print(f"\nPerformance Metrics:")
        print(f"Total Processing Time: {performance_metrics['total_processing_time']:.2f}s")
        print(f"Average Message Generation: {performance_metrics['average_message_time']:.2f}s")
        print(f"Average Email Sending: {performance_metrics['average_email_time']:.2f}s")
        print(f"Average Task Creation: {performance_metrics['average_task_time']:.2f}s")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 