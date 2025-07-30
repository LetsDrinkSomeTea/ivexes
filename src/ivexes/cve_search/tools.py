"""CVE search tools for vulnerability research and analysis."""

from typing import cast
import nvdlib

from agents import Tool, function_tool

INDEX_FOR_ENGLISH = 0


def _search_cve_by_id(cve_id: str) -> str:
    results = nvdlib.searchCVE(cveId=cve_id)
    if len(results) > 0:  # Can only return one or none CVE,
        cve = results[0]  # when querying by ID
        return f"""
<cve>
ID: {cve.id}
<Description> {cve.descriptions[INDEX_FOR_ENGLISH].value} </Description>
<Published> {cve.published} </Published>
</cve>
"""
    else:
        return f'No CVE found with ID {cve_id}.'


@function_tool
def search_cve_by_id(cve_id: str) -> str:
    """Search for CVE information by CVE ID using the NVD database.

    Args:
        cve_id: The CVE ID to search for, e.g., "CVE-2021-34527".
    """
    return _search_cve_by_id(cve_id)


cve_tools = cast(list[Tool], [search_cve_by_id])
