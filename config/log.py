import logging
import datetime

now = datetime.datetime.now()

def setup_logger(name):
    """
Set up and return a logger with the given name and level.
Uses Rich for prettier console output with unified formatting.
Args:
name (str): Logger name.
Returns:
logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)

    # Define a unified formatter
    log_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)

    # File handler for logging to a file
    log_file = f"logs/log-{now.strftime('%H-%M-%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # StreamHandler for logging to the CLI
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger