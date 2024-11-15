import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os
from smtplib import SMTPException

logger = logging.getLogger(__name__)

class EmailSender:
    """Advanced email sender with comprehensive error handling and logging."""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """
        Initialize the email sender.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            username: Email username/account
            password: Email password or app password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        
        logger.info(f"Email sender initialized for {username} via {smtp_server}:{smtp_port}")
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: str | None = None) -> bool:
        """
        Send an email with comprehensive error handling.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content
            from_email: Sender email address (optional, defaults to username)
            
        Returns:
            True if email sent successfully, False otherwise
            
        Raises:
            SMTPException: If SMTP operation fails
            ValueError: If email parameters are invalid
        """
        if not all([to_email, subject, body]):
            raise ValueError("to_email, subject, and body are required")
        
        if '@' not in to_email:
            raise ValueError("Invalid recipient email address")
        
        try:
            logger.info(f"Sending email to {to_email}")
            
            msg = MIMEMultipart()
            msg['From'] = formataddr(("Outreach Agent", from_email or self.username))
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Successfully sent email to {to_email}")
            return True
            
        except SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            raise
    
    def send_bulk_emails(self, email_list: list, subject: str, body: str, from_email: str | None = None) -> dict:
        """
        Send emails to multiple recipients with detailed reporting.
        
        Args:
            email_list: List of recipient email addresses
            subject: Email subject line
            body: Email body content
            from_email: Sender email address (optional)
            
        Returns:
            Dictionary with success/failure counts and details
        """
        results = {
            'total': len(email_list),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        logger.info(f"Starting bulk email send to {len(email_list)} recipients")
        
        for email in email_list:
            try:
                if self.send_email(email, subject, body, from_email):
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to send to {email}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error sending to {email}: {str(e)}")
                logger.error(f"Error in bulk send to {email}: {e}")
        
        logger.info(f"Bulk email completed: {results['successful']} successful, {results['failed']} failed")
        return results
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection and authentication.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.username, self.password)
                logger.info("SMTP connection test successful")
                return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False
    
    def get_server_info(self) -> dict:
        """
        Get SMTP server information.
        
        Returns:
            Dictionary with server configuration details
        """
        return {
            'server': self.smtp_server,
            'port': self.smtp_port,
            'username': self.username,
            'encryption': 'TLS'
        } 