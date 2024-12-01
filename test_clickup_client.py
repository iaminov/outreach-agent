from unittest.mock import Mock, patch

import pytest
import requests
from requests.exceptions import HTTPError, RequestException

from clickup_client import ClickUpClient


class TestClickUpClient:
    @pytest.fixture
    def client(self):
        return ClickUpClient(api_key="test_api_key")

    def test_init_with_api_key(self):
        client = ClickUpClient(api_key="key123")
        assert client.api_key == "key123"
        assert client.base_url == "https://api.clickup.com/api/v2/"
        assert client.headers["Authorization"] == "key123"

    def test_init_without_api_key_raises_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="ClickUp API key is required"):
                ClickUpClient()

    def test_init_with_env_api_key(self):
        with patch.dict("os.environ", {"CLICKUP_API_KEY": "env_key"}):
            client = ClickUpClient()
            assert client.api_key == "env_key"

    @patch("requests.post")
    def test_create_task_success(self, mock_post, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "task123",
            "name": "Test Task",
            "description": "Test Description",
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = client.create_task(
            list_id="list123",
            name="Test Task",
            description="Test Description",
            priority=2,
        )

        assert result["id"] == "task123"
        assert result["name"] == "Test Task"
        mock_post.assert_called_once()

    def test_create_task_missing_required_params(self, client):
        with pytest.raises(ValueError, match="list_id and name are required"):
            client.create_task(list_id="", name="Task")

        with pytest.raises(ValueError, match="list_id and name are required"):
            client.create_task(list_id="list123", name="")

    @patch("requests.post")
    def test_create_task_http_error_401(self, mock_post, client):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        with pytest.raises(HTTPError):
            client.create_task("list123", "Task")

    @patch("requests.post")
    def test_create_task_network_error(self, mock_post, client):
        mock_post.side_effect = RequestException("Network error")

        with pytest.raises(RequestException):
            client.create_task("list123", "Task")

    @patch("requests.get")
    def test_get_tasks_success(self, mock_get, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "tasks": [
                {"id": "task1", "name": "Task 1"},
                {"id": "task2", "name": "Task 2"},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = client.get_tasks("list123")

        assert len(result) == 2
        assert result[0]["name"] == "Task 1"
        mock_get.assert_called_once()

    @patch("requests.put")
    def test_update_task_success(self, mock_put, client):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "task123", "name": "Updated Task"}
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response

        updates = {"name": "Updated Task"}
        result = client.update_task("task123", updates)

        assert result["name"] == "Updated Task"
        mock_put.assert_called_once()

    @patch("requests.delete")
    def test_delete_task_success(self, mock_delete, client):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        result = client.delete_task("task123")

        assert result is True
        mock_delete.assert_called_once()

    @patch("requests.delete")
    def test_delete_task_failure(self, mock_delete, client):
        mock_delete.side_effect = Exception("Delete failed")

        result = client.delete_task("task123")

        assert result is False

    @patch("requests.get")
    def test_get_lists_success(self, mock_get, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [
                {"id": "list1", "name": "List 1"},
                {"id": "list2", "name": "List 2"},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = client.get_lists("space123")

        assert len(result) == 2
        assert result[0]["name"] == "List 1"
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_test_connection_success(self, mock_get, client):
        mock_response = Mock()
        mock_response.json.return_value = {"user": {"id": "123", "username": "test"}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = client.test_connection()

        assert result is True
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_test_connection_failure(self, mock_get, client):
        mock_get.side_effect = Exception("Connection failed")

        result = client.test_connection()

        assert result is False
