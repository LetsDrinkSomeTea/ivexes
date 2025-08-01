# Vector Database API Reference

## Overview

The Vector Database module provides comprehensive knowledge base integration for cybersecurity analysis using ChromaDB for vector storage and semantic search. It incorporates three major cybersecurity frameworks: CWE (Common Weakness Enumeration), CAPEC (Common Attack Pattern Enumeration and Classification), and MITRE ATT&CK, enabling agents to query relevant security information using natural language semantic search.

### Key Features

- **Multi-Framework Integration**: CWE, CAPEC, and MITRE ATT&CK data
- **Semantic Search**: Vector-based similarity search using embeddings
- **Flexible Embedding Providers**: Built-in, local (Sentence Transformers), or OpenAI embeddings
- **Persistent Storage**: ChromaDB with configurable storage paths
- **Structured Queries**: Type-specific queries for targeted results
- **Lazy/Eager Loading**: Configurable initialization strategies

## Core Classes

### CweCapecAttackDatabase

Main interface for cybersecurity knowledge base operations with vector similarity search.

```python
from ivexes.vector_db import CweCapecAttackDatabase
from ivexes.config import PartialSettings

settings = PartialSettings(
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    chroma_path='/path/to/vector/storage'
)
db = CweCapecAttackDatabase(settings, load='eager')
```

#### Constructor

```python
def __init__(
    self,
    settings: IvexesSettings,
    load: Literal['lazy', 'eager'] = 'lazy'
) -> None
```

**Parameters:**
- `settings` (IvexesSettings): Configuration including embedding provider, model, and storage path
- `load` (Literal['lazy', 'eager']): Initialization strategy
  - `'lazy'`: Initialize database on first query (default)
  - `'eager'`: Initialize database immediately during construction

**Example:**
```python
from ivexes.config import PartialSettings

settings = PartialSettings(
    embedding_provider='openai',  # or 'local', 'builtin'
    embedding_model='text-embedding-3-small',
    openai_api_key='your-api-key',
    chroma_path='/home/user/.ivexes/chromadb'
)

# Lazy initialization - database loaded on first query
db = CweCapecAttackDatabase(settings, load='lazy')

# Eager initialization - database loaded immediately
db = CweCapecAttackDatabase(settings, load='eager')
```

#### Initialization Methods

##### initialize()

Download and initialize all cybersecurity knowledge bases with error handling.

```python
def initialize(self) -> None
```

**Process:**
1. Configure embedding function based on settings
2. Create ChromaDB persistent client
3. Initialize collection with embedding function
4. Download and parse CWE, CAPEC, and ATT&CK data if collection is empty

**Example:**
```python
db = CweCapecAttackDatabase(settings, load='lazy')
# Manually trigger initialization
db.initialize()
print(f"Database initialized with {db.collection.count()} entries")
```

##### initialize_cwe()

Initialize database with CWE (Common Weakness Enumeration) data.

```python
def initialize_cwe(self) -> None
```

Downloads and parses CWE XML data from MITRE, extracting weakness definitions and relationships.

##### initialize_capec()

Initialize database with CAPEC (Common Attack Pattern Enumeration) data.

```python
def initialize_capec(self) -> None
```

Downloads and parses CAPEC XML data, extracting attack pattern descriptions and relationships.

##### initialize_attack()

Initialize database with MITRE ATT&CK framework data.

```python
def initialize_attack(self) -> None
```

Downloads and parses ATT&CK STIX data including techniques, tactics, mitigations, groups, and software.

#### Query Methods

##### query()

General-purpose semantic search across knowledge bases with type filtering.

```python
def query(
    self, 
    query_text: str, 
    types: list[QueryTypes] | None = None, 
    n: int = 3
) -> list[str]
```

**Parameters:**
- `query_text` (str): Natural language query
- `types` (list[QueryTypes] | None): Filter by specific data types (default: all types)
- `n` (int): Number of results to return

**Returns:**
- `list[str]`: List of formatted knowledge base entries

**Query Types:**
```python
QueryTypes = Literal[
    'cwe',                  # Common Weakness Enumeration
    'capec',                # Common Attack Pattern Enumeration  
    'attack-technique',     # ATT&CK Techniques
    'attack-mitigation',    # ATT&CK Mitigations
    'attack-group',         # ATT&CK Threat Groups
    'attack-malware',       # ATT&CK Malware
    'attack-tool',          # ATT&CK Tools
    'attack-tactic',        # ATT&CK Tactics
]
```

**Example:**
```python
# General search across all knowledge bases
results = db.query("buffer overflow vulnerability", n=5)
for result in results:
    print(result)

# Search specific types
cwe_results = db.query(
    "sql injection", 
    types=['cwe', 'capec'], 
    n=3
)

# Search ATT&CK techniques only
attack_results = db.query(
    "privilege escalation",
    types=['attack-technique', 'attack-tactic'],
    n=5
)
```

##### query_cwe()

Search Common Weakness Enumeration entries.

```python
def query_cwe(self, query_text: str, n: int = 3) -> list[str]
```

**Example:**
```python
weaknesses = db.query_cwe("cross-site scripting", n=5)
for weakness in weaknesses:
    print(weakness)
```

##### query_capec()

Search Common Attack Pattern Enumeration entries.

```python
def query_capec(self, query_text: str, n: int = 3) -> list[str]
```

**Example:**
```python
attack_patterns = db.query_capec("social engineering", n=3)
for pattern in attack_patterns:
    print(pattern)
```

##### query_attack_techniques()

Search MITRE ATT&CK techniques.

```python
def query_attack_techniques(self, query_text: str, n: int = 3) -> list[str]
```

**Example:**
```python
techniques = db.query_attack_techniques("lateral movement", n=5)
for technique in techniques:
    print(technique)
```

##### query_attack_tactics()

Search MITRE ATT&CK tactics (kill chain phases).

```python
def query_attack_tactics(self, query_text: str, n: int = 3) -> list[str]
```

##### query_attack_mitigations()

Search MITRE ATT&CK mitigations.

```python
def query_attack_mitigations(self, query_text: str, n: int = 3) -> list[str]
```

##### query_attack_groups()

Search MITRE ATT&CK threat groups.

```python
def query_attack_groups(self, query_text: str, n: int = 3) -> list[str]
```

##### query_attack_software()

Search MITRE ATT&CK software (malware and tools).

```python
def query_attack_software(self, query_text: str, n: int = 3) -> list[str]
```

##### query_attack_all()

Search all MITRE ATT&CK data types.

```python
def query_attack_all(self, query_text: str, n: int = 3) -> list[str]
```

**Example:**
```python
# Comprehensive ATT&CK search
all_attack_info = db.query_attack_all("ransomware", n=10)
for info in all_attack_info:
    print(info)
```

#### Utility Methods

##### clear()

Clear all data from the database collection.

```python
def clear(self) -> None
```

**Example:**
```python
# Clear all data for fresh initialization
db.clear()
db.initialize()  # Reload data
```

## Tool Functions

### create_vectordb_tools()

Create vector database tools for agent integration.

```python
from ivexes.vector_db.tools import create_vectordb_tools

def create_vectordb_tools(
    db: Optional[CweCapecAttackDatabase] = None, 
    settings: Optional[Settings] = None
) -> list[Tool]
```

**Parameters:**
- `db` (Optional[CweCapecAttackDatabase]): Database instance (creates new if not provided)
- `settings` (Optional[Settings]): Configuration settings (loads from environment if not provided)

**Returns:**
- `list[Tool]`: List of tool functions for agent use

**Available Tools:**
- `semantic_search_cwe()`: Search CWE entries
- `semantic_search_capec()`: Search CAPEC entries  
- `semantic_search_attack_techniques()`: Search ATT&CK techniques
- `semantic_search_attack_tactics()`: Search ATT&CK tactics
- `semantic_search_attack_mitigations()`: Search ATT&CK mitigations
- `semantic_search_attack_groups()`: Search ATT&CK groups
- `semantic_search_attack_software()`: Search ATT&CK software
- `semantic_search_attack_all()`: Search all ATT&CK data
- `semantic_search()`: General search with type filtering

**Example:**
```python
from ivexes.agents import SingleAgent
from ivexes.vector_db.tools import create_vectordb_tools
from ivexes.config import PartialSettings

settings = PartialSettings(
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct'
)

# Create tools for agent
tools = create_vectordb_tools(settings=settings)

# Use with agent
agent = SingleAgent(bin_path='/usr/bin/target', settings=settings)
# Tools are automatically available to the agent
```

### Tool Functions Reference

#### semantic_search_cwe()

Agent tool for searching CWE entries.

```python
@function_tool
def semantic_search_cwe(query: str, n: int = 5) -> str
```

**Parameters:**
- `query` (str): Search query
- `n` (int): Number of results (default: 5)

**Returns:**
- `str`: Formatted search results

#### semantic_search_capec()

Agent tool for searching CAPEC entries.

```python
@function_tool
def semantic_search_capec(query: str, n: int = 5) -> str
```

#### semantic_search_attack_techniques()

Agent tool for searching ATT&CK techniques.

```python
@function_tool
def semantic_search_attack_techniques(query: str, n: int = 5) -> str
```

#### semantic_search()

General semantic search with type filtering.

```python
@function_tool
def semantic_search(query: str, type: list[QueryTypes], n: int = 5) -> str
```

**Parameters:**
- `query` (str): Search query
- `type` (list[QueryTypes]): Types to search
- `n` (int): Number of results

## Usage Examples

### Basic Knowledge Base Search

```python
"""Basic vector database operations."""

from ivexes.vector_db import CweCapecAttackDatabase
from ivexes.config import PartialSettings

# Configure database
settings = PartialSettings(
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct',
    chroma_path='/tmp/ivexes/chromadb'
)

# Initialize database
db = CweCapecAttackDatabase(settings, load='eager')

# Search for vulnerabilities
buffer_overflow_cwe = db.query_cwe("buffer overflow", n=3)
print("Buffer Overflow CWE Entries:")
for entry in buffer_overflow_cwe:
    print(f"- {entry}")

# Search for attack patterns
social_engineering = db.query_capec("social engineering", n=3)
print("\nSocial Engineering CAPEC:")
for pattern in social_engineering:
    print(f"- {pattern}")

# Search ATT&CK techniques
persistence = db.query_attack_techniques("persistence mechanisms", n=5)
print("\nPersistence Techniques:")
for technique in persistence:
    print(f"- {technique}")
```

### Multi-Type Knowledge Analysis

```python
"""Advanced multi-type knowledge base analysis."""

from ivexes.vector_db import CweCapecAttackDatabase
from ivexes.config import PartialSettings

settings = PartialSettings(
    embedding_provider='openai',
    embedding_model='text-embedding-3-small',
    openai_api_key='your-api-key'
)

db = CweCapecAttackDatabase(settings)

def analyze_security_topic(topic: str) -> dict:
    """Comprehensive analysis of a security topic across all knowledge bases."""
    
    analysis = {
        'topic': topic,
        'weaknesses': db.query_cwe(topic, n=3),
        'attack_patterns': db.query_capec(topic, n=3),
        'techniques': db.query_attack_techniques(topic, n=3),
        'mitigations': db.query_attack_mitigations(topic, n=3),
        'threat_groups': db.query_attack_groups(topic, n=2)
    }
    
    return analysis

# Analyze web application security
web_security = analyze_security_topic("web application security")

print(f"Analysis: {web_security['topic']}")
print(f"Found {len(web_security['weaknesses'])} related weaknesses")
print(f"Found {len(web_security['attack_patterns'])} attack patterns")
print(f"Found {len(web_security['techniques'])} techniques")
print(f"Found {len(web_security['mitigations'])} mitigations")

# Cross-reference analysis
for weakness in web_security['weaknesses']:
    print(f"Weakness: {weakness[:100]}...")
```

### Agent Integration Example

```python
"""Vector database integration with IVEXES agents."""

import asyncio
from ivexes.agents import SingleAgent
from ivexes.vector_db.tools import create_vectordb_tools
from ivexes.config import PartialSettings

async def vulnerability_research_agent():
    """Agent with vector database knowledge for enhanced analysis."""
    
    settings = PartialSettings(
        model='openai/gpt-4o-mini',
        max_turns=20,
        embedding_provider='local',
        embedding_model='intfloat/multilingual-e5-large-instruct',
        codebase_path='/path/to/vulnerable/code'
    )
    
    # Create vector database tools
    vectordb_tools = create_vectordb_tools(settings=settings)
    
    agent = SingleAgent(
        bin_path='/usr/bin/vulnerable_service',
        settings=settings
    )
    
    print("Starting vulnerability research with knowledge base integration...")
    
    # Agent now has access to all semantic search tools:
    # - semantic_search_cwe
    # - semantic_search_capec
    # - semantic_search_attack_techniques
    # - semantic_search_attack_mitigations
    # - semantic_search_attack_groups
    # - semantic_search_attack_software
    # - semantic_search_attack_all
    # - semantic_search
    
    async for chunk in agent.run_streamed():
        print(chunk, end='', flush=True)

# Run the research agent
if __name__ == "__main__":
    asyncio.run(vulnerability_research_agent())
```

### Custom Knowledge Base Analysis

```python
"""Custom knowledge base analysis with advanced filtering."""

from ivexes.vector_db import CweCapecAttackDatabase, QueryTypes
from ivexes.config import PartialSettings
from typing import Dict, List

class SecurityKnowledgeAnalyzer:
    """Advanced security knowledge analyzer with custom query strategies."""
    
    def __init__(self, settings: PartialSettings):
        self.db = CweCapecAttackDatabase(settings, load='lazy')
        self.cache = {}
    
    def comprehensive_threat_analysis(self, threat_description: str) -> Dict[str, List[str]]:
        """Perform comprehensive threat analysis across all knowledge bases."""
        
        if threat_description in self.cache:
            return self.cache[threat_description]
        
        # Ensure database is initialized
        self.db._check_database()
        
        analysis = {
            'threat_description': threat_description,
            'related_weaknesses': self.db.query_cwe(threat_description, n=5),
            'attack_patterns': self.db.query_capec(threat_description, n=5),
            'attack_techniques': self.db.query_attack_techniques(threat_description, n=5),
            'defensive_mitigations': self.db.query_attack_mitigations(threat_description, n=5),
            'known_threat_groups': self.db.query_attack_groups(threat_description, n=3),
            'associated_malware': self.db.query_attack_software(threat_description, n=3)
        }
        
        # Cache results
        self.cache[threat_description] = analysis
        return analysis
    
    def find_related_patterns(self, cwe_id: str) -> Dict[str, List[str]]:
        """Find related attack patterns and techniques for a specific CWE."""
        
        # Search for the specific CWE
        cwe_details = self.db.query_cwe(cwe_id, n=1)
        if not cwe_details:
            return {'error': f'CWE {cwe_id} not found'}
        
        cwe_description = cwe_details[0]
        
        # Extract key terms from CWE description for broader search
        search_terms = cwe_description.split()[:10]  # Use first 10 words
        search_query = ' '.join(search_terms)
        
        return {
            'cwe_details': cwe_details,
            'related_capec': self.db.query_capec(search_query, n=5),
            'attack_techniques': self.db.query_attack_techniques(search_query, n=5),
            'mitigations': self.db.query_attack_mitigations(search_query, n=3)
        }
    
    def threat_landscape_analysis(self, domain: str) -> Dict[str, int]:
        """Analyze threat landscape for a specific domain."""
        
        landscape = {}
        
        # Count different types of threats
        all_types: List[QueryTypes] = [
            'cwe', 'capec', 'attack-technique', 'attack-mitigation',
            'attack-group', 'attack-malware', 'attack-tool', 'attack-tactic'
        ]
        
        for threat_type in all_types:
            results = self.db.query(domain, types=[threat_type], n=10)
            landscape[threat_type] = len(results)
        
        return landscape

# Usage example
settings = PartialSettings(
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct'
)

analyzer = SecurityKnowledgeAnalyzer(settings)

# Comprehensive analysis
ransomware_analysis = analyzer.comprehensive_threat_analysis("ransomware attack")
print(f"Ransomware Analysis Results:")
print(f"- Related weaknesses: {len(ransomware_analysis['related_weaknesses'])}")
print(f"- Attack patterns: {len(ransomware_analysis['attack_patterns'])}")
print(f"- Attack techniques: {len(ransomware_analysis['attack_techniques'])}")

# CWE-specific analysis
buffer_overflow_patterns = analyzer.find_related_patterns("CWE-120")
print(f"\nBuffer Overflow (CWE-120) Related Patterns:")
print(f"- Related CAPEC patterns: {len(buffer_overflow_patterns.get('related_capec', []))}")

# Domain threat landscape
web_landscape = analyzer.threat_landscape_analysis("web application")
print(f"\nWeb Application Threat Landscape:")
for threat_type, count in web_landscape.items():
    print(f"- {threat_type}: {count} entries")
```

### Performance Optimization Example

```python
"""Vector database performance optimization and batch operations."""

from ivexes.vector_db import CweCapecAttackDatabase
from ivexes.config import PartialSettings
import time
from typing import List, Dict

class OptimizedKnowledgeSearch:
    """Optimized knowledge base search with caching and batch operations."""
    
    def __init__(self, settings: PartialSettings):
        # Use eager loading for better performance
        self.db = CweCapecAttackDatabase(settings, load='eager')
        self.search_cache = {}
        self.batch_cache = {}
    
    def cached_search(self, query: str, types: List[str] = None, n: int = 5) -> List[str]:
        """Cached search to avoid repeated queries."""
        
        cache_key = f"{query}_{types}_{n}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
        
        results = self.db.query(query, types, n)
        self.search_cache[cache_key] = results
        return results
    
    def batch_search(self, queries: List[str], types: List[str] = None, n: int = 3) -> Dict[str, List[str]]:
        """Perform batch searches efficiently."""
        
        batch_key = f"{hash(tuple(queries))}_{types}_{n}"
        if batch_key in self.batch_cache:
            return self.batch_cache[batch_key]
        
        results = {}
        for query in queries:
            results[query] = self.cached_search(query, types, n)
        
        self.batch_cache[batch_key] = results
        return results
    
    def clear_cache(self):
        """Clear search caches."""
        self.search_cache.clear()
        self.batch_cache.clear()

# Performance testing
settings = PartialSettings(
    embedding_provider='builtin',  # Fastest for testing
    chroma_path='/tmp/ivexes/perf_test'
)

optimizer = OptimizedKnowledgeSearch(settings)

# Batch vulnerability analysis
vulnerability_queries = [
    "sql injection",
    "cross-site scripting", 
    "buffer overflow",
    "privilege escalation",
    "authentication bypass"
]

start_time = time.time()
batch_results = optimizer.batch_search(vulnerability_queries, types=['cwe', 'capec'], n=3)
batch_time = time.time() - start_time

print(f"Batch search completed in {batch_time:.2f} seconds")
print(f"Found results for {len(batch_results)} queries")

# Test cache performance
start_time = time.time()
cached_results = optimizer.batch_search(vulnerability_queries, types=['cwe', 'capec'], n=3)
cached_time = time.time() - start_time

print(f"Cached search completed in {cached_time:.2f} seconds")
print(f"Performance improvement: {(batch_time - cached_time) / batch_time * 100:.1f}%")
```

## Configuration

### Embedding Providers

#### Built-in Provider (Default)
```python
settings = PartialSettings(
    embedding_provider='builtin'  # ChromaDB default embedding
)
```

#### Local Provider (Sentence Transformers)
```python
settings = PartialSettings(
    embedding_provider='local',
    embedding_model='intfloat/multilingual-e5-large-instruct'
)
```

#### OpenAI Provider
```python
settings = PartialSettings(
    embedding_provider='openai',
    embedding_model='text-embedding-3-small',
    openai_api_key='your-api-key'
)
```

### Storage Configuration

```python
settings = PartialSettings(
    chroma_path='/home/user/.ivexes/chromadb',  # Custom storage path
    embedding_model='intfloat/multilingual-e5-large-instruct'
)
```

## Error Handling

### Common Errors

1. **Initialization Failures**: Network issues downloading knowledge bases
2. **Embedding Errors**: Invalid API keys or model names
3. **Storage Issues**: Insufficient disk space or permissions
4. **Query Errors**: Invalid query types or parameters

### Error Handling Example

```python
"""Robust vector database usage with comprehensive error handling."""

from ivexes.vector_db import CweCapecAttackDatabase
from ivexes.config import PartialSettings
from ivexes.exceptions import VectorDatabaseError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_knowledge_search(query: str) -> dict:
    """Perform knowledge search with comprehensive error handling."""
    
    settings = PartialSettings(
        embedding_provider='local',
        embedding_model='intfloat/multilingual-e5-large-instruct',
        chroma_path='/tmp/ivexes/robust_test'
    )
    
    try:
        # Initialize database with retry logic
        db = None
        for attempt in range(3):
            try:
                db = CweCapecAttackDatabase(settings, load='eager')
                logger.info(f"Database initialized on attempt {attempt + 1}")
                break
            except Exception as e:
                logger.warning(f"Initialization attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise VectorDatabaseError(f"Failed to initialize after 3 attempts: {e}")
        
        # Perform searches with error handling
        results = {
            'query': query,
            'cwe_results': [],
            'capec_results': [],
            'attack_results': [],
            'errors': []
        }
        
        # CWE search
        try:
            results['cwe_results'] = db.query_cwe(query, n=3)
            logger.info(f"CWE search successful: {len(results['cwe_results'])} results")
        except Exception as e:
            results['errors'].append(f"CWE search failed: {e}")
            logger.error(f"CWE search error: {e}")
        
        # CAPEC search
        try:
            results['capec_results'] = db.query_capec(query, n=3)
            logger.info(f"CAPEC search successful: {len(results['capec_results'])} results")
        except Exception as e:
            results['errors'].append(f"CAPEC search failed: {e}")
            logger.error(f"CAPEC search error: {e}")
        
        # ATT&CK search
        try:
            results['attack_results'] = db.query_attack_all(query, n=5)
            logger.info(f"ATT&CK search successful: {len(results['attack_results'])} results")
        except Exception as e:
            results['errors'].append(f"ATT&CK search failed: {e}")
            logger.error(f"ATT&CK search error: {e}")
        
        return results
        
    except VectorDatabaseError as e:
        logger.error(f"Vector database error: {e}")
        return {
            'query': query,
            'error': str(e),
            'success': False
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'query': query,
            'error': f"Unexpected error: {e}",
            'success': False
        }

# Usage with error handling
search_results = robust_knowledge_search("privilege escalation")

if 'error' in search_results:
    print(f"Search failed: {search_results['error']}")
else:
    print(f"Search Results for: {search_results['query']}")
    print(f"- CWE entries: {len(search_results['cwe_results'])}")
    print(f"- CAPEC entries: {len(search_results['capec_results'])}")
    print(f"- ATT&CK entries: {len(search_results['attack_results'])}")
    
    if search_results['errors']:
        print(f"- Partial failures: {len(search_results['errors'])}")
        for error in search_results['errors']:
            print(f"  * {error}")
```

## Best Practices

### Performance Optimization

1. **Use Eager Loading**: For applications with frequent queries
2. **Cache Results**: Implement caching for repeated searches
3. **Batch Queries**: Group related searches together
4. **Choose Appropriate Embedding Models**: Balance accuracy vs speed
5. **Monitor Storage**: Vector databases can consume significant disk space

### Security Considerations

1. **API Key Management**: Secure storage of OpenAI API keys
2. **Storage Permissions**: Appropriate file system permissions for ChromaDB
3. **Network Security**: Consider network access for embedding providers
4. **Data Validation**: Validate query inputs to prevent injection attacks

### Troubleshooting

1. **Slow Initialization**: Check network connectivity for knowledge base downloads
2. **High Memory Usage**: Consider using built-in embeddings for resource-constrained environments
3. **Inconsistent Results**: Ensure consistent embedding model across sessions
4. **Storage Issues**: Monitor disk space and ChromaDB directory permissions

## See Also

- [Configuration API](config.md) - Settings and configuration management
- [Tools API](tools.md) - Shared utilities and helpers
- [Agents API](agents.md) - Agent integration and tool usage
- [Examples Guide](../documentation/examples.md) - Practical usage examples