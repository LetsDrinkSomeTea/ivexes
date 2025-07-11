"""MITRE ATT&CK framework data parser for vector database.

This module provides functionality to parse MITRE ATT&CK framework data
and insert it into a ChromaDB vector database for similarity search
and retrieval.
"""

import chromadb
import click

import logging
from .attack_downloader import (
    get_attack_data,
    get_all_techniques,
    get_all_tactics,
    get_all_mitigations,
    get_all_groups,
    get_all_software,
)

logger = logging.getLogger(__name__)


def _safe_get(obj, *keys, default=''):
    """Safely get nested attributes/keys from an object."""
    result = obj
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            result = getattr(result, key, default)
        if result is default:
            return default
    return result if result else default


def insert_attack_techniques(collection: chromadb.Collection, attack_data):
    """Insert ATT&CK techniques into the ChromaDB collection.

    Args:
        collection: The ChromaDB collection to insert into
        attack_data: MitreAttackData object
    """
    techniques = get_all_techniques(attack_data)

    with click.progressbar(
        techniques, label='Embedding ATT&CK Techniques: ', show_percent=True
    ) as items:
        for technique in items:
            # Extract technique ID (e.g., T1234)
            external_refs = _safe_get(technique, 'external_references', default=[])
            technique_id = None
            for ref in external_refs:
                if ref.get('source_name') == 'mitre-attack':
                    technique_id = ref.get('external_id')
                    break

            if not technique_id:
                continue

            name = _safe_get(technique, 'name')
            description = _safe_get(technique, 'description')

            # Get kill chain phases (tactics)
            kill_chain_phases = _safe_get(technique, 'kill_chain_phases', default=[])
            tactics = [phase.get('phase_name', '') for phase in kill_chain_phases]
            tactics_text = ', '.join(tactics) if tactics else 'N/A'

            # Compose document
            doc = f"""
<ATT&CK-TECHNIQUE>
{technique_id} {name}:
<Description>: {description} </Description>
<Tactics>: {tactics_text} </Tactics>
</ATT&CK-TECHNIQUE>
"""
            meta = {
                'id': technique_id,
                'name': name,
                'type': 'attack-technique',
                'tactics': tactics_text,
            }

            logger.debug(f'Adding {technique_id}: {name[:50]}...')
            collection.add(
                ids=[f'attack-technique-{technique_id}'],
                documents=[doc],
                metadatas=[meta],
            )

    logger.info(f'Inserted {len(techniques)} ATT&CK techniques into Chroma.')


def insert_attack_tactics(collection: chromadb.Collection, attack_data):
    """Insert ATT&CK tactics into the ChromaDB collection.

    Args:
        collection: The ChromaDB collection to insert into
        attack_data: MitreAttackData object
    """
    tactics = get_all_tactics(attack_data)

    with click.progressbar(
        tactics, label='Embedding ATT&CK Tactics: ', show_percent=True
    ) as items:
        for tactic in items:
            # Extract tactic ID (e.g., TA0001)
            external_refs = _safe_get(tactic, 'external_references', default=[])
            tactic_id = None
            for ref in external_refs:
                if ref.get('source_name') == 'mitre-attack':
                    tactic_id = ref.get('external_id')
                    break

            if not tactic_id:
                continue

            name = _safe_get(tactic, 'name')
            description = _safe_get(tactic, 'description')

            # Get the short name (x_mitre_shortname)
            shortname = _safe_get(tactic, 'x_mitre_shortname', default='')

            # Compose document
            doc = f"""
<ATT&CK-TACTIC>
{tactic_id} {name}:
<Description>: {description} </Description>
<Short_Name>: {shortname} </Short_Name>
</ATT&CK-TACTIC>
"""
            meta = {
                'id': tactic_id,
                'name': name,
                'type': 'attack-tactic',
                'shortname': shortname,
            }

            logger.debug(f'Adding {tactic_id}: {name[:50]}...')
            collection.add(
                ids=[f'attack-tactic-{tactic_id}'], documents=[doc], metadatas=[meta]
            )

    logger.info(f'Inserted {len(tactics)} ATT&CK tactics into Chroma.')


def insert_attack_mitigations(collection: chromadb.Collection, attack_data):
    """Insert ATT&CK mitigations into the ChromaDB collection.

    Args:
        collection: The ChromaDB collection to insert into
        attack_data: MitreAttackData object
    """
    mitigations = get_all_mitigations(attack_data)

    with click.progressbar(
        mitigations, label='Embedding ATT&CK Mitigations: ', show_percent=True
    ) as items:
        for mitigation in items:
            # Extract mitigation ID (e.g., M1234)
            external_refs = _safe_get(mitigation, 'external_references', default=[])
            mitigation_id = None
            for ref in external_refs:
                if ref.get('source_name') == 'mitre-attack':
                    mitigation_id = ref.get('external_id')
                    break

            if not mitigation_id:
                continue

            name = _safe_get(mitigation, 'name')
            description = _safe_get(mitigation, 'description')

            # Compose document
            doc = f"""
<ATT&CK-MITIGATION>
{mitigation_id} {name}:
<Description>: {description} </Description>
</ATT&CK-MITIGATION>
"""
            meta = {'id': mitigation_id, 'name': name, 'type': 'attack-mitigation'}

            logger.debug(f'Adding {mitigation_id}: {name[:50]}...')
            collection.add(
                ids=[f'attack-mitigation-{mitigation_id}'],
                documents=[doc],
                metadatas=[meta],
            )

    logger.info(f'Inserted {len(mitigations)} ATT&CK mitigations into Chroma.')


def insert_attack_groups(collection: chromadb.Collection, attack_data):
    """Insert ATT&CK groups into the ChromaDB collection.

    Args:
        collection: The ChromaDB collection to insert into
        attack_data: MitreAttackData object
    """
    groups = get_all_groups(attack_data)

    with click.progressbar(
        groups, label='Embedding ATT&CK Groups: ', show_percent=True
    ) as items:
        for group in items:
            # Extract group ID (e.g., G1234)
            external_refs = _safe_get(group, 'external_references', default=[])
            group_id = None
            for ref in external_refs:
                if ref.get('source_name') == 'mitre-attack':
                    group_id = ref.get('external_id')
                    break

            if not group_id:
                continue

            name = _safe_get(group, 'name')
            description = _safe_get(group, 'description')
            aliases = _safe_get(group, 'aliases', default=[])
            aliases_text = ', '.join(aliases) if aliases else 'N/A'

            # Compose document
            doc = f"""
<ATT&CK-GROUP>
{group_id} {name}:
<Description>: {description} </Description>
<Aliases>: {aliases_text} </Aliases>
</ATT&CK-GROUP>
"""
            meta = {
                'id': group_id,
                'name': name,
                'type': 'attack-group',
                'aliases': aliases_text,
            }

            logger.debug(f'Adding {group_id}: {name[:50]}...')
            collection.add(
                ids=[f'attack-group-{group_id}'], documents=[doc], metadatas=[meta]
            )

    logger.info(f'Inserted {len(groups)} ATT&CK groups into Chroma.')


def insert_attack_software(collection: chromadb.Collection, attack_data):
    """Insert ATT&CK software (tools and malware) into the ChromaDB collection.

    Args:
        collection: The ChromaDB collection to insert into
        attack_data: MitreAttackData object
    """
    software_items = get_all_software(attack_data)

    with click.progressbar(
        software_items, label='Embedding ATT&CK Software: ', show_percent=True
    ) as items:
        for software in items:
            # Extract software ID (e.g., S1234)
            external_refs = _safe_get(software, 'external_references', default=[])
            software_id = None
            for ref in external_refs:
                if ref.get('source_name') == 'mitre-attack':
                    software_id = ref.get('external_id')
                    break

            if not software_id:
                continue

            name = _safe_get(software, 'name')
            description = _safe_get(software, 'description')
            labels = _safe_get(software, 'labels', default=[])
            software_type = 'malware' if 'malware' in labels else 'tool'

            # Compose document
            doc = f"""
<ATT&CK-SOFTWARE>
{software_id} {name} ({software_type}):
<Description>: {description} </Description>
<Type>: {software_type} </Type>
</ATT&CK-SOFTWARE>
"""
            meta = {
                'id': software_id,
                'name': name,
                'type': f'attack-{software_type}',
                'software_type': software_type,
            }

            logger.debug(f'Adding {software_id}: {name[:50]}...')
            collection.add(
                ids=[f'attack-software-{software_id}'],
                documents=[doc],
                metadatas=[meta],
            )

    logger.info(f'Inserted {len(software_items)} ATT&CK software items into Chroma.')


def insert_attack_all(collection: chromadb.Collection, domain='enterprise'):
    """Insert all ATT&CK data (techniques, mitigations, groups, software) into the collection.

    Args:
        collection: The ChromaDB collection to insert into
        domain: The ATT&CK domain to load ("enterprise", "ics", or "mobile")
    """
    attack_data = get_attack_data(domain)

    insert_attack_techniques(collection, attack_data)
    insert_attack_tactics(collection, attack_data)
    insert_attack_mitigations(collection, attack_data)
    insert_attack_groups(collection, attack_data)
    insert_attack_software(collection, attack_data)
