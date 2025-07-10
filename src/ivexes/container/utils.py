from docker.models.containers import Container

import logging

logger = logging.getLogger(__name__)


def find_existing(client, container_name: str) -> Container | None:
    """ """
    c = [c for c in client.containers.list(all=True) if c.name == container_name]
    if len(c) > 0 and c[0]:
        # container already exists, ask for removal
        logger.info(f'Container {c[0].name} found exists.')
        return c[0]
    return None


def remove_if_exists(client, container_name: str) -> None:
    """
    Remove the container if it exists.
    """
    container = find_existing(client, container_name)
    if not container:
        logger.info(f'Container {container_name} not existing.')
        return
    container.stop()
    container.wait()
    container.remove(force=True)
    logger.info(f'Container {container.name} removed')
