import logging

def setup_default_logging(ivexes_level: str = 'INFO'):
    """
    Setup default logging configuration.
    
    - Third-party libraries: WARNING
    - All ivexes submodules: User-specified level (default INFO)
    
    Args:
        ivexes_level: Log level for all ivexes modules
    """
    # Root logger catches everything at WARNING+
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True
    )
    
    # Set ivexes package and ALL submodules to user level
    logging.getLogger('ivexes').setLevel(ivexes_level)
    
    # Explicitly silence noisy third-party libraries
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)
