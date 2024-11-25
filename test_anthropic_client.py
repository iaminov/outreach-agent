from unittest.mock import MagicMock, Mock, patch

import pytest
from anthropic import APIError, RateLimitError

from anthropic_client import AnthropicClient


class TestAnthropicClient:
    @pytest.fixture
    def mock_anthropic(self):
        with patch("anthropic_client.anthropic.Anthropic") as mock:
            yield mock

    @pytest.fixture
    def client(self, mock_anthropic):
        return AnthropicClient(api_key="test_api_key")

    def test_init_with_api_key(self, mock_anthropic):
        client = AnthropicClient(api_key="test_key")
        assert client.api_key == "test_key"
        mock_anthropic.assert_called_once_with(api_key="test_key")

    def test_init_without_api_key_raises_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key is required"):
                AnthropicClient()

    def test_init_with_env_api_key(self, mock_anthropic):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "env_key"}):
            client = AnthropicClient()
            assert client.api_key == "env_key"

    def test_generate_outreach_message_success(self, client):
        mock_response = Mock()
        mock_response.content = [Mock(text="Generated message")]
        client.client.messages.create = Mock(return_value=mock_response)

        lead = {"name": "John Doe", "company": "TechCorp"}
        client_info = {"name": "Agency"}
        offer = "Marketing services"

        result = client.generate_outreach_message(lead, client_info, offer)

        assert result == "Generated message"
        client.client.messages.create.assert_called_once()

    def test_generate_outreach_message_missing_lead_fields(self, client):
        lead = {"name": "John Doe"}
        client_info = {"name": "Agency"}
        offer = "Marketing services"

        with pytest.raises(
            ValueError, match="Lead must contain 'name' and 'company' fields"
        ):
            client.generate_outreach_message(lead, client_info, offer)

    def test_generate_outreach_message_missing_client_info(self, client):
        lead = {"name": "John Doe", "company": "TechCorp"}
        client_info = {}
        offer = "Marketing services"

        with pytest.raises(ValueError, match="Client info must contain 'name' field"):
            client.generate_outreach_message(lead, client_info, offer)

    def test_generate_outreach_message_generic_error(self, client):
        client.client.messages.create = Mock(side_effect=Exception("Generic error"))

        lead = {"name": "John Doe", "company": "TechCorp"}
        client_info = {"name": "Agency"}
        offer = "Marketing services"

        with pytest.raises(Exception, match="Generic error"):
            client.generate_outreach_message(lead, client_info, offer)

    def test_build_prompt(self, client):
        lead = {"name": "John Doe", "company": "TechCorp"}
        client_info = {"name": "Agency"}
        offer = "Marketing services"

        prompt = client._build_prompt(lead, client_info, offer)

        assert "John Doe" in prompt
        assert "TechCorp" in prompt
        assert "Agency" in prompt
        assert "Marketing services" in prompt

    def test_test_connection_success(self, client):
        mock_response = Mock()
        mock_response.content = [Mock(text="Hello")]
        client.client.messages.create = Mock(return_value=mock_response)

        result = client.test_connection()

        assert result is True
        client.client.messages.create.assert_called_once()

    def test_test_connection_failure(self, client):
        client.client.messages.create = Mock(side_effect=Exception("Connection failed"))

        result = client.test_connection()

        assert result is False
