from unittest.mock import Mock, patch

import pytest
import requests
from requests.exceptions import HTTPError, RequestException

from airtable_client import AirtableClient


class TestAirtableClient:
    @pytest.fixture
    def client(self):
        return AirtableClient(
            base_id="test_base", table_name="test_table", api_key="test_key"
        )

    def test_init_with_api_key(self):
        client = AirtableClient(base_id="base123", table_name="Leads", api_key="key123")
        assert client.api_key == "key123"
        assert client.base_id == "base123"
        assert client.table_name == "Leads"
        assert client.endpoint == "https://api.airtable.com/v0/base123/Leads"

    def test_init_without_api_key_raises_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Airtable API key is required"):
                AirtableClient(base_id="base", table_name="table")

    def test_init_with_env_api_key(self):
        with patch.dict("os.environ", {"AIRTABLE_API_KEY": "env_key"}):
            client = AirtableClient(base_id="base", table_name="table")
            assert client.api_key == "env_key"

    @patch("requests.get")
    def test_get_leads_success(self, mock_get, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "records": [
                {"id": "rec1", "fields": {"Name": "John", "Company": "Corp"}},
                {"id": "rec2", "fields": {"Name": "Jane", "Company": "Inc"}},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = client.get_leads()

        assert len(result) == 2
        assert result[0]["fields"]["Name"] == "John"
        mock_get.assert_called_once_with(
            client.endpoint, headers=client.headers, timeout=30
        )

    @patch("requests.get")
    def test_get_leads_http_error_401(self, mock_get, client):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        with pytest.raises(HTTPError):
            client.get_leads()

    @patch("requests.get")
    def test_get_leads_network_error(self, mock_get, client):
        mock_get.side_effect = RequestException("Network error")

        with pytest.raises(RequestException):
            client.get_leads()

    @patch("requests.post")
    def test_add_lead_success(self, mock_post, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "rec123",
            "fields": {"Name": "John", "Company": "Corp", "Email": "john@corp.com"},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        lead = {"Name": "John", "Company": "Corp", "Email": "john@corp.com"}
        result = client.add_lead(lead)

        assert result["id"] == "rec123"
        mock_post.assert_called_once()

    def test_add_lead_invalid_type(self, client):
        with pytest.raises(ValueError, match="Lead must be a dictionary"):
            client.add_lead("not a dict")

    @patch("requests.patch")
    def test_update_lead_success(self, mock_patch, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "rec123",
            "fields": {"Name": "John Updated"},
        }
        mock_response.raise_for_status = Mock()
        mock_patch.return_value = mock_response

        lead = {"Name": "John Updated"}
        result = client.update_lead("rec123", lead)

        assert result["fields"]["Name"] == "John Updated"
        mock_patch.assert_called_once()

    def test_update_lead_invalid_type(self, client):
        with pytest.raises(ValueError, match="Lead must be a dictionary"):
            client.update_lead("rec123", "not a dict")

    @patch("requests.delete")
    def test_delete_lead_success(self, mock_delete, client):
        mock_response = Mock()
        mock_response.json.return_value = {"deleted": True, "id": "rec123"}
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        result = client.delete_lead("rec123")

        assert result["deleted"] is True
        assert result["id"] == "rec123"
        mock_delete.assert_called_once_with(
            f"{client.endpoint}/rec123", headers=client.headers, timeout=30
        )

    @patch("requests.get")
    def test_test_connection_success(self, mock_get, client):
        mock_response = Mock()
        mock_response.json.return_value = {"records": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = client.test_connection()

        assert result is True
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_test_connection_failure(self, mock_get, client):
        mock_get.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            client.test_connection()
