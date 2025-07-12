"""CVE search tools for vulnerability research and analysis."""

from typing import cast
import nvdlib

from agents import Tool, function_tool


def _search_cve_by_id(cve_id: str) -> str:
    results = nvdlib.searchCVE(cveId=cve_id)
    ret = ''
    for cve in results:
        cve_text = '<cve>\n'
        cve_text += f'ID: {cve.id}\n'
        cve_text += f'Description: {cve.descriptions[0].value}\n'
        cve_text += f'Published: {cve.published}\n'
        cve_text += '</cve>'

        ret += cve_text + '\n'
    return ret if ret else 'No CVE found with that ID.'


@function_tool
def search_cve_by_id(cve_id: str) -> str:
    """Search for CVE information by CVE ID using the NVD database.

    Args:
        cve_id: The CVE ID to search for, e.g., "CVE-2021-34527".
    """
    return _search_cve_by_id(cve_id)


cve_tools = cast(list[Tool], [search_cve_by_id])
