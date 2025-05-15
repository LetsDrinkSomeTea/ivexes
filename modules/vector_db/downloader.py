import urllib.request
import zipfile
import io
import xml.etree.ElementTree as ElementTree
import config.log

logger = config.log.get(__name__)

CAPEC_URL = "https://capec.mitre.org/data/xml/capec_latest.xml"
CWE_URL = "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip"

def download_capec():
    """
    Download the CAPEC XML file and return it as a string.

    Returns:
        str: The CAPEC XML content
    """
    logger.info(f"Downloading CAPEC XML from {CAPEC_URL}")
    try:
        with urllib.request.urlopen(CAPEC_URL) as response:
            xml_content = response.read().decode('utf-8')
            logger.info("Successfully downloaded CAPEC XML")
            return xml_content
    except Exception as e:
        logger.error(f"Failed to download CAPEC XML: {e}")
        raise

def download_cwe():
    """
    Download and extract the CWE XML file from the zip archive and return it as a string.

    Returns:
        str: The CWE XML content
    """
    logger.info(f"Downloading CWE XML from {CWE_URL}")
    try:
        # Download the zip file
        with urllib.request.urlopen(CWE_URL) as response:
            zip_content = response.read()

        # Extract the XML file from the zip archive
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
            # Get the first XML file in the archive
            xml_files = [name for name in zip_file.namelist() if name.endswith('.xml')]
            if not xml_files:
                raise ValueError("No XML file found in the zip archive")

            xml_content = zip_file.read(xml_files[0]).decode('utf-8')
            logger.info(f"Successfully extracted CWE XML from {xml_files[0]}")
            return xml_content
    except Exception as e:
        logger.error(f"Failed to download or extract CWE XML: {e}")
        raise

def get_capec_tree():
    """
    Download the CAPEC XML and return it as an ElementTree.

    Returns:
        ElementTree.ElementTree: The parsed CAPEC XML
    """
    xml_content = download_capec()
    return ElementTree.fromstring(xml_content)

def get_cwe_tree():
    """
    Download and extract the CWE XML and return it as an ElementTree.

    Returns:
        ElementTree.ElementTree: The parsed CWE XML
    """
    xml_content = download_cwe()
    return ElementTree.fromstring(xml_content)
