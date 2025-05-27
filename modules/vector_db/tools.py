from agents import function_tool
import config.log
from modules.vector_db.embed import CweCapecDatabase

logger = config.log.get(__name__)

db = CweCapecDatabase()


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
    logger.info(f"Running semantic_search_cwe({query=}, {n=})")
    return "\n".join(db.query_cwe(query, n))


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
    logger.info(f"Running semantic_search_capec({query=}, {n=})")
    return "\n".join(db.query_capec(query, n))


cwe_capec_tools = [semantic_search_capec, semantic_search_cwe]
