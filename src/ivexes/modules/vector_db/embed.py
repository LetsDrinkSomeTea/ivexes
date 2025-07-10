from typing import cast
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from chromadb.config import Settings

import ivexes.config.log as log
from ivexes.config.settings import get_settings
from ivexes.modules.vector_db.downloader import get_cwe_tree, get_capec_tree
from ivexes.modules.vector_db.parser import insert_capec, insert_cwe
from ivexes.modules.vector_db.attack_parser import insert_attack_all

from os import path

logger = log.get(__name__)


class CweCapecAttackDatabase:
    def __init__(self) -> None:
        ef = DefaultEmbeddingFunction()
        settings = get_settings()
        if settings.embedding_provider == 'openai':
            from chromadb.utils.embedding_functions.openai_embedding_function import (
                OpenAIEmbeddingFunction,
            )

            ef = OpenAIEmbeddingFunction(
                model_name=settings.embedding_model, api_key=settings.openai_api_key
            )
        if settings.embedding_provider == 'local':
            from chromadb.utils.embedding_functions.sentence_transformer_embedding_function import (
                SentenceTransformerEmbeddingFunction,
            )

            ef = SentenceTransformerEmbeddingFunction(
                model_name=settings.embedding_model
            )
        db_path = path.join(settings.chroma_path, settings.embedding_model)
        logger.info(f'Using database path: {db_path}')

        self.chroma_client = chromadb.PersistentClient(
            settings=Settings(allow_reset=True), path=db_path
        )
        logger.info(f'using {settings.embedding_provider=} and ef={type(ef)}')
        self.collection = self.chroma_client.get_or_create_collection(
            name='collection-local',
            embedding_function=cast(chromadb.EmbeddingFunction, ef),
        )

        logger.info(f'currently {self.collection.count()} entries loaded')
        if self.collection.count() == 0:
            logger.info('Initializing database...')
            self.initialize()

    def initialize(self) -> None:
        """Download and load CWE, CAPEC, and ATT&CK datasets into the Chroma collection with error handling."""
        self.initialize_attack()
        self.initialize_cwe()
        self.initialize_capec()

    def initialize_cwe(self) -> None:
        try:
            logger.info('Downloading and parsing CWE data...')
            cwe_root = get_cwe_tree()
            insert_cwe(self.collection, cwe_root)
            logger.info('Successfully downloaded and inserted CWE data.')
        except Exception as exc:
            logger.error('Failed to download or insert CWE data: %s', exc)

    def initialize_capec(self) -> None:
        try:
            logger.info('Downloading and parsing CAPEC data...')
            capec_root = get_capec_tree()
            insert_capec(self.collection, capec_root)
            logger.info('Successfully downloaded and inserted CAPEC data.')
        except Exception as exc:
            logger.error('Failed to download or insert CAPEC data: %s', exc)

    def initialize_attack(self) -> None:
        try:
            logger.info('Downloading and parsing ATT&CK data...')
            insert_attack_all(self.collection, domain='enterprise')
            logger.info('Successfully downloaded and inserted ATT&CK data.')
        except Exception as exc:
            logger.error('Failed to download or insert ATT&CK data: %s', exc)

    def clear(self) -> None:
        self.chroma_client.reset()
        logger.info('DB cleared')

    def query(
        self, query_text: str, types: list[str] | None = None, n: int = 3
    ) -> list[str]:
        """Query the collection, optionally filtering by type."""
        if types is None:
            types = [
                'cwe',
                'capec',
                'attack-technique',
                'attack-mitigation',
                'attack-group',
                'attack-malware',
                'attack-tool',
                'attack-tactic',
            ]

        logger.info('Querying the collection for types: %s', types)
        results = self.collection.query(
            query_texts=query_text, n_results=n, where={'type': {'$in': types}}
        )
        logger.debug(results)
        metadata = results.get('metadatas', [[]])[0]
        documents = results.get('documents', [[]])[0]
        return [
            f'{m.get("type", "").upper()}-{m.get("id", "")} {d}'
            for (m, d) in zip(metadata, documents)
        ]

    def query_cwe(self, query_text: str, n: int = 3) -> list[str]:
        return self.query(query_text, ['cwe'], n)

    def query_capec(self, query_text: str, n: int = 3) -> list[str]:
        return self.query(query_text, ['capec'], n)

    def query_attack_techniques(self, query_text: str, n: int = 3) -> list[str]:
        """Query for ATT&CK techniques."""
        return self.query(query_text, ['attack-technique'], n)

    def query_attack_tactics(self, query_text: str, n: int = 3) -> list[str]:
        """Query for ATT&CK tactics."""
        return self.query(query_text, ['attack-tactic'], n)

    def query_attack_mitigations(self, query_text: str, n: int = 3) -> list[str]:
        """Query for ATT&CK mitigations."""
        return self.query(query_text, ['attack-mitigation'], n)

    def query_attack_groups(self, query_text: str, n: int = 3) -> list[str]:
        """Query for ATT&CK groups."""
        return self.query(query_text, ['attack-group'], n)

    def query_attack_software(self, query_text: str, n: int = 3) -> list[str]:
        """Query for ATT&CK software (malware and tools)."""
        return self.query(query_text, ['attack-malware', 'attack-tool'], n)

    def query_attack_all(self, query_text: str, n: int = 3) -> list[str]:
        """Query for all ATT&CK data types."""
        return self.query(
            query_text,
            [
                'attack-technique',
                'attack-mitigation',
                'attack-group',
                'attack-malware',
                'attack-tool',
                'attack-tactic',
            ],
            n,
        )
