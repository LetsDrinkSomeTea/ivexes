import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

import ivexes.config.log as log
from ivexes.config.settings import settings
from ivexes.modules.vector_db.downloader import get_cwe_tree, get_capec_tree
from ivexes.modules.vector_db.parser import insert_capec, insert_cwe

logger = log.get(__name__)


class CweCapecDatabase:
    def __init__(self) -> None:
        self.chroma_client = chromadb.PersistentClient(settings=chromadb.config.Settings(allow_reset=True))
        ef =   DefaultEmbeddingFunction()
        if settings.embedding_provider == "openai":
            from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction
            ef = OpenAIEmbeddingFunction(
                model_name=settings.embedding_model,
                api_key=settings.openai_api_key,
            ) 
        logger.info(f"using {settings.embedding_provider=}")
        self.collection = self.chroma_client.get_or_create_collection(name="collection-local", embedding_function=ef)

        logger.info(f"currently {self.collection.count()} entries loaded")
        if self.collection.count() == 0:
            logger.info("Initializing database...")
            self.initialize()

    def initialize(self) -> None:
        """Download and load CWE and CAPEC datasets into the Chroma collection with error handling."""
        try:
            logger.info("Downloading and parsing CWE data...")
            cwe_root = get_cwe_tree()
            insert_cwe(self.collection, cwe_root)
            logger.info("Successfully downloaded and inserted CWE data.")
        except Exception as exc:
            logger.error("Failed to download or insert CWE data: %s", exc)

        try:
            logger.info("Downloading and parsing CAPEC data...")
            capec_root = get_capec_tree()
            insert_capec(self.collection, capec_root)
            logger.info("Successfully downloaded and inserted CAPEC data.")
        except Exception as exc:
            logger.error("Failed to download or insert CAPEC data: %s", exc)

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
        return [f'{m.get("type", "").upper()}-{m.get("id", "")} {d}' for (m, d) in zip(metadata, documents)]

    def query_cwe(self, query_text: str, n: int = 3) -> list[str]:
        return self.query(query_text, ["cwe"], n)

    def query_capec(self, query_text: str, n: int = 3) -> list[str]:
        return self.query(query_text, ["capec"], n)
