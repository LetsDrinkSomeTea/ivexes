"""Token counting and text statistics module.

This module provides utilities for counting tokens, characters, and words
in text files and directories, useful for analyzing content size and
processing requirements.
"""

import logging

logger = logging.getLogger(__name__)

__all__ = ['get_text_statistics', 'get_file_statistics', 'get_directory_statistics']


def get_text_statistics(string: str) -> tuple[int, int, int]:
    """Get the number of tokens, characters, and words in a given string.

    Args:
        string: The input string to analyze.

    Returns:
        tuple[int, int, int]: A tuple containing the number of tokens, characters, and words.
    """
    import tiktoken
    from ..config.settings import get_settings

    encoding = tiktoken.encoding_for_model(get_settings().model)
    tokens = encoding.encode(string)
    return len(tokens), len(string), len(string.split())


def get_file_statistics(file_path: str) -> tuple[int, int, int]:
    """get_file_statistics returns the number of tokens, characters, and words in a file.

    Args:
        file_path (str): The path to the file to analyze.

    Returns:
        tuple[int, int, int]: A tuple containing the number of tokens, characters, and words.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return get_text_statistics(content)
    except UnicodeDecodeError:
        pass
    except ValueError:
        pass

    return 0, 0, 0


def get_directory_statistics(directory_path: str) -> tuple[int, int, int]:
    """get_directory_statistics returns the total number of tokens, characters, and words in all files in a directory.

    Args:
        directory_path (str): The path to the directory to analyze.

    Returns:
        tuple[int, int, int]: A tuple containing the total number of tokens, characters, and words.
    """
    import os

    total_tokens = 0
    total_characters = 0
    total_words = 0

    skipped_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                tokens, characters, words = get_file_statistics(file_path)
                if tokens == 0 and characters == 0 and words == 0:
                    skipped_files.append(os.path.basename(file_path))
                    continue
                total_tokens += tokens
                total_characters += characters
                total_words += words

    logger.warning(f'Skipped files {"; ".join(skipped_files)} due to encoding issues.')
    return total_tokens, total_characters, total_words
