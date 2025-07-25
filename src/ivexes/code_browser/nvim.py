"""Neovim container setup and management module.

This module provides functionality to set up and manage Docker containers
running Neovim with LSP capabilities for code analysis. It handles container
lifecycle management including creation, configuration, and cleanup.
"""

import time

from docker.errors import ContainerError, ImageNotFound
from docker.models.containers import Container

import logging
from ..config.settings import Settings
from ..container import (
    cleanup,
    find_by_name,
    remove_if_exists,
    santize_name,
    get_client,
)

logger = logging.getLogger(__name__)

NVIM_LSP_CONTAINER_PREFIX = 'ivexes-nvim-lsp-'


def setup_container(
    code_base: str, settings: Settings, port: int = 8080, renew: bool = False
) -> Container:
    """Set up a Docker container with the codebase mounted for Neovim LSP analysis.

    Args:
        code_base: Path to the codebase directory to be mounted
        settings: Configuration settings for the container
        port: Port number to expose from the container (default: '8080')
        renew: Whether to remove existing container and create a new one (default: False)

    Returns:
        The Docker container object if successful, None otherwise
    """
    client = get_client()
    container_name = santize_name(f'{NVIM_LSP_CONTAINER_PREFIX}{settings.trace_name}')

    if renew:
        remove_if_exists(container_name)
    else:
        c = find_by_name(container_name)
        if c:
            logger.info(f'Returning: container {c.name}.')
            return c
    cleanup(NVIM_LSP_CONTAINER_PREFIX)

    try:
        logger.info(f'Starting container {container_name} with {code_base=}')
        container: Container = client.containers.run(
            image='nvim-lsp:latest',
            name=container_name,
            detach=True,
            volumes={code_base: {'bind': '/codebase', 'mode': 'ro'}},
            ports={
                '8080': ('127.0.0.1', port)  # Bind to a random port
            },
            remove=True,
        )
        time.sleep(30)  # Wait for the container to start
        logger.info(f'Container {container.name} started')
        return container
    except ContainerError as e:
        logger.error(f'Container error: {e}')
        exit(1)
    except ImageNotFound as e:
        logger.error(f'Image not found: {e}')
        exit(1)
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        exit(1)
