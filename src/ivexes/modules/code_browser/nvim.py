import time

import docker
from docker.errors import ContainerError, ImageNotFound
from docker.models.containers import Container

import ivexes.config.log as log
from ivexes.config.settings import get_settings
from ivexes.container.utils import find_existing, remove_if_exists

logger = log.get(__name__)


def setup_container(
    code_base: str, port: str = '8080', renew: bool = False
) -> Container:
    """
    Set up a Docker container with the codebase mounted for Neovim LSP analysis.

    Args:
        code_base: Path to the codebase directory to be mounted
        port: Port number to expose from the container (default: '8080')
        renew: Whether to remove existing container and create a new one (default: False)

    Returns:
        The Docker container object if successful, None otherwise
    """
    client = docker.from_env()
    container_name = f'ivexes-nvim-lsp-{get_settings().trace_name}'

    c = (
        remove_if_exists(client, container_name)
        if renew
        else find_existing(client, container_name)
    )
    if c:
        logger.info(f'Returning: container {c.name}.')
        return c

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
            # remove=True
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
