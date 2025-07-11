"""Test cases for the vector_db embedding module.

This module contains unit tests for the CWE/CAPEC database embedding
functionality, including ChromaDB integration and query operations.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os

# Add the project root to the Python path to allow importing modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)

from modules.vector_db.embed import CweCapecDatabase


class TestCweCapecDatabase(unittest.TestCase):
    """Test cases for the CweCapecDatabase class in the vector_db embed module."""

    @patch('modules.vector_db.embed.chromadb.PersistentClient')
    @patch('modules.vector_db.embed.OpenAIEmbeddingFunction')
    @patch('modules.vector_db.embed.DefaultEmbeddingFunction')
    def test_init_with_openai_embedding(
        self, mock_default_ef, mock_openai_ef, mock_client
    ):
        """Test initialization with OpenAI embedding function."""
        # Mock settings
        with patch('modules.vector_db.embed.settings') as mock_settings:
            mock_settings.embedding_provider = 'openai'
            mock_settings.embedding_model = 'text-embedding-ada-002'
            mock_settings.openai_api_key = 'test-api-key'

            # Mock the ChromaDB client and collection
            mock_chroma_client = MagicMock()
            mock_collection = MagicMock()
            mock_collection.count.return_value = 10  # Simulate existing entries
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            mock_client.return_value = mock_chroma_client

            # Mock the OpenAI embedding function
            mock_openai_instance = MagicMock()
            mock_openai_ef.return_value = mock_openai_instance

            # Initialize the database
            db = CweCapecDatabase()

            # Verify the client was created with the correct settings
            mock_client.assert_called_once()

            # Verify the OpenAI embedding function was created with the correct settings
            mock_openai_ef.assert_called_once_with(
                model_name=mock_settings.embedding_model,
                api_key=mock_settings.openai_api_key,
            )

            # Verify the collection was created with the OpenAI embedding function
            mock_chroma_client.get_or_create_collection.assert_called_once_with(
                name='collection-local', embedding_function=mock_openai_instance
            )

            # Verify initialize was not called since count > 0
            self.assertEqual(db.collection, mock_collection)

    @patch('modules.vector_db.embed.chromadb.PersistentClient')
    @patch('modules.vector_db.embed.DefaultEmbeddingFunction')
    def test_init_with_default_embedding(self, mock_default_ef, mock_client):
        """Test initialization with default embedding function."""
        # Mock settings
        with patch('modules.vector_db.embed.settings') as mock_settings:
            mock_settings.embedding_provider = 'default'

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
            db = CweCapecDatabase()

            # Verify the default embedding function was used
            mock_default_ef.assert_called_once()

            # Verify the collection was created with the default embedding function
            mock_chroma_client.get_or_create_collection.assert_called_once_with(
                name='collection-local', embedding_function=mock_default_instance
            )

    @patch('modules.vector_db.embed.chromadb.PersistentClient')
    @patch('modules.vector_db.embed.DefaultEmbeddingFunction')
    @patch('modules.vector_db.embed.get_cwe_tree')
    @patch('modules.vector_db.embed.get_capec_tree')
    @patch('modules.vector_db.embed.insert_cwe')
    @patch('modules.vector_db.embed.insert_capec')
    def test_initialize(
        self,
        mock_insert_capec,
        mock_insert_cwe,
        mock_get_capec_tree,
        mock_get_cwe_tree,
        mock_default_ef,
        mock_client,
    ):
        """Test the initialize method."""
        # Mock settings
        with patch('modules.vector_db.embed.settings') as mock_settings:
            mock_settings.embedding_provider = 'default'

            # Mock the ChromaDB client and collection
            mock_chroma_client = MagicMock()
            mock_collection = MagicMock()
            mock_collection.count.return_value = (
                0  # Empty collection to trigger initialize
            )
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            mock_client.return_value = mock_chroma_client

            # Mock the trees
            mock_cwe_tree = MagicMock()
            mock_capec_tree = MagicMock()
            mock_get_cwe_tree.return_value = mock_cwe_tree
            mock_get_capec_tree.return_value = mock_capec_tree

            # Initialize the database
            db = CweCapecDatabase()

            # Verify the trees were fetched
            mock_get_cwe_tree.assert_called_once()
            mock_get_capec_tree.assert_called_once()

            # Verify the insert functions were called with the correct arguments
            mock_insert_cwe.assert_called_once_with(mock_collection, mock_cwe_tree)
            mock_insert_capec.assert_called_once_with(mock_collection, mock_capec_tree)

    @patch('modules.vector_db.embed.chromadb.PersistentClient')
    @patch('modules.vector_db.embed.DefaultEmbeddingFunction')
    def test_clear(self, mock_default_ef, mock_client):
        """Test the clear method."""
        # Mock the ChromaDB client and collection
        mock_chroma_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_chroma_client

        # Initialize the database
        with patch('modules.vector_db.embed.settings') as mock_settings:
            mock_settings.embedding_provider = 'default'
            db = CweCapecDatabase()

        # Call the clear method
        db.clear()

        # Verify the client's reset method was called
        mock_chroma_client.reset.assert_called_once()

    @patch('modules.vector_db.embed.chromadb.PersistentClient')
    @patch('modules.vector_db.embed.DefaultEmbeddingFunction')
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
        with patch('modules.vector_db.embed.settings') as mock_settings:
            mock_settings.embedding_provider = 'default'
            db = CweCapecDatabase()

        # Call the query method
        results = db.query('test query', ['cwe'], 5)

        # Verify the collection's query method was called with the correct arguments
        mock_collection.query.assert_called_once_with(
            query_texts='test query', n_results=5, where={'type': {'$in': ['cwe']}}
        )

        # Verify the results are formatted correctly
        self.assertEqual(results, ['CWE-1 Test CWE description'])

    @patch('modules.vector_db.embed.chromadb.PersistentClient')
    @patch('modules.vector_db.embed.DefaultEmbeddingFunction')
    def test_query_cwe(self, mock_default_ef, mock_client):
        """Test the query_cwe method."""
        # Mock the ChromaDB client and collection
        mock_chroma_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_chroma_client

        # Initialize the database
        with patch('modules.vector_db.embed.settings') as mock_settings:
            mock_settings.embedding_provider = 'default'
            db = CweCapecDatabase()

        # Mock the query method
        db.query = MagicMock(return_value=['CWE-1 Test CWE description'])

        # Call the query_cwe method
        results = db.query_cwe('test query', 5)

        # Verify the query method was called with the correct arguments
        db.query.assert_called_once_with('test query', ['cwe'], 5)

        # Verify the results are correct
        self.assertEqual(results, ['CWE-1 Test CWE description'])

    @patch('modules.vector_db.embed.chromadb.PersistentClient')
    @patch('modules.vector_db.embed.DefaultEmbeddingFunction')
    def test_query_capec(self, mock_default_ef, mock_client):
        """Test the query_capec method."""
        # Mock the ChromaDB client and collection
        mock_chroma_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_chroma_client

        # Initialize the database
        with patch('modules.vector_db.embed.settings') as mock_settings:
            mock_settings.embedding_provider = 'default'
            db = CweCapecDatabase()

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
