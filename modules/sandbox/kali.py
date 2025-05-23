import os
import time

import docker
from docker.errors import ContainerError, ImageNotFound
from docker.models.containers import Container

import config.log
from container.utils import find_existing, remove_if_exists

logger = config.log.get(__name__)


def setup_container(executable_archive: str, port: str = '2222', renew: bool = True) -> Container | None:
    """

    """
    assert executable_archive.endswith('.tar') or executable_archive.endswith('.tgz'), "Executable archive must be a .tar or .tgz file"
    client = docker.from_env()
    container_name = f"kali-{os.path.basename(executable_archive).rsplit('.', 1)[0]}"

    c = remove_if_exists(client, container_name) if renew else find_existing(client, container_name)
    if c:
        logger.info(f"Returning: container {c.name}.")
        return c

    try:
        logger.info(f"Starting container {container_name} with {executable_archive=}")
        container: Container = client.containers.run(
            image="kali-ssh:latest",
            name=container_name,
            detach=True,
            ports={
                '22': ('127.0.0.1', port)
            },
            remove=True
        )
        time.sleep(10)  # Wait for the container to start
        logger.info(f"Container {container.name} started")
        data = open(executable_archive, 'rb').read()
        container.put_archive("/root", data)
        return container
    except ContainerError as e:
        logger.error(f"Container error: {e}")
    except ImageNotFound as e:
        logger.error(f"Image not found: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return None
