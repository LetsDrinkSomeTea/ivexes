import time

import docker
from docker.errors import ContainerError, ImageNotFound
from docker.models.containers import Container

import ivexes.config.log as log
from ivexes.config.settings import settings
from ivexes.container.utils import find_existing, remove_if_exists

logger = log.get(__name__)


def setup_container(setup_archive: str, port: int = 2222, renew: bool = True) -> Container | None:
    """

    """
    assert setup_archive.endswith('.tar') or setup_archive.endswith('.tgz'), "Executable archive must be a .tar or .tgz file"
    assert isinstance(port, int), f"port must be number, got {type(port)}"
    client = docker.from_env()
    container_name = f"kali-{settings.trace_name}"

    c = remove_if_exists(client, container_name) if renew else find_existing(client, container_name)
    if c:
        logger.info(f"Returning: container {c.name}.")
        return c

    try:
        logger.info(f"Starting container {container_name} with {setup_archive=}")
        container: Container = client.containers.run(
            image="kali-ssh:latest",
            name=container_name,
            detach=True,
            ports={
                '22': ('127.0.0.1', port)
            },
            #remove=True
        )
        time.sleep(10)  # Wait for the container to start
        logger.info(f"Container {container.name} started")
        data = open(setup_archive, 'rb').read()
        container.put_archive("/tmp", data)
        logger.info(f"Setup archive {setup_archive} uploaded to container {container.name}")
        container.exec_run("chmod +x /tmp/setup.sh")
        ret = container.exec_run("bash /tmp/setup.sh")
        logger.debug(f"Setup script output: {ret.output.decode()}")
        return container
    except ContainerError as e:
        logger.error(f"Container error: {e}")
    except ImageNotFound as e:
        logger.error(f"Image not found: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return None
