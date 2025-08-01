# CVE Search API Reference

## Overview

The CVE Search module provides tools for querying and retrieving vulnerability information from the National Vulnerability Database (NVD). It enables agents to search for Common Vulnerabilities and Exposures (CVE) records by ID and retrieve detailed vulnerability information including descriptions, publication dates, and severity scores.

## Core Functionality

The module is built on top of the `nvdlib` library, which provides Python access to the NVD's REST API. All CVE searches are performed against the official NIST National Vulnerability Database.

### Key Features

- **CVE ID Lookup**: Search for specific CVE records by identifier
- **Structured Results**: Returns formatted vulnerability information
- **NVD Integration**: Direct access to official vulnerability database
- **Agent Integration**: Tool functions compatible with IVEXES agents

## Functions

### _search_cve_by_id()

Internal function that performs the actual CVE lookup.

```python
def _search_cve_by_id(cve_id: str) -> str
```

**Parameters:**
- `cve_id` (str): CVE identifier to search for (e.g., "CVE-2021-34527")

**Returns:**
- `str`: Formatted CVE information or error message

**Internal Implementation:**
```python
results = nvdlib.searchCVE(cveId=cve_id)
if len(results) > 0:
    cve = results[0]
    return formatted_cve_info
else:
    return f'No CVE found with ID {cve_id}.'
```

This function is not directly exposed but is used internally by the tool functions.

## Tool Functions

### search_cve_by_id()

Agent tool for searching CVE information by CVE identifier.

```python
@function_tool
def search_cve_by_id(cve_id: str) -> str
```

**Parameters:**
- `cve_id` (str): The CVE ID to search for (e.g., "CVE-2021-34527")

**Returns:**
- `str`: Formatted CVE information including:
  - CVE ID
  - Description
  - Publication date
  - Additional metadata

**Output Format:**
```xml
<cve>
ID: CVE-YYYY-NNNNN
<Description> Detailed vulnerability description </Description>
<Published> YYYY-MM-DDTHH:MM:SS.sssZ </Published>
</cve>
```

**Example Usage:**
```python
from ivexes.cve_search.tools import search_cve_by_id

# Search for a specific CVE
result = search_cve_by_id("CVE-2021-44228")
print(result)
# Output:
# <cve>
# ID: CVE-2021-44228
# <Description> Apache Log4j2 <=2.14.1 JNDI features used in configuration... </Description>
# <Published> 2021-12-10T10:15:09.393Z </Published>
# </cve>

# Search for non-existent CVE
result = search_cve_by_id("CVE-9999-99999")
print(result)
# Output: No CVE found with ID CVE-9999-99999.
```

## Tool Integration

### cve_tools

Pre-configured list of CVE tools for agent integration.

```python
from ivexes.cve_search import cve_tools

# Available in the tools list
print(cve_tools)  # [search_cve_by_id]
```

### Agent Integration

CVE tools are automatically available to agents through the import system:

```python
from ivexes.agents import SingleAgent
from ivexes.cve_search.tools import cve_tools
from ivexes.config import PartialSettings

# Create agent with CVE search capabilities
settings = PartialSettings(
    model='openai/gpt-4o-mini',
    max_turns=20
)

agent = SingleAgent(
    bin_path='/usr/bin/target',
    settings=settings
)

# CVE tools are automatically included in agent tool set
# Agent can now call search_cve_by_id() during analysis
```

## Usage Examples

### Basic CVE Lookup

```python
"""Basic CVE information retrieval."""

from ivexes.cve_search.tools import search_cve_by_id

def lookup_vulnerability(cve_id: str) -> dict:
    """Look up vulnerability information for a CVE ID."""
    
    result = search_cve_by_id(cve_id)
    
    if "No CVE found" in result:
        return {
            'found': False,
            'cve_id': cve_id,
            'error': f'CVE {cve_id} not found in NVD database'
        }
    
    # Parse the structured result
    return {
        'found': True,
        'cve_id': cve_id,
        'raw_data': result
    }

# Example usage
vulnerability = lookup_vulnerability("CVE-2021-44228")
if vulnerability['found']:
    print(f"Found Log4j vulnerability: {vulnerability['raw_data']}")
else:
    print(f"Error: {vulnerability['error']}")
```

### Batch CVE Analysis

```python
"""Analyze multiple CVEs for a security assessment."""

from ivexes.cve_search.tools import search_cve_by_id
from typing import List, Dict, Any

def analyze_cve_list(cve_ids: List[str]) -> Dict[str, Any]:
    """Analyze a list of CVE IDs and return summary information."""
    
    results = {
        'total_searched': len(cve_ids),
        'found': 0,
        'not_found': 0,
        'vulnerabilities': [],
        'missing': []
    }
    
    for cve_id in cve_ids:
        try:
            cve_info = search_cve_by_id(cve_id)
            
            if "No CVE found" in cve_info:
                results['not_found'] += 1
                results['missing'].append(cve_id)
            else:
                results['found'] += 1
                results['vulnerabilities'].append({
                    'cve_id': cve_id,
                    'info': cve_info
                })
                
        except Exception as e:
            results['missing'].append(f"{cve_id} (Error: {e})")
            results['not_found'] += 1
    
    return results

# Example: Analyze known vulnerabilities
known_cves = [
    "CVE-2021-44228",  # Log4j
    "CVE-2021-34527",  # PrintNightmare
    "CVE-2020-1472",   # Zerologon
    "CVE-9999-99999"   # Invalid CVE for testing
]

analysis = analyze_cve_list(known_cves)
print(f"Analysis Results:")
print(f"- Total searched: {analysis['total_searched']}")
print(f"- Found: {analysis['found']}")
print(f"- Not found: {analysis['not_found']}")

for vuln in analysis['vulnerabilities']:
    print(f"\nVulnerability: {vuln['cve_id']}")
    print(vuln['info'])
```

### Agent Integration Example

```python
"""Example of CVE search integration in agent workflow."""

import asyncio
from ivexes.agents import SingleAgent
from ivexes.config import PartialSettings

async def vulnerability_analysis_with_cve():
    """Perform vulnerability analysis with CVE lookup capability."""
    
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=25,
        codebase_path='/path/to/vulnerable/codebase',
        vulnerable_folder='vulnerable-version',
        patched_folder='patched-version'
    )
    
    agent = SingleAgent(
        bin_path='/usr/bin/vulnerable_service',
        settings=settings
    )
    
    # The agent now has access to search_cve_by_id tool
    # During analysis, it can search for relevant CVEs
    
    print("Starting vulnerability analysis with CVE lookup capability...")
    
    # Agent can use the CVE search tool during its analysis
    # For example, if it identifies a vulnerability pattern,
    # it can search for related CVEs to provide context
    
    async for chunk in agent.run_streamed():
        print(chunk, end='', flush=True)

# Run the analysis
if __name__ == "__main__":
    asyncio.run(vulnerability_analysis_with_cve())
```

### Custom CVE Analysis Tool

```python
"""Custom tool that extends CVE search functionality."""

from ivexes.cve_search.tools import search_cve_by_id
from typing import Optional, Dict, Any
import re
from datetime import datetime

class CVEAnalyzer:
    """Enhanced CVE analysis with additional processing capabilities."""
    
    def __init__(self):
        self.cache = {}  # Simple caching for repeated lookups
    
    def search_with_cache(self, cve_id: str) -> str:
        """Search CVE with caching to avoid repeated API calls."""
        if cve_id in self.cache:
            return self.cache[cve_id]
        
        result = search_cve_by_id(cve_id)
        self.cache[cve_id] = result
        return result
    
    def parse_cve_info(self, cve_data: str) -> Optional[Dict[str, Any]]:
        """Parse the XML-like CVE response into structured data."""
        if "No CVE found" in cve_data:
            return None
        
        # Parse the structured CVE response
        patterns = {
            'id': r'ID: (CVE-\d{4}-\d+)',
            'description': r'<Description>\s*(.*?)\s*</Description>',
            'published': r'<Published>\s*(.*?)\s*</Published>'
        }
        
        parsed = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, cve_data, re.DOTALL)
            if match:
                parsed[key] = match.group(1).strip()
        
        return parsed
    
    def analyze_severity_keywords(self, description: str) -> Dict[str, Any]:
        """Analyze description for severity indicators."""
        high_severity_keywords = [
            'remote code execution', 'buffer overflow', 'privilege escalation',
            'authentication bypass', 'sql injection', 'cross-site scripting'
        ]
        
        medium_severity_keywords = [
            'denial of service', 'information disclosure', 'memory leak'
        ]
        
        description_lower = description.lower()
        
        severity_indicators = {
            'high_risk_keywords': [kw for kw in high_severity_keywords if kw in description_lower],
            'medium_risk_keywords': [kw for kw in medium_severity_keywords if kw in description_lower],
            'estimated_severity': 'unknown'
        }
        
        if severity_indicators['high_risk_keywords']:
            severity_indicators['estimated_severity'] = 'high'
        elif severity_indicators['medium_risk_keywords']:
            severity_indicators['estimated_severity'] = 'medium'
        else:
            severity_indicators['estimated_severity'] = 'low'
        
        return severity_indicators
    
    def comprehensive_analysis(self, cve_id: str) -> Dict[str, Any]:
        """Perform comprehensive CVE analysis."""
        # Get CVE data
        raw_data = self.search_with_cache(cve_id)
        parsed_data = self.parse_cve_info(raw_data)
        
        if not parsed_data:
            return {
                'cve_id': cve_id,
                'found': False,
                'error': 'CVE not found'
            }
        
        # Analyze severity
        severity_analysis = self.analyze_severity_keywords(parsed_data['description'])
        
        # Determine age
        try:
            pub_date = datetime.fromisoformat(parsed_data['published'].replace('Z', '+00:00'))
            age_days = (datetime.now(pub_date.tzinfo) - pub_date).days
        except:
            age_days = None
        
        return {
            'cve_id': cve_id,
            'found': True,
            'parsed_data': parsed_data,
            'severity_analysis': severity_analysis,
            'age_days': age_days,
            'raw_data': raw_data
        }

# Usage example
analyzer = CVEAnalyzer()

# Comprehensive analysis
analysis = analyzer.comprehensive_analysis("CVE-2021-44228")
if analysis['found']:
    print(f"CVE: {analysis['cve_id']}")
    print(f"Description: {analysis['parsed_data']['description']}")
    print(f"Estimated Severity: {analysis['severity_analysis']['estimated_severity']}")
    print(f"High-risk keywords found: {analysis['severity_analysis']['high_risk_keywords']}")
    print(f"Age: {analysis['age_days']} days")
```

### Integration with Vector Database

```python
"""Integrate CVE search with vector database for enhanced analysis."""

from ivexes.cve_search.tools import search_cve_by_id
from ivexes.vector_db import VectorDB
from ivexes.config import PartialSettings

async def cve_enhanced_search(query: str, cve_ids: List[str]) -> Dict[str, Any]:
    """Enhanced CVE search using vector database for context."""
    
    settings = PartialSettings(
        embedding_provider='local',
        embedding_model='intfloat/multilingual-e5-large-instruct'
    )
    
    # Initialize vector database
    vector_db = VectorDB(settings)
    
    results = {
        'query': query,
        'cve_details': [],
        'related_patterns': [],
        'recommendations': []
    }
    
    # Get CVE information
    for cve_id in cve_ids:
        cve_info = search_cve_by_id(cve_id)
        if "No CVE found" not in cve_info:
            results['cve_details'].append({
                'cve_id': cve_id,
                'info': cve_info
            })
    
    # Use vector database to find related attack patterns
    if results['cve_details']:
        # Extract descriptions for vector search
        descriptions = []
        for cve in results['cve_details']:
            # Parse description from CVE info
            import re
            desc_match = re.search(r'<Description>\s*(.*?)\s*</Description>', cve['info'], re.DOTALL)
            if desc_match:
                descriptions.append(desc_match.group(1))
        
        # Query vector database for related patterns
        combined_query = f"{query} " + " ".join(descriptions)
        vector_results = await vector_db.query(combined_query, n_results=5)
        
        if vector_results:
            results['related_patterns'] = vector_results
    
    return results

# Example usage
cve_search_results = asyncio.run(cve_enhanced_search(
    query="buffer overflow vulnerability",
    cve_ids=["CVE-2021-44228", "CVE-2020-1472"]
))
```

## Error Handling

### Common Errors

1. **Network Issues**: NVD API unavailable or timeout
2. **Invalid CVE Format**: Malformed CVE identifiers
3. **Rate Limiting**: Too many API requests
4. **Missing Dependencies**: nvdlib not installed

### Error Handling Example

```python
"""Robust CVE search with comprehensive error handling."""

from ivexes.cve_search.tools import search_cve_by_id
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

def robust_cve_search(cve_id: str, max_retries: int = 3) -> Optional[str]:
    """Search CVE with retry logic and error handling."""
    
    # Validate CVE format
    import re
    if not re.match(r'^CVE-\d{4}-\d+$', cve_id):
        logger.error(f"Invalid CVE format: {cve_id}")
        return f"Error: Invalid CVE format '{cve_id}'. Expected format: CVE-YYYY-NNNNN"
    
    for attempt in range(max_retries):
        try:
            result = search_cve_by_id(cve_id)
            logger.info(f"Successfully retrieved CVE {cve_id}")
            return result
        
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {cve_id}: {e}")
            
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} attempts failed for {cve_id}")
                return f"Error: Unable to retrieve CVE {cve_id} after {max_retries} attempts. Last error: {e}"
    
    return None

# Usage with error handling
cve_result = robust_cve_search("CVE-2021-44228")
if cve_result and not cve_result.startswith("Error:"):
    print("CVE information retrieved successfully")
    print(cve_result)
else:
    print(f"Failed to retrieve CVE: {cve_result}")
```

## API Limitations

### NVD API Constraints

- **Rate Limiting**: The NVD API has rate limits for requests
- **Data Freshness**: CVE data may have delays in updates
- **Network Dependency**: Requires internet connection to NVD
- **API Changes**: NVD API changes may affect functionality

### Best Practices

1. **Cache Results**: Implement caching for repeated CVE lookups
2. **Batch Processing**: Group CVE searches when possible
3. **Error Handling**: Always handle network and API errors
4. **Validation**: Validate CVE ID format before searching
5. **Rate Limiting**: Implement client-side rate limiting for bulk operations

## Configuration

### NVD API Settings

The CVE search functionality uses the `nvdlib` library which connects to the NVD REST API. No additional configuration is required, but network access to NIST servers is necessary.

### Optional Enhancements

For production use, consider:
- API key registration with NVD for higher rate limits
- Local CVE database caching
- Proxy configuration for corporate networks
- Custom timeout and retry settings

## See Also

- [Vector Database API](vector_db.md) - Knowledge base integration for enhanced analysis
- [Agents API](agents.md) - Agent integration and tool usage
- [Examples Guide](../documentation/examples.md) - Practical usage examples
- [Development Guide](../documentation/development.md) - Extending CVE search functionality