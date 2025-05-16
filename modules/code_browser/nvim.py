import time

import docker
from docker.errors import ContainerError, ImageNotFound
from docker.models.containers import Container
import os
import config.log
logger = config.log.get(__name__)

def setup_container(code_base: os.path, port: str = '8080', renew: bool = False) -> Container | None:
    """
    Set up a Docker container with the codebase mounted.
    """
    client = docker.from_env()
    c = [c for c in client.containers.list() if c.name == f"nvim-lsp-{os.path.basename(code_base)}"]
    if len(c) > 0 and c[0]:
        # container already exists, ask for removal
        logger.info(f"Container {c[0].name} already exists.")
        if renew :
            c[0].stop()
            c[0].remove(force=True)
            logger.info(f"Container {c[0].name} removed")
        else:
            logger.info(f"Returning existing container {c[0].name}")
            return c[0]


    try:
        container: Container = client.containers.run(
            image="nvim-lsp:latest",
            name=f"nvim-lsp-{os.path.basename(code_base)}",
            detach=True,
            volumes={
                code_base: {
                    'bind': '/codebase',
                    'mode': 'ro'
                }
            },
            ports={
                port: '8080'  # Bind to a random port
            },
            remove=True
        )
        time.sleep(30)  # Wait for the container to start
        logger.info(f"Container {container.name} with {code_base=} started")
        return container
    except ContainerError as e:
        logger.error(f"Container error: {e}")
    except ImageNotFound as e:
        logger.error(f"Image not found: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return None
