"""Container utilities module.

This module provides utility functions for Docker container management
including container lookup and cleanup operations.
"""

import time
from typing import cast
from docker.models.containers import Container
from docker import DockerClient

import logging

logger = logging.getLogger(__name__)


def find_by_name(client: DockerClient, container_name: str) -> Container | None:
    """Find a container by its name.

    Args:
        client: Docker client instance.
        container_name (str): Name of the container to find.
    """
    c = [c for c in client.containers.list(all=True) if c.name == container_name]
    if len(c) > 0 and c[0]:
        container = cast(Container, c[0])
        # container already exists, ask for removal
        logger.info(f'Container {container.name} found exists.')
        if container.status != 'running':
            logger.info(
                f'Container {container.name} is not running, status: {container.status}. Starting it...'
            )
            container.start()
            time.sleep(10)  # Wait for the container to start
        return c[0]
    return None


def remove_if_exists(client: DockerClient, container_name: str) -> bool:
    """Remove the container if it exists.

    Args:
        client: Docker client instance.
        container_name (str): Name of the container to remove.

    Returns:
        bool: True if the container was removed, False if it did not exist.
    """
    container = find_by_name(client, container_name)
    if not container:
        logger.info(f'Container {container_name} not existing.')
        return False
    container.stop()
    container.wait()
    container.remove(force=True)
    logger.info(f'Container {container.name} removed')
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
