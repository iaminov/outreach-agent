import os
import logging
from typing import Any, TypedDict

import requests
from requests.exceptions import RequestException, HTTPError

logger = logging.getLogger(__name__)

class Lead(TypedDict, total=False):
    """TypedDict for lead data for stronger type checking."""
    Name: str
    Company: str
    Email: str

class AirtableClient:
    """Client for Airtable API with error handling and data validation."""
    
    def __init__(self, base_id: str, table_name: str, api_key: str | None = None):
        """
        Initialize the Airtable client.

        Args:
            base_id: Airtable base ID.
            table_name: Name of the table containing leads.
            api_key: Airtable API key. If not provided, it uses the AIRTABLE_API_KEY environment variable.

        Raises:
            ValueError: If the API key is not provided and not found in environment variables.
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
    
    def get_leads(self) -> list[Lead]:
        """
        Retrieve all leads from the Airtable base.

        Returns:
            A list of dictionaries, where each dictionary represents a lead record.

        Raises:
            HTTPError: If the API request fails (e.g., 4xx or 5xx status codes).
            RequestException: If there's a network or connection error.
            ValueError: If the response from Airtable is not valid JSON.
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
    
    def add_lead(self, lead: Lead) -> dict[str, Any]:
        """
        Add a new lead to the Airtable base.

        Args:
            lead: A dictionary containing the lead's information.

        Returns:
            A dictionary representing the newly created lead record from Airtable.

        Raises:
            ValueError: If the provided lead is not a dictionary.
            HTTPError: If the API request fails.
            RequestException: If there's a network or connection error.
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
    
    def update_lead(self, record_id: str, lead: Lead) -> dict[str, Any]:
        """
        Update an existing lead in the Airtable base.

        Args:
            record_id: The ID of the Airtable record to update.
            lead: A dictionary containing the updated lead information.

        Returns:
            A dictionary representing the updated lead record from Airtable.

        Raises:
            ValueError: If the provided lead is not a dictionary.
            HTTPError: If the API request fails.
            RequestException: If there's a network or connection error.
        """
        if not isinstance(lead, dict):
            raise ValueError("Lead must be a dictionary")

        try:
            logger.info(f"Updating lead {record_id} in Airtable.")

            data = {"fields": lead}
            response = requests.patch(
                f"{self.endpoint}/{record_id}",
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Successfully updated lead {record_id}.")
            return result

        except HTTPError as e:
            logger.error(f"Airtable API HTTP error updating lead {record_id}: {e}")
            raise
        except RequestException as e:
            logger.error(f"Network error updating lead {record_id} in Airtable: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating lead {record_id}: {e}")
            raise
    
    def delete_lead(self, record_id: str) -> dict[str, Any]:
        """
        Delete a lead from the Airtable base.

        Args:
            record_id: The ID of the Airtable record to delete.

        Returns:
            A confirmation dictionary from Airtable, e.g., {'deleted': True, 'id': 'rec...'}.

        Raises:
            HTTPError: If the API request fails.
            RequestException: If there's a network or connection error.
        """
        try:
            logger.info(f"Deleting lead {record_id} from Airtable.")

            response = requests.delete(
                f"{self.endpoint}/{record_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Successfully deleted lead: {record_id}")
            return result

        except HTTPError as e:
            logger.error(f"Airtable API HTTP error deleting lead {record_id}: {e}")
            raise
        except RequestException as e:
            logger.error(f"Network error deleting lead {record_id} from Airtable: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting lead {record_id}: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test the API connection and authentication.

        Returns:
            True if the connection is successful, False otherwise.
        Raises:
            HTTPError: If the API request fails (e.g., invalid auth, not found).
            RequestException: If there's a network or connection error.
        """

        try:
            logger.info("Testing Airtable API connection...")
            response = requests.get(self.endpoint, headers=self.headers, params={"maxRecords": 1}, timeout=10)
            response.raise_for_status()
            logger.info("Airtable API connection test successful.")
            return True
        except HTTPError as e:
            logger.error(f"Airtable API connection test failed (HTTP error): {e}")
            raise
        except RequestException as e:
            logger.error(f"Airtable API connection test failed (Network error): {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during connection test: {e}")
            raise
