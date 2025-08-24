import os
import logging
import time
import anthropic
from anthropic import APIError, RateLimitError

logger = logging.getLogger(__name__)

class AnthropicClient:
    """Client for Anthropic Claude AI API with error handling and logging."""
    
    def __init__(self, api_key: str | None = None):
        """
        Initialize the Anthropic client.
        
        Args:
            api_key: Anthropic API key. If not provided, will use ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("Anthropic client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
    
    def generate_outreach_message(self, lead: dict[str, str], client_info: dict[str, str], offer: str, max_retries: int = 3) -> str:
        """
        Generate a personalized outreach message using Claude AI with retry mechanism.
        
        Args:
            lead: Dictionary containing lead information (name, company)
            client_info: Dictionary containing client information (name)
            offer: Description of the service offer
            max_retries: Maximum number of retry attempts for rate limit errors
            
        Returns:
            Generated personalized message
            
        Raises:
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded after retries
            ValueError: If required parameters are missing
        """
        if not all(key in lead for key in ['name', 'company']):
            raise ValueError("Lead must contain 'name' and 'company' fields")
        
        if 'name' not in client_info:
            raise ValueError("Client info must contain 'name' field")
        
        prompt = self._build_prompt(lead, client_info, offer)
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Generating message for {lead['name']} at {lead['company']} (attempt {attempt + 1})")
                
                response = self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=400,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                message = response.content[0].text
                logger.info(f"Successfully generated message for {lead['name']}")
                return message
                
            except RateLimitError as e:
                if attempt < max_retries:
                    wait_time = (2 ** attempt) * 1
                    logger.warning(f"Rate limit hit, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Rate limit exceeded after {max_retries} retries: {e}")
                    raise
            except APIError as e:
                logger.error(f"Anthropic API error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error generating message: {e}")
                raise
    
    def _build_prompt(self, lead: dict[str, str], client_info: dict[str, str], offer: str) -> str:
        """
        Build a comprehensive prompt for message generation.
        
        Args:
            lead: Lead information
            client_info: Client information
            offer: Service offer description
            
        Returns:
            Formatted prompt string
        """
        return (
            f"You are an expert sales agent specializing in personalized outreach. "
            f"Write a compelling, personalized cold outreach email to {lead['name']} "
            f"at {lead['company']}. "
            f"\n\nContext:"
            f"\n- You represent {client_info['name']}"
            f"\n- Your offer: {offer}"
            f"\n- Target: {lead['name']} at {lead['company']}"
            f"\n\nRequirements:"
            f"\n- Make the message friendly, concise, and highly personalized"
            f"\n- Reference specific aspects of {lead['company']} that make them a good fit"
            f"\n- Avoid generic language - be specific and relevant"
            f"\n- Include a clear, compelling call to action"
            f"\n- Keep the tone professional but approachable"
            f"\n- Maximum 150 words"
            f"\n\nGenerate the email body only (no subject line):"
        )
    
    def test_connection(self) -> bool:
        """
        Test the API connection and authentication.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            logger.info("Anthropic API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Anthropic API connection test failed: {e}")
            return False 