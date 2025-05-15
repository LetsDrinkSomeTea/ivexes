import docker
import docker.errors
import docker.models

import os
import config.log
logger = config.log.get(__name__)

def setup_container(code_base: os.path) -> str | None:
    """
    Set up a Docker container with the specified image and name.
    """
    client = docker.from_env()
    c = [c for c in client.containers.list() if c.name == f"nvim-lsp-{os.path.basename(code_base)}"]
    if len(c) > 0 and c[0]:
        logger.info(f"Removing already existing {c[0].name} container")
        c[0].remove(force=True)

    try:
        container = client.containers.run(
            image="nvim-lsp:latest",
            name=f"nvim-lsp-{os.path.basename(code_base)}",
            detach=True,
            volumes={
                code_base: {
                    'bind': '/codebase',
                    'mode': 'rw'
                }
            }
        )
        logger.info(f"Container {container.name} with {code_base=} started")
        return container.id
    except docker.errors.ContainerError as e:
        logger.error(f"Container error: {e}")
    except docker.errors.ImageNotFound as e:
        logger.error(f"Image not found: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return None
