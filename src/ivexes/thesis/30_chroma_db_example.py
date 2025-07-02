from typing import cast
from chromadb import EmbeddingFunction, Client, Embeddings, Documents
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import SentenceTransformer

chroma_client = Client()


class SentenceTransformerEmbeddingFunctionSelf(EmbeddingFunction):
    def __init__(self, model_name) -> None:
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input).tolist()


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
