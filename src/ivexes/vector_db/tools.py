"""Vector Database Tools for Cybersecurity Knowledge Bases.

This module provides tool functions for querying cybersecurity knowledge bases
including CWE (Common Weakness Enumeration), CAPEC (Common Attack Pattern
Enumeration and Classification), and MITRE ATT&CK framework data.

All tools perform semantic search using vector embeddings to find relevant
cybersecurity information based on natural language queries.
"""

from typing import Optional
from agents import function_tool, Tool
import logging

from ivexes.config import Settings, create_settings
from .vector_db import CweCapecAttackDatabase, QueryTypes

logger = logging.getLogger(__name__)


def create_vectordb_tools(
    db: Optional[CweCapecAttackDatabase] = None, settings: Optional[Settings] = None
) -> list[Tool]:
    """Create vector database tools with injected database instance.

    Args:
        db: CweCapecAttackDatabase instance, if not provided, a new instance will be created using the settings.
        settings: Settings instance for creating a new database instance, if needed. Gets ignored if `db` is provided and created from environment variables if not present.

    Returns:
        List of tools for vector database operations
    """
    if not settings:
        settings = create_settings()
    if not db:
        db = CweCapecAttackDatabase(settings)

    @function_tool
    def semantic_search_cwe(query: str, n: int = 5):
        """Semantically searches Common Weakness Enumeration (CWE) descriptions in a vector database.

        Args:
            query (str): The query to search for.
            n (int, optional): The count of items to return. Defaults to 5.

        Returns:
            str: The n best matches formatted as a string.
        """
        logger.info(f'Running semantic_search_cwe({query=}, {n=})')
        return '\n'.join(db.query_cwe(query, n))

    @function_tool
    def semantic_search_capec(query: str, n: int = 5):
        """Semantically searches Common Attack Pattern Enumerations and Classifications (CAPEC) descriptions in a vector database.

        Args:
            query (str): The query to search for.
            n (int, optional): The count of items to return. Defaults to 5.

        Returns:
            str: The n best matches formatted as a string.
        """
        logger.info(f'Running semantic_search_capec({query=}, {n=})')
        return '\n'.join(db.query_capec(query, n))

    @function_tool
    def semantic_search_attack_techniques(query: str, n: int = 5):
        """Semantically searches MITRE ATT&CK techniques in a vector database.

        Args:
            query (str): The query to search for.
            n (int, optional): The count of items to return. Defaults to 5.

        Returns:
            str: The n best matches formatted as a string.
        """
        logger.info(f'Running semantic_search_attack_techniques({query=}, {n=})')
        return '\n'.join(db.query_attack_techniques(query, n))

    @function_tool
    def semantic_search_attack_tactics(query: str, n: int = 5):
        """Semantically searches MITRE ATT&CK tactics (kill chain phases) in a vector database.

        Args:
            query (str): The query to search for.
            n (int, optional): The count of items to return. Defaults to 5.

        Returns:
            str: The n best matches formatted as a string.
        """
        logger.info(f'Running semantic_search_attack_tactics({query=}, {n=})')
        return '\n'.join(db.query_attack_tactics(query, n))

    @function_tool
    def semantic_search_attack_mitigations(query: str, n: int = 5):
        """Semantically searches MITRE ATT&CK mitigations in a vector database.

        Args:
            query (str): The query to search for.
            n (int, optional): The count of items to return. Defaults to 5.

        Returns:
            str: The n best matches formatted as a string.
        """
        logger.info(f'Running semantic_search_attack_mitigations({query=}, {n=})')
        return '\n'.join(db.query_attack_mitigations(query, n))

    @function_tool
    def semantic_search_attack_groups(query: str, n: int = 5):
        """Semantically searches MITRE ATT&CK threat groups in a vector database.

        Args:
            query (str): The query to search for.
            n (int, optional): The count of items to return. Defaults to 5.

        Returns:
            str: The n best matches formatted as a string.
        """
        logger.info(f'Running semantic_search_attack_groups({query=}, {n=})')
        return '\n'.join(db.query_attack_groups(query, n))

    @function_tool
    def semantic_search_attack_software(query: str, n: int = 5):
        """Semantically searches MITRE ATT&CK software (malware and tools) in a vector database.

        Args:
            query (str): The query to search for.
            n (int, optional): The count of items to return. Defaults to 5.

        Returns:
            str: The n best matches formatted as a string.
        """
        logger.info(f'Running semantic_search_attack_software({query=}, {n=})')
        return '\n'.join(db.query_attack_software(query, n))

    @function_tool
    def semantic_search_attack_all(query: str, n: int = 5):
        """Semantically searches all MITRE ATT&CK data (techniques, tactics, mitigations, groups, software) in a vector database.

        Args:
            query (str): The query to search for.
            n (int, optional): The count of items to return. Defaults to 5.

        Returns:
            str: The n best matches formatted as a string.
        """
        logger.info(f'Running semantic_search_attack_all({query=}, {n=})')
        return '\n'.join(db.query_attack_all(query, n))

    @function_tool
    def semantic_search(query: str, type: list[QueryTypes], n: int = 5):
        """Semantic search knowledge base for cybersecurity information.

        Args:
            query (str): The query to search for.
            type (list[QueryTypes]): The types to filter the search by.
            n (int, optional): The count of items to return. Defaults to 5.

        Returns:
            str: The n best matches formatted as a list of strings.
        """
        logger.info(f'Running semantic_search({query=}, {type=}, {n=})')
        return '\n'.join(db.query(query, types=type if type else None, n=n))

    return [
        semantic_search_cwe,
        semantic_search_capec,
        semantic_search_attack_techniques,
        semantic_search_attack_tactics,
        semantic_search_attack_mitigations,
        semantic_search_attack_groups,
        semantic_search_attack_software,
        semantic_search_attack_all,
        semantic_search,
    ]
