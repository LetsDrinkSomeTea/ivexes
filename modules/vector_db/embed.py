from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from dotenv import load_dotenv

load_dotenv(verbose=True)

from parser import insert_capec, insert_cwe

import chromadb
from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction
from chromadb.config import Settings

import log

logger = log.get(__name__)

class CweCapecDatabase:
    def __init__(self, openai_embedding: bool = False) -> None:
        self.chroma_client = chromadb.PersistentClient(settings=Settings(allow_reset=True))
        ef = OpenAIEmbeddingFunction(model_name="text-embedding-3-large") if openai_embedding else DefaultEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(name="collection-local", embedding_function=ef)

        logger.info(f"currently {self.collection.count()} entries loaded")
        if self.collection.count() == 0:
            logger.info("Initializing database...")
            self.initialize()


    def initialize(self) -> None:
        """Load CWE and CAPEC datasets into the Chroma collection with error handling."""
        try:
            insert_cwe(self.collection, './cwe.xml')
            logger.info("Successfully inserted CWE data from './cwe.xml'.")
        except FileNotFoundError as fnf:
            logger.error("CWE file not found: %s", fnf)
        except Exception as exc:
            logger.error("Failed to insert CWE data: %s", exc)

        try:
            insert_capec(self.collection, './capec.xml')
            logger.info("Successfully inserted CAPEC data from './capec.xml'.")
        except FileNotFoundError as fnf:
            logger.error("CAPEC file not found: %s", fnf)
        except Exception as exc:
            logger.error("Failed to insert CAPEC data: %s", exc)

    def clear(self) -> None:
        self.chroma_client.reset()
        logger.info("DB cleared")

    def query(self, query_text: str, types: list[str] | None = None, n: int = 3) -> list[str]:
        """Query the collection, optionally filtering by type."""
        if types is None:
            types = ["cwe", "capec"]

        logger.info("Querying the collection for types: %s", types)
        results = self.collection.query(
            query_texts=query_text,
            n_results=n,
            where={"type": {"$in": types}}
        )
        logger.debug(results)
        metadata = results.get("metadatas", [[]])[0]
        documents = results.get("documents", [[]])[0]
        return [f"{m.get("type", "").upper()}-{m.get("id", "")} {d}" for (m,d) in zip(metadata, documents)]

    
    def query_cwe(self, query_text: str, n: int = 3) -> list[str]:
        return self.query(query_text, ["cwe"], n)

    def query_capec(self, query_text: str, n: int = 3) -> list[str]:
        return self.query(query_text, ["capec"], n)
