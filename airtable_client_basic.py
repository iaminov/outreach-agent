"""Basic Airtable client implementation."""

import requests

class AirtableClient:
    def __init__(self, base_id, api_key):
        self.base_id = base_id
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }
    
    def get_records(self, table_name):
        # TODO: Implement record retrieval
        pass
