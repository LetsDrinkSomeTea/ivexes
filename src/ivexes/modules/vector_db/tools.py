from agents import function_tool
import ivexes.config.log as log
from ivexes.modules.vector_db.embed import CweCapecAttackDatabase

logger = log.get(__name__)

db = CweCapecAttackDatabase()


@function_tool
def semantic_search_cwe(query: str, n: int = 5):
    """
    Semantically searches Common Weakness Enumeration (CWE) descriptions in a vector database

    Args:
       query: The query to search for
       n: The count of items to return (default 5)

    Returns:
       The n best matches
    """
    logger.info(f'Running semantic_search_cwe({query=}, {n=})')
    return '\n'.join(db.query_cwe(query, n))


@function_tool
def semantic_search_capec(query: str, n: int = 5):
    """
    Semantically searches Common Attack Pattern Enumerations and Classifications (CAPEC) descriptions in a vector database

    Args:
       query: The query to search for
       n: The count of items to return (default 5)

    Returns:
       The n best matches
    """
    logger.info(f'Running semantic_search_capec({query=}, {n=})')
    return '\n'.join(db.query_capec(query, n))


@function_tool
def semantic_search_attack_techniques(query: str, n: int = 5):
    """
    Semantically searches MITRE ATT&CK techniques in a vector database

    Args:
       query: The query to search for
       n: The count of items to return (default 5)

    Returns:
       The n best matches
    """
    logger.info(f'Running semantic_search_attack_techniques({query=}, {n=})')
    return '\n'.join(db.query_attack_techniques(query, n))


@function_tool
def semantic_search_attack_tactics(query: str, n: int = 5):
    """
    Semantically searches MITRE ATT&CK tactics (kill chain phases) in a vector database

    Args:
       query: The query to search for
       n: The count of items to return (default 5)

    Returns:
       The n best matches
    """
    logger.info(f'Running semantic_search_attack_tactics({query=}, {n=})')
    return '\n'.join(db.query_attack_tactics(query, n))


@function_tool
def semantic_search_attack_mitigations(query: str, n: int = 5):
    """
    Semantically searches MITRE ATT&CK mitigations in a vector database

    Args:
       query: The query to search for
       n: The count of items to return (default 5)

    Returns:
       The n best matches
    """
    logger.info(f'Running semantic_search_attack_mitigations({query=}, {n=})')
    return '\n'.join(db.query_attack_mitigations(query, n))


@function_tool
def semantic_search_attack_groups(query: str, n: int = 5):
    """
    Semantically searches MITRE ATT&CK threat groups in a vector database

    Args:
       query: The query to search for
       n: The count of items to return (default 5)

    Returns:
       The n best matches
    """
    logger.info(f'Running semantic_search_attack_groups({query=}, {n=})')
    return '\n'.join(db.query_attack_groups(query, n))


@function_tool
def semantic_search_attack_software(query: str, n: int = 5):
    """
    Semantically searches MITRE ATT&CK software (malware and tools) in a vector database

    Args:
       query: The query to search for
       n: The count of items to return (default 5)

    Returns:
       The n best matches
    """
    logger.info(f'Running semantic_search_attack_software({query=}, {n=})')
    return '\n'.join(db.query_attack_software(query, n))


@function_tool
def semantic_search_attack_all(query: str, n: int = 5):
    """
    Semantically searches all MITRE ATT&CK data (techniques, tactics, mitigations, groups, software) in a vector database

    Args:
       query: The query to search for
       n: The count of items to return (default 5)

    Returns:
       The n best matches
    """
    logger.info(f'Running semantic_search_attack_all({query=}, {n=})')
    return '\n'.join(db.query_attack_all(query, n))


# Export all tools
vectordb_tools = [
    semantic_search_cwe,
    semantic_search_capec,
    semantic_search_attack_techniques,
    semantic_search_attack_mitigations,
    semantic_search_attack_groups,
    semantic_search_attack_software,
    semantic_search_attack_all,
]
