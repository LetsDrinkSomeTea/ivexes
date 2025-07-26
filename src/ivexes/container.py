"""Container utilities module.

This module provides utility functions for Docker container management
including container lookup and cleanup operations.
"""

import time
from typing import Optional, cast
import docker
from docker.models.containers import Container
from docker import DockerClient

import logging

logger = logging.getLogger(__name__)

_client: Optional[DockerClient] = None


def get_client() -> DockerClient:
    """Get or create a Docker client instance.

    Returns:
        DockerClient: A Docker client instance.
    """
    global _client
    if not _client:
        _client = docker.from_env()
    return _client


def find_by_name(container_name: str) -> Container | None:
    """Find a container by its name.

    Args:
        container_name (str): Name of the container to find.
    """
    client = get_client()
    c = [c for c in client.containers.list(all=True) if c.name == container_name]
    if len(c) > 0 and c[0]:
        container = cast(Container, c[0])
        # container already exists, ask for removal
        logger.info(f'Container {container.name} found exists.')
        while container.status != 'running':
            logger.info(
                f'Container {container.name} is not running, status: {container.status}. Starting it...'
            )
            container.start()
            time.sleep(10)  # Wait for the container to start
            container.reload()
        return c[0]
    return None


def cleanup(prefix: str = 'ivexes-') -> None:
    """Cleanup containers with a specific prefix.

    Args:
        prefix (str): Prefix of the containers to remove.
    """
    client = get_client()
    containers = [
        cast(Container, c)
        for c in client.containers.list(all=True)
        if c.name.startswith(prefix)
    ]
    for container in containers:
        logger.info(f'Removing container {container.name} with prefix {prefix}')
        try:
            container.remove(force=True)
            logger.info(f'Container {container.name} removed successfully.')
        except Exception as e:
            logger.error(f'Error removing container {container.name}: {e}')
    while len(containers) > 0:
        time.sleep(1)
        containers = [
            cast(Container, c)
            for c in client.containers.list(all=True)
            if c.name.startswith(prefix)
        ]
    time.sleep(5)  # Give some time for cleanup to complete


def remove_if_exists(container_name: str) -> bool:
    """Remove the container if it exists.

    Args:
        container_name (str): Name of the container to remove.

    Returns:
        bool: True if the container was removed, False if it did not exist.
    """
    container = find_by_name(container_name)
    if not container:
        logger.info(f'Container {container_name} not existing.')
        return False
    container.stop()
    container.wait()
    container.remove(force=True)
    logger.info(f'Container {container.name} removed')
    while find_by_name(container_name):
        time.sleep(1)
    return True


def santize_name(name: str) -> str:
    """Sanitize a container name by replacing invalid characters.

    Args:
        name (str): The original name to sanitize.

    Returns:
        str: Sanitized name with invalid characters replaced by hyphens.
    """
    valid_chars = 'abcdefghijklmnopqrstuvwxyz123456789-'
    sanitized = ''.join(c if c in valid_chars else '-' for c in name.lower())
    return sanitized.strip('-')  # Remove leading/trailing hyphens


__all__ = ['get_client', 'find_by_name', 'cleanup', 'remove_if_exists', 'santize_name']
