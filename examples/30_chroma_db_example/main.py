"""ChromaDB vector database example."""

from typing import cast
from chromadb import EmbeddingFunction, Client
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

chroma_client = Client()

ef = SentenceTransformerEmbeddingFunction(
    model_name='intfloat/multilingual-e5-large-instruct'
)

ef = cast(EmbeddingFunction, ef)
collection = chroma_client.create_collection(
    name='example_collection', embedding_function=ef
)

collection.add(
    ids=['id1', 'id2'],
    documents=['This is an example about airplanes', 'This is an example about trees'],
)
result = collection.query(query_texts='forest')

print(result)
