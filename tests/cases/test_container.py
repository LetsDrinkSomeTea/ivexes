"""Test cases for the container module.

This module contains comprehensive unit tests for Docker container management
functionality, including container lifecycle, error handling, and resource management.
"""

import unittest
from unittest.mock import patch, MagicMock
import docker

from ivexes.container import find_by_name, remove_if_exists


class TestContainerModule(unittest.TestCase):
    """Test cases for the container module."""

    def test_find_by_name_success(self):
        """Test finding a container by name when it exists."""
        # Mock the Docker client and container
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.name = 'test-container'
        mock_client.containers.list.return_value = [mock_container]

        # Call the function
        result = find_by_name(mock_client, 'test-container')

        # Verify the result
        self.assertEqual(result, mock_container)
        mock_client.containers.list.assert_called_once_with(all=True)

    def test_find_by_name_not_found(self):
        """Test finding a container by name when it doesn't exist."""
        # Mock the Docker client with no containers
        mock_client = MagicMock()
        mock_client.containers.list.return_value = []

        # Call the function
        result = find_by_name(mock_client, 'non-existent-container')

        # Verify the result
        self.assertIsNone(result)
        mock_client.containers.list.assert_called_once_with(all=True)

    def test_find_by_name_multiple_containers(self):
        """Test finding a container by name when multiple containers exist."""
        # Mock the Docker client with multiple containers
        mock_client = MagicMock()
        mock_container1 = MagicMock()
        mock_container1.name = 'container1'
        mock_container2 = MagicMock()
        mock_container2.name = 'target-container'
        mock_container3 = MagicMock()
        mock_container3.name = 'container3'
        mock_client.containers.list.return_value = [
            mock_container1,
            mock_container2,
            mock_container3,
        ]

        # Call the function
        result = find_by_name(mock_client, 'target-container')

        # Verify the result
        self.assertEqual(result, mock_container2)
        mock_client.containers.list.assert_called_once_with(all=True)

    def test_find_by_name_docker_error(self):
        """Test finding a container by name when Docker client fails."""
        # Mock the Docker client to raise an exception
        mock_client = MagicMock()
        mock_client.containers.list.side_effect = docker.errors.DockerException(
            'Docker daemon not running'
        )

        # Verify that the function raises the exception
        with self.assertRaises(docker.errors.DockerException):
            find_by_name(mock_client, 'test-container')

    def test_remove_if_exists_container_exists(self):
        """Test removing a container that exists."""
        # Mock the client and container
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.name = 'test-container'
        mock_client.containers.list.return_value = [mock_container]

        # Call the function
        result = remove_if_exists(mock_client, 'test-container')

        # Verify the container was removed
        self.assertTrue(result)
        mock_container.stop.assert_called_once()
        mock_container.wait.assert_called_once()
        mock_container.remove.assert_called_once_with(force=True)

    def test_remove_if_exists_container_not_found(self):
        """Test removing a container that doesn't exist."""
        # Mock the client with no containers
        mock_client = MagicMock()
        mock_client.containers.list.return_value = []

        # Call the function (should not raise any exception)
        result = remove_if_exists(mock_client, 'non-existent-container')

        # Verify no removal was attempted
        self.assertFalse(result)
        mock_client.containers.list.assert_called_once_with(all=True)

    def test_remove_if_exists_removal_error(self):
        """Test removing a container when removal fails."""
        # Mock the client and container
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.name = 'test-container'
        mock_container.remove.side_effect = docker.errors.APIError(
            'Container removal failed'
        )
        mock_client.containers.list.return_value = [mock_container]

        # Verify that the function raises the exception
        with self.assertRaises(docker.errors.APIError):
            remove_if_exists(mock_client, 'test-container')

        # Verify removal was attempted
        mock_container.stop.assert_called_once()
        mock_container.wait.assert_called_once()
        mock_container.remove.assert_called_once_with(force=True)

    def test_find_by_name_empty_name(self):
        """Test finding a container with empty name."""
        # Mock the Docker client
        mock_client = MagicMock()
        mock_client.containers.list.return_value = []

        # Call the function with empty name
        result = find_by_name(mock_client, '')

        # Verify the result
        self.assertIsNone(result)
        mock_client.containers.list.assert_called_once_with(all=True)

    def test_find_by_name_none_name(self):
        """Test finding a container with None name."""
        # Mock the Docker client
        mock_client = MagicMock()
        mock_client.containers.list.return_value = []

        # Call the function with None name
        result = find_by_name(mock_client, None)

        # Verify the result
        self.assertIsNone(result)
        mock_client.containers.list.assert_called_once_with(all=True)

    def test_find_by_name_partial_match(self):
        """Test that finding a container requires exact name match."""
        # Mock the Docker client with containers having similar names
        mock_client = MagicMock()
        mock_container1 = MagicMock()
        mock_container1.name = 'test-container-1'
        mock_container2 = MagicMock()
        mock_container2.name = 'test-container-extended'
        mock_client.containers.list.return_value = [mock_container1, mock_container2]

        # Call the function with partial name
        result = find_by_name(mock_client, 'test-container')

        # Verify no container is found (exact match required)
        self.assertIsNone(result)
        mock_client.containers.list.assert_called_once_with(all=True)

    def test_find_by_name_case_sensitivity(self):
        """Test that container name matching is case sensitive."""
        # Mock the Docker client
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.name = 'Test-Container'
        mock_client.containers.list.return_value = [mock_container]

        # Call the function with different case
        result = find_by_name(mock_client, 'test-container')

        # Verify no container is found (case sensitive)
        self.assertIsNone(result)
        mock_client.containers.list.assert_called_once_with(all=True)


if __name__ == '__main__':
    unittest.main()
