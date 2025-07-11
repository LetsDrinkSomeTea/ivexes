"""MITRE ATT&CK framework data downloader.

This module provides functionality to download and parse MITRE ATT&CK
framework data from official sources, extracting techniques, tactics,
mitigations, groups, and software information.
"""

from mitreattack.stix20 import MitreAttackData
import requests
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

# ATT&CK STIX data URLs
ENTERPRISE_ATTACK_URL = 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'
ICS_ATTACK_URL = (
    'https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json'
)
MOBILE_ATTACK_URL = 'https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json'


def get_attack_data(domain='enterprise'):
    """Download and return MITRE ATT&CK data for the specified domain.

    Args:
        domain: The ATT&CK domain to download ("enterprise", "ics", or "mobile")

    Returns:
        MitreAttackData: The ATT&CK data object
    """
    url_map = {
        'enterprise': ENTERPRISE_ATTACK_URL,
        'ics': ICS_ATTACK_URL,
        'mobile': MOBILE_ATTACK_URL,
    }

    if domain not in url_map:
        raise ValueError(
            f'Invalid domain: {domain}. Must be one of {list(url_map.keys())}'
        )

    url = url_map[domain]
    logger.info(f'Downloading ATT&CK {domain} data from {url}')

    try:
        # Download the JSON data
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Create a temporary file to store the downloaded data
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as temp_file:
            temp_file.write(response.text)
            file_name = temp_file.name

        # Create MitreAttackData object with the downloaded file
        attack_data = MitreAttackData(file_name)

        # Clean up the temporary file after loading
        try:
            os.unlink(file_name)
        except Exception as e:
            logger.warning(f'Failed to delete temporary file {file_name}: {e}')

        logger.info(f'Successfully downloaded ATT&CK {domain} data')
        return attack_data

    except requests.RequestException as e:
        logger.error(f'Failed to download ATT&CK {domain} data: {e}')
        raise
    except Exception as e:
        logger.error(f'Failed to process ATT&CK {domain} data: {e}')
        # Clean up temporary file if it exists
        if 'file_name' in locals() and os.path.exists(file_name):
            try:
                os.unlink(file_name)
            except Exception:
                pass
        raise


def get_all_techniques(attack_data):
    """Get all techniques from the ATT&CK data.

    Args:
        attack_data: MitreAttackData object

    Returns:
        list: List of technique objects
    """
    techniques = attack_data.get_techniques(remove_revoked_deprecated=True)
    logger.info(f'Retrieved {len(techniques)} techniques')
    return techniques


def get_all_tactics(attack_data):
    """Get all tactics from the ATT&CK data.

    Args:
        attack_data: MitreAttackData object

    Returns:
        list: List of tactic objects
    """
    tactics = attack_data.get_tactics(remove_revoked_deprecated=True)
    logger.info(f'Retrieved {len(tactics)} tactics')
    return tactics


def get_all_mitigations(attack_data):
    """Get all mitigations from the ATT&CK data.

    Args:
        attack_data: MitreAttackData object

    Returns:
        list: List of mitigation objects
    """
    mitigations = attack_data.get_mitigations(remove_revoked_deprecated=True)
    logger.info(f'Retrieved {len(mitigations)} mitigations')
    return mitigations


def get_all_groups(attack_data):
    """Get all groups from the ATT&CK data.

    Args:
        attack_data: MitreAttackData object

    Returns:
        list: List of group objects
    """
    groups = attack_data.get_groups(remove_revoked_deprecated=True)
    logger.info(f'Retrieved {len(groups)} groups')
    return groups


def get_all_software(attack_data):
    """Get all software (tools and malware) from the ATT&CK data.

    Args:
        attack_data: MitreAttackData object

    Returns:
        list: List of software objects
    """
    software = attack_data.get_software(remove_revoked_deprecated=True)
    logger.info(f'Retrieved {len(software)} software items')
    return software
