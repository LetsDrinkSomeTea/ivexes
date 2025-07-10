import logging

from ivexes.config.settings import get_settings


def get(name: str) -> logging.Logger:
    """
    Set up and return a logger with the given name and level.

    Uses a unified formatter for consistent log output formatting.

    Args:
        name: Logger name to identify the source of log messages

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(get_settings().log_level)
    logger.handlers.clear()

    log_format = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, date_format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
