"""Sandbox container management module.

This module provides functionality to set up and manage Docker containers
for sandboxed environments, including container lifecycle management
and configuration.
"""

import time
from typing import Optional

import docker
from docker.errors import ContainerError, ImageNotFound
from docker.models.containers import Container

import logging
from ..config.settings import Settings
from ..container import find_by_name, get_client, remove_if_exists, santize_name

logger = logging.getLogger(__name__)


def setup_container(
    settings: Settings,
    docker_image: Optional[str] = None,
    renew: bool = True,
) -> Container:
    """Set up a Docker container for sandbox execution.

    Args:
        settings: Settings instance containing configuration parameters
        port: Port number to map for container access
        docker_image: Docker image to use (defaults to settings.sandbox_image)
        renew: Whether to remove existing container with same name

    Returns:
        Container: Docker container object ready for use

    Raises:
        AssertionError: If setup_archive is not .tar/.tgz or port is not int
        docker.errors.APIError: If Docker operations fail
    """

    def run_setup_script(container: Container, setup_archive: Optional[str]):
        if not setup_archive:
            return
        if not (setup_archive.endswith('.tar') or setup_archive.endswith('.tgz')):
            raise ValueError('Executable archive must be a .tar or .tgz file')
        with open(setup_archive, 'rb') as f:
            data = f.read()
        container.put_archive('/tmp', data)
        logger.info(
            f'Setup archive {setup_archive} uploaded to container {container.name}'
        )
        container.exec_run('chmod a+x /tmp/setup.sh')
        ret = container.exec_run('sudo -u user bash /tmp/setup.sh')
        logger.debug(f'Setup script output: {ret.output.decode()}')

    def create_user(container: Container, username: str):
        """Create a user in the container if it doesn't exist.

        Args:
            container: Docker container object
            username: Username to create
        """
        try:
            # Check if user already exists
            result = container.exec_run(f'id -u {username}', user='root')
            if result.exit_code == 0:
                logger.debug(
                    f'User {username} already exists in container {container.name}'
                )
                return

            # Create user with home directory and no password
            result = container.exec_run(
                ['useradd', '-m', '-p', 'passwd', '-s', '/bin/sh', username],
                user='root',
            )
            if result.exit_code != 0:
                logger.error(
                    f'Failed to create user {username}: {result.output.decode()}'
                )
            logger.info(f'Created user {username} in container {container.name}')
        except Exception as e:
            logger.error(f'Failed to create user {username}: {e}')

    client = get_client()
    # settings parameter is provided
    if docker_image is None:
        docker_image = settings.sandbox_image
    container_name = santize_name(
        f'ivexes-{docker_image.split(":")[0]}-{settings.trace_name}'
    )

    try:
        if renew:
            remove_if_exists(container_name)
        else:
            c = find_by_name(container_name)
            if c:
                logger.info(f'Returning: container {c.name}.')
                return c

        logger.info(
            f'Starting container {container_name} with {settings.setup_archive=}'
        )
        container: Container = client.containers.run(
            image=docker_image,
            name=container_name,
            detach=True,
            environment={
                'TERM': 'xterm-mono',
            },
            remove=True,
        )
        MAX_DELAY = 30
        time_waited = 0
        while container.status != 'running':
            time.sleep(1)  # Wait for the container to start
            time_waited += 1
            restarted = False
            try:
                container.reload()
            except docker.errors.NotFound:
                logger.info(
                    f'Container {container_name} exited immediately, trying to restart with CMD sleep infinity'
                )
                if not restarted:
                    container: Container = client.containers.run(
                        image=docker_image,
                        name=container_name,
                        detach=True,
                        environment={
                            'TERM': 'xterm-mono',
                        },
                        # remove=True,
                        command=['sleep', 'infinity'],
                    )
                    time_waited = 0
                    restarted = True

            if time_waited > MAX_DELAY:
                raise TimeoutError(
                    f'Container {container_name} did not start within {MAX_DELAY} seconds'
                )
        create_user(container, 'user')
        run_setup_script(container, settings.setup_archive)
        logger.info(f'Container {container.name} started')
        return container
    except ContainerError as e:
        logger.error(f'Container error: {e}')
        raise RuntimeError(f'Container setup failed: {e}') from e
    except ImageNotFound as e:
        logger.error(f'Image not found: {e}')
        raise RuntimeError(f'Docker image not found: {e}') from e
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        raise RuntimeError(f'Container setup failed: {e}') from e
