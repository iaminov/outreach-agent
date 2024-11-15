import os
import logging
import requests
from requests.exceptions import RequestException, HTTPError

logger = logging.getLogger(__name__)

class ClickUpClient:
    """Advanced client for ClickUp API with comprehensive error handling and task management."""
    
    def __init__(self, api_key: str | None = None):
        """
        Initialize the ClickUp client.
        
        Args:
            api_key: ClickUp API key. If not provided, will use CLICKUP_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("CLICKUP_API_KEY")
        if not self.api_key:
            raise ValueError("ClickUp API key is required")
        
        self.base_url = "https://api.clickup.com/api/v2/"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        logger.info("ClickUp client initialized successfully")
    
    def create_task(self, list_id: str, name: str, description: str | None = None, 
                   due_date: str | None = None, priority: int | None = None) -> dict:
        """
        Create a new task in ClickUp with comprehensive options.
        
        Args:
            list_id: ClickUp list ID where the task will be created
            name: Task name/title
            description: Task description (optional)
            due_date: Due date in ISO format (optional)
            priority: Task priority (1-4, optional)
            
        Returns:
            Response from ClickUp API
            
        Raises:
            HTTPError: If the API request fails
            RequestException: If there's a network or connection error
            ValueError: If required parameters are invalid
        """
        if not list_id or not name:
            raise ValueError("list_id and name are required")
        
        try:
            logger.info(f"Creating ClickUp task: {name}")
            
            data = {"name": name}
            
            if description:
                data["description"] = description
            if due_date:
                data["due_date"] = due_date
            if priority and 1 <= priority <= 4:
                data["priority"] = priority
            
            url = f"{self.base_url}list/{list_id}/task"
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully created ClickUp task: {name}")
            return result
            
        except HTTPError as e:
            logger.error(f"ClickUp API HTTP error creating task: {e}")
            if e.response.status_code == 401:
                logger.error("Authentication failed - check your API key")
            elif e.response.status_code == 404:
                logger.error("List not found - check your list ID")
            raise
        except RequestException as e:
            logger.error(f"Network error creating ClickUp task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating ClickUp task: {e}")
            raise
    
    def get_tasks(self, list_id: str, limit: int = 100) -> list[dict]:
        """
        Retrieve tasks from a ClickUp list.
        
        Args:
            list_id: ClickUp list ID
            limit: Maximum number of tasks to retrieve
            
        Returns:
            List of tasks from the specified list
        """
        try:
            logger.info(f"Retrieving tasks from list: {list_id}")
            
            url = f"{self.base_url}list/{list_id}/task"
            params = {"limit": limit}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            tasks = data.get('tasks', [])
            
            logger.info(f"Successfully retrieved {len(tasks)} tasks from ClickUp")
            return tasks
            
        except Exception as e:
            logger.error(f"Error retrieving tasks: {e}")
            raise
    
    def update_task(self, task_id: str, updates: dict) -> dict:
        """
        Update an existing ClickUp task.
        
        Args:
            task_id: ClickUp task ID
            updates: Dictionary containing fields to update
            
        Returns:
            Updated task data from ClickUp API
        """
        try:
            logger.info(f"Updating ClickUp task: {task_id}")
            
            url = f"{self.base_url}task/{task_id}"
            response = requests.put(url, headers=self.headers, json=updates, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully updated ClickUp task: {task_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a ClickUp task.
        
        Args:
            task_id: ClickUp task ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Deleting ClickUp task: {task_id}")
            
            url = f"{self.base_url}task/{task_id}"
            response = requests.delete(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Successfully deleted ClickUp task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False
    
    def get_lists(self, space_id: str) -> list[dict]:
        """
        Retrieve all lists from a ClickUp space.
        
        Args:
            space_id: ClickUp space ID
            
        Returns:
            List of lists from the specified space
        """
        try:
            logger.info(f"Retrieving lists from space: {space_id}")
            
            url = f"{self.base_url}space/{space_id}/list"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            lists = data.get('lists', [])
            
            logger.info(f"Successfully retrieved {len(lists)} lists from ClickUp")
            return lists
            
        except Exception as e:
            logger.error(f"Error retrieving lists: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test the API connection and authentication.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            url = f"{self.base_url}user"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info("ClickUp API connection test successful")
            return True
        except Exception as e:
            logger.error(f"ClickUp API connection test failed: {e}")
            return False 