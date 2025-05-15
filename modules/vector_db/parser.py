import xml.etree.ElementTree as ET
import chromadb

import click

import log
logger = log.get(__name__)

def insert_cwe(collection: chromadb.Collection, xml_file: str):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    cwe_ns = {'ns': 'http://cwe.mitre.org/cwe-7'}

    weaknesses = root.find('ns:Weaknesses', cwe_ns)
    with click.progressbar(weaknesses.findall('ns:Weakness', cwe_ns), label="Embedding CWEs: ", show_percent=True) as items:
        for weakness in items:
            wid = weakness.get('ID')
            name = weakness.get('Name')
            # Main description
            desc_node = weakness.find('ns:Description', cwe_ns)
            desc_text = desc_node.text.strip() if desc_node is not None and desc_node.text is not None else ""
            # Extended description
            ext_node = weakness.find('ns:Extended_Description', cwe_ns)
            ext_text = ext_node.text.strip() if ext_node is not None and ext_node.text is not None else "N/A"
            # Compose document
            doc = f"{name}:\nDescription: {desc_text}\nExtended: {ext_text}"
            meta = {
                "id": wid,
                "name": name,
                "type": "cwe"
            }
            logger.debug(f"Adding CWE-{wid:<4}: {name[:50]:<50}: {desc_text[:50]}...")
            collection.add(
                ids=[wid],
                documents=[doc],
                metadatas=[meta]
            )
        logger.info(f"Inserted {len(collection.get()['ids'])} CWE entries into Chroma.")
    return collection


def insert_capec(collection: chromadb.Collection, xml_file: str):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    capec_ns = {'ns': 'http://capec.mitre.org/capec-3'}

    attack_patterns = root.find('ns:Attack_Patterns', capec_ns)
    with click.progressbar(attack_patterns.findall('ns:Attack_Pattern', capec_ns), label="Embedding CAPECs: ",
                           show_percent=True) as items:
        for ap in items:
            aid = ap.get('ID')
            name = ap.get('Name')
            # Main description
            desc_node = ap.find('ns:Description', capec_ns)
            desc_text = desc_node.text.strip() if desc_node is not None and desc_node.text is not None else ""
            # Prerequisites (multiple entries)
            prereq_node = ap.find('ns:Prerequisites', capec_ns)
            prereqs = []
            if prereq_node is not None:
                for p in prereq_node.findall('ns:Prerequisite', capec_ns):
                    if p.text:
                        prereqs.append(p.text.strip())
            prereq_text = " | ".join(prereqs) if len(prereqs) > 0 else "N/A"
            # Compose document
            doc = f"{name}:\nDescription: {desc_text}\nPrerequisites: {prereq_text}"
            meta = {
                "id": aid,
                "name": name,
                "type": "capec"
            }
            logger.debug(f"Adding CAPEC-{aid:<4}: {name[:50]:<50}: {desc_text[:50]}...")
            collection.add(
                ids=[aid],
                documents=[doc],
                metadatas=[meta]
            )
        logger.info(f"Inserted {len(collection.get()['ids'])} CAPEC entries into Chroma.")
    return collection
