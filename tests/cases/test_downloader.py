"""Test cases for the vector_db downloader module.

This module contains unit tests for the CWE and CAPEC data downloader
functionality, including mocking external HTTP requests and XML parsing.
"""

import unittest
from unittest.mock import patch, Mock
import xml.etree.ElementTree as ElementTree
import io
import zipfile

# Mock the logger before importing the module
from ivexes.vector_db.downloader import (
    download_capec,
    download_cwe,
    get_capec_tree,
    get_cwe_tree,
    CAPEC_URL,
    CWE_URL,
)


class TestDownloader(unittest.TestCase):
    """Test cases for the vector_db downloader module."""

    @patch('ivexes.vector_db.downloader.urllib.request.urlopen')
    def test_download_capec(self, mock_urlopen):
        """Test downloading CAPEC XML data."""
        # Mock the response from urlopen
        mock_response = Mock()
        mock_response.read.return_value = b'<capec:Attack_Patterns xmlns:capec="http://capec.mitre.org/capec-3"></capec:Attack_Patterns>'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Call the function
        result = download_capec()

        # Verify the function called urlopen with the correct URL
        mock_urlopen.assert_called_once_with(CAPEC_URL)

        # Verify the result is the decoded XML content
        self.assertEqual(
            result,
            '<capec:Attack_Patterns xmlns:capec="http://capec.mitre.org/capec-3"></capec:Attack_Patterns>',
        )

    @patch('ivexes.vector_db.downloader.urllib.request.urlopen')
    def test_download_cwe(self, mock_urlopen):
        """Test downloading and extracting CWE XML data from a zip file."""
        # Create a mock zip file with XML content
        xml_content = (
            b'<Weakness_Catalog xmlns="http://cwe.mitre.org/cwe-7"></Weakness_Catalog>'
        )
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr('cwec_latest.xml', xml_content)
        zip_buffer.seek(0)

        # Mock the response from urlopen
        mock_response = Mock()
        mock_response.read.return_value = zip_buffer.getvalue()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Call the function
        result = download_cwe()

        # Verify the function called urlopen with the correct URL
        mock_urlopen.assert_called_once_with(CWE_URL)

        # Verify the result is the decoded XML content from the zip file
        self.assertEqual(
            result,
            '<Weakness_Catalog xmlns="http://cwe.mitre.org/cwe-7"></Weakness_Catalog>',
        )

    @patch('ivexes.vector_db.downloader.download_capec')
    def test_get_capec_tree(self, mock_download_capec):
        """Test getting the CAPEC ElementTree."""
        # Mock the download_capec function to return XML content
        mock_download_capec.return_value = '<capec:Attack_Patterns xmlns:capec="http://capec.mitre.org/capec-3"></capec:Attack_Patterns>'

        # Call the function
        result = get_capec_tree()

        # Verify the function called download_capec
        mock_download_capec.assert_called_once()

        # Verify the result is an ElementTree element
        self.assertIsInstance(result, ElementTree.Element)

    @patch('ivexes.vector_db.downloader.download_cwe')
    def test_get_cwe_tree(self, mock_download_cwe):
        """Test getting the CWE ElementTree."""
        # Mock the download_cwe function to return XML content
        mock_download_cwe.return_value = (
            '<Weakness_Catalog xmlns="http://cwe.mitre.org/cwe-7"></Weakness_Catalog>'
        )

        # Call the function
        result = get_cwe_tree()

        # Verify the function called download_cwe
        mock_download_cwe.assert_called_once()

        # Verify the result is an ElementTree element
        self.assertIsInstance(result, ElementTree.Element)

    @patch('ivexes.vector_db.downloader.urllib.request.urlopen')
    def test_download_capec_error(self, mock_urlopen):
        """Test error handling when downloading CAPEC data fails."""
        # Mock urlopen to raise an exception
        mock_urlopen.side_effect = Exception('Connection error')

        # Verify that the function raises the exception
        with self.assertRaises(Exception):
            download_capec()

    @patch('ivexes.vector_db.downloader.urllib.request.urlopen')
    def test_download_cwe_error(self, mock_urlopen):
        """Test error handling when downloading CWE data fails."""
        # Mock urlopen to raise an exception
        mock_urlopen.side_effect = Exception('Connection error')

        # Verify that the function raises the exception
        with self.assertRaises(Exception):
            download_cwe()
