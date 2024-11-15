import os
import logging
import requests
from requests.exceptions import RequestException, HTTPError

logger = logging.getLogger(__name__)

class AirtableClient:
    """Advanced client for Airtable API with comprehensive error handling and data validation."""
    
    def __init__(self, base_id: str, table_name: str, api_key: str | None = None):
        """
        Initialize the Airtable client.
        
        Args:
            base_id: Airtable base ID
            table_name: Name of the table containing leads
            api_key: Airtable API key. If not provided, will use AIRTABLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("AIRTABLE_API_KEY")
        if not self.api_key:
            raise ValueError("Airtable API key is required")
        
        self.base_id = base_id
        self.table_name = table_name
        self.endpoint = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Airtable client initialized for base: {base_id}, table: {table_name}")
    
    def get_leads(self) -> list[dict]:
        """
        Retrieve all leads from the Airtable base.
        
        Returns:
            List of lead records from Airtable
            
        Raises:
            HTTPError: If the API request fails
            RequestException: If there's a network or connection error
            ValueError: If the response format is invalid
        """
        try:
            logger.info(f"Retrieving leads from Airtable table: {self.table_name}")
            
            response = requests.get(self.endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            records = data.get('records', [])
            
            logger.info(f"Successfully retrieved {len(records)} leads from Airtable")
            return records
            
        except HTTPError as e:
            logger.error(f"Airtable API HTTP error: {e}")
            if e.response.status_code == 401:
                logger.error("Authentication failed - check your API key")
            elif e.response.status_code == 404:
                logger.error("Base or table not found - check your base ID and table name")
            raise
        except RequestException as e:
            logger.error(f"Network error connecting to Airtable: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid response format from Airtable: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving leads: {e}")
            raise
    
    def add_lead(self, lead: dict) -> dict:
        """
        Add a new lead to the Airtable base.
        
        Args:
            lead: Dictionary containing lead information
            
        Returns:
            Response from Airtable API
            
        Raises:
            HTTPError: If the API request fails
            RequestException: If there's a network or connection error
            ValueError: If the lead data is invalid
        """
        if not isinstance(lead, dict):
            raise ValueError("Lead must be a dictionary")
        
        try:
            logger.info(f"Adding new lead to Airtable: {lead.get('Name', 'Unknown')}")
            
            data = {"fields": lead}
            response = requests.post(self.endpoint, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully added lead: {lead.get('Name', 'Unknown')}")
            return result
            
        except HTTPError as e:
            logger.error(f"Airtable API HTTP error adding lead: {e}")
            raise
        except RequestException as e:
            logger.error(f"Network error adding lead to Airtable: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding lead: {e}")
            raise
    
    def update_lead(self, record_id: str, lead: dict) -> dict:
        """
        Update an existing lead in the Airtable base.
        
        Args:
            record_id: Airtable record ID
            lead: Dictionary containing updated lead information
            
        Returns:
            Response from Airtable API
        """
        try:
            logger.info(f"Updating lead in Airtable: {lead.get('Name', 'Unknown')}")
            
            data = {"fields": lead}
            response = requests.patch(
                f"{self.endpoint}/{record_id}", 
                headers=self.headers, 
                json=data, 
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully updated lead: {lead.get('Name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error updating lead: {e}")
            raise
    
    def delete_lead(self, record_id: str) -> bool:
        """
        Delete a lead from the Airtable base.
        
        Args:
            record_id: Airtable record ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Deleting lead from Airtable: {record_id}")
            
            response = requests.delete(
                f"{self.endpoint}/{record_id}", 
                headers=self.headers, 
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Successfully deleted lead: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting lead: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test the API connection and authentication.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = requests.get(self.endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info("Airtable API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Airtable API connection test failed: {e}")
            return False 
