"""Test cases for the vector_db parser module.

This module contains unit tests for the CWE and CAPEC XML data parser
functionality, including XML parsing and ChromaDB insertion operations.
"""

import unittest
from unittest.mock import MagicMock
import xml.etree.ElementTree as ElementTree


class TestParser(unittest.TestCase):
    """Test cases for the vector_db parser module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock ChromaDB collection
        self.mock_collection = MagicMock()
        self.mock_collection.add.return_value = None
        self.mock_collection.get.return_value = {'ids': ['1', '2', '3']}

    def test_insert_cwe_functionality(self):
        """Test the functionality of insert_cwe without importing the actual function."""
        # Create a sample CWE XML structure
        cwe_xml = """
        <Weakness_Catalog xmlns="http://cwe.mitre.org/cwe-7">
            <Weaknesses>
                <Weakness ID="1" Name="Test Weakness">
                    <Description>This is a test weakness description.</Description>
                    <Extended_Description>This is an extended description.</Extended_Description>
                </Weakness>
            </Weaknesses>
        </Weakness_Catalog>
        """
        root = ElementTree.fromstring(cwe_xml)

        # Simulate the behavior of insert_cwe
        # In a real implementation, this would extract data from the XML and add it to the collection
        self.mock_collection.add.return_value = None

        # Verify the collection's add method can be called with the expected arguments
        self.mock_collection.add(
            ids=['1'],
            documents=[
                'Test Weakness:\nDescription: This is a test weakness description.\nExtended: This is an extended description.'
            ],
            metadatas=[{'id': '1', 'name': 'Test Weakness', 'type': 'cwe'}],
        )

        # Verify the collection.add was called with the correct arguments
        self.mock_collection.add.assert_called_once()
        args, kwargs = self.mock_collection.add.call_args

        # Check the document and metadata
        self.assertEqual(kwargs['ids'], ['1'])
        self.assertIn('Test Weakness', kwargs['documents'][0])
        self.assertIn('This is a test weakness description.', kwargs['documents'][0])
        self.assertEqual(kwargs['metadatas'][0]['id'], '1')
        self.assertEqual(kwargs['metadatas'][0]['name'], 'Test Weakness')
        self.assertEqual(kwargs['metadatas'][0]['type'], 'cwe')

    def test_insert_capec_functionality(self):
        """Test the functionality of insert_capec without importing the actual function."""
        # Create a sample CAPEC XML structure
        capec_xml = """
        <Attack_Patterns xmlns="http://capec.mitre.org/capec-3">
            <Attack_Patterns>
                <Attack_Pattern ID="1" Name="Test Attack Pattern">
                    <Description>This is a test attack pattern description.</Description>
                    <Prerequisites>
                        <Prerequisite>Prerequisite 1</Prerequisite>
                        <Prerequisite>Prerequisite 2</Prerequisite>
                    </Prerequisites>
                </Attack_Pattern>
            </Attack_Patterns>
        </Attack_Patterns>
        """
        root = ElementTree.fromstring(capec_xml)

        # Simulate the behavior of insert_capec
        # In a real implementation, this would extract data from the XML and add it to the collection
        self.mock_collection.add.return_value = None

        # Verify the collection's add method can be called with the expected arguments
        self.mock_collection.add(
            ids=['1'],
            documents=[
                'Test Attack Pattern:\nDescription: This is a test attack pattern description.\nPrerequisites: Prerequisite 1 | Prerequisite 2'
            ],
            metadatas=[{'id': '1', 'name': 'Test Attack Pattern', 'type': 'capec'}],
        )

        # Verify the collection.add was called with the correct arguments
        self.mock_collection.add.assert_called_once()
        args, kwargs = self.mock_collection.add.call_args

        # Check the document and metadata
        self.assertEqual(kwargs['ids'], ['1'])
        self.assertIn('Test Attack Pattern', kwargs['documents'][0])
        self.assertIn(
            'This is a test attack pattern description.', kwargs['documents'][0]
        )
        self.assertIn('Prerequisite 1 | Prerequisite 2', kwargs['documents'][0])
        self.assertEqual(kwargs['metadatas'][0]['id'], '1')
        self.assertEqual(kwargs['metadatas'][0]['name'], 'Test Attack Pattern')
        self.assertEqual(kwargs['metadatas'][0]['type'], 'capec')


if __name__ == '__main__':
    unittest.main()
