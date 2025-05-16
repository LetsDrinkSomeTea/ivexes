import logging
import datetime
from config.settings import settings

now = datetime.datetime.now()
#logging.basicConfig(level=logging.ERROR)

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
    logger.setLevel(settings.log_level)
    logger.handlers.clear()
#    logger.propagate = False

    # Define a unified formatter
    log_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)

    # File handler for logging to a file
    # log_file = f"logs/log-{now.strftime('%H-%M-%S')}.log"
    # file_handler = logging.FileHandler(log_file)
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    # StreamHandler for logging to the CLI
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
