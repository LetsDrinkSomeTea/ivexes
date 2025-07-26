"""Test cases for the vector_db embedding module.

This module contains unit tests for the CWE/CAPEC database embedding
functionality, including ChromaDB integration and query operations.
"""

import unittest
from unittest.mock import patch, MagicMock

from ivexes.vector_db import CweCapecAttackDatabase


class TestCweCapecDatabase(unittest.TestCase):
    """Test cases for the CweCapecDatabase class in the vector_db embed module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_settings = MagicMock()
        self.mock_settings.embedding_provider = 'builtin'
        self.mock_settings.embedding_model = 'builtin'
        self.mock_settings.chroma_path = '/tmp/chroma'
        self.mock_settings.openai_api_key = 'test-api-key'

    @patch('ivexes.vector_db.vector_db.chromadb.PersistentClient')
    @patch('ivexes.vector_db.vector_db.DefaultEmbeddingFunction')
    def test_init_with_default_embedding(self, mock_default_ef, mock_client):
        """Test initialization with default embedding function."""
        # Mock the ChromaDB client and collection
        mock_chroma_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10  # Simulate existing entries
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_chroma_client

        # Mock the default embedding function
        mock_default_instance = MagicMock()
        mock_default_ef.return_value = mock_default_instance

        # Initialize the database
        db = CweCapecAttackDatabase(settings=self.mock_settings)
        db.initialize()

        # Verify the default embedding function was used
        mock_default_ef.assert_called_once()

        # Verify the client was created
        mock_client.assert_called_once()

    @patch('ivexes.vector_db.vector_db.chromadb.PersistentClient')
    @patch('ivexes.vector_db.vector_db.DefaultEmbeddingFunction')
    def test_init_with_openai_embedding(self, mock_default_ef, mock_client):
        """Test initialization with OpenAI embedding function."""
        # Set up for OpenAI embedding
        self.mock_settings.embedding_provider = 'openai'
        self.mock_settings.embedding_model = 'text-embedding-ada-002'

        # Mock the ChromaDB client and collection
        mock_chroma_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_chroma_client

        # Mock the OpenAI embedding function
        with patch(
            'chromadb.utils.embedding_functions.openai_embedding_function.OpenAIEmbeddingFunction'
        ) as mock_openai_ef:
            mock_openai_instance = MagicMock()
            mock_openai_ef.return_value = mock_openai_instance

            # Initialize the database
            db = CweCapecAttackDatabase(settings=self.mock_settings)
            db.initialize()

            # Verify the OpenAI embedding function was created
            mock_openai_ef.assert_called_once_with(
                model_name='text-embedding-ada-002', api_key='test-api-key'
            )

    @patch('ivexes.vector_db.vector_db.chromadb.PersistentClient')
    @patch('ivexes.vector_db.vector_db.DefaultEmbeddingFunction')
    def test_query(self, mock_default_ef, mock_client):
        """Test the query method."""
        # Mock the ChromaDB client and collection
        mock_chroma_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10

        # Mock the query results
        mock_query_results = {
            'metadatas': [[{'type': 'cwe', 'id': '1', 'name': 'Test CWE'}]],
            'documents': [['Test CWE description']],
        }
        mock_collection.query.return_value = mock_query_results

        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_chroma_client

        # Initialize the database
        db = CweCapecAttackDatabase(settings=self.mock_settings)

        # Call the query method
        results = db.query('test query', ['cwe'], 5)

        # Verify the collection's query method was called with the correct arguments
        mock_collection.query.assert_called_once_with(
            query_texts='test query', n_results=5, where={'type': {'$in': ['cwe']}}
        )

    @patch('ivexes.vector_db.vector_db.chromadb.PersistentClient')
    @patch('ivexes.vector_db.vector_db.DefaultEmbeddingFunction')
    def test_query_cwe(self, mock_default_ef, mock_client):
        """Test the query_cwe method."""
        # Mock the ChromaDB client and collection
        mock_chroma_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_chroma_client

        # Initialize the database
        db = CweCapecAttackDatabase(settings=self.mock_settings)

        # Mock the query method
        db.query = MagicMock(return_value=['CWE-1 Test CWE description'])

        # Call the query_cwe method
        results = db.query_cwe('test query', 5)

        # Verify the query method was called with the correct arguments
        db.query.assert_called_once_with('test query', ['cwe'], 5)

        # Verify the results are correct
        self.assertEqual(results, ['CWE-1 Test CWE description'])

    @patch('ivexes.vector_db.vector_db.chromadb.PersistentClient')
    @patch('ivexes.vector_db.vector_db.DefaultEmbeddingFunction')
    def test_query_capec(self, mock_default_ef, mock_client):
        """Test the query_capec method."""
        # Mock the ChromaDB client and collection
        mock_chroma_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_chroma_client

        # Initialize the database
        db = CweCapecAttackDatabase(settings=self.mock_settings)

        # Mock the query method
        db.query = MagicMock(return_value=['CAPEC-1 Test CAPEC description'])

        # Call the query_capec method
        results = db.query_capec('test query', 5)

        # Verify the query method was called with the correct arguments
        db.query.assert_called_once_with('test query', ['capec'], 5)

        # Verify the results are correct
        self.assertEqual(results, ['CAPEC-1 Test CAPEC description'])


if __name__ == '__main__':
    unittest.main()
