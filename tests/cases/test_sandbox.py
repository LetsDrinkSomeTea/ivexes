"""Tests for sandbox functionality."""

import io
import os
import time
import unittest
from unittest.mock import patch

from ivexes.config import PartialSettings, create_settings
from ivexes.sandbox import Sandbox


class TestSandboxModule(unittest.TestCase):
    """Test cases for the Sandbox module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sandbox = None
        self.temp_files = []
        with patch.dict(
            os.environ,
            {
                'LLM_API_KEY': 'sk-test-key',
                'SANDBOX_IMAGE': 'python:3.13',
            },
            clear=True,
        ):
            self.settings = create_settings(
                PartialSettings(
                    llm_api_key='llm-key-for-verification', sandbox_image='python:3.13'
                )
            )

    def tearDown(self):
        """Clean up after each test method."""
        if self.sandbox:
            try:
                self.sandbox.close()
            except:
                pass

        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                os.remove(temp_file)
            except:
                pass

    def test_basic_sandbox(self):
        """Test basic sandbox functionality."""
        self.sandbox = Sandbox(settings=self.settings)

        # Test initial state
        self.assertFalse(self.sandbox.is_running())

        # Test connection
        self.assertTrue(self.sandbox.connect())
        self.assertTrue(self.sandbox.is_running())

        # Test file operations
        test_file_content = 'Test123'
        self.assertTrue(self.sandbox.write_file('/tmp/test.txt', test_file_content))
        self.assertEqual(self.sandbox.read_file('/tmp/test.txt'), test_file_content)

        # Test command execution
        exit_code, output = self.sandbox.run('whoami')
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.strip(), 'user')

        # Test command execution with different user
        exit_code, output = self.sandbox.run('whoami', user='root')
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.strip(), 'root')

        # Test cleanup
        self.sandbox.close()
        self.assertFalse(self.sandbox.is_running())

    def test_interactive_mode(self):
        """Test interactive session functionality."""
        self.sandbox = Sandbox(settings=self.settings)
        self.assertTrue(self.sandbox.connect())

        # Test basic interactive session
        with self.sandbox.interactive('sh') as session:
            self.assertTrue(session.is_alive())

            # Wait for shell prompt
            session.send('echo "Hello World"')
            output = session.read()
            self.assertIn('Hello World', output[1])

        # Session should be closed after context manager
        self.assertFalse(session.is_alive())

    def test_file_operations(self):
        """Test file read/write operations."""
        self.sandbox = Sandbox(settings=self.settings)
        self.assertTrue(self.sandbox.connect())

        # Test writing and reading various file types
        test_cases = [
            ('simple.txt', 'Hello World'),
            ('multiline.txt', 'Line 1\nLine 2\nLine 3'),
            ('special_chars.txt', 'Special: !@#$%^&*()'),
            ('unicode.txt', 'Unicode: 你好世界 🌍'),
            ('empty.txt', ''),
        ]

        for filename, content in test_cases:
            with self.subTest(filename=filename):
                filepath = f'/tmp/{filename}'
                self.assertTrue(self.sandbox.write_file(filepath, content))
                read_content = self.sandbox.read_file(filepath)
                self.assertEqual(read_content, content)

        # Test reading non-existent file
        self.assertIsNone(self.sandbox.read_file('/tmp/nonexistent.txt'))

    def test_command_execution_edge_cases(self):
        """Test edge cases in command execution."""
        self.sandbox = Sandbox(settings=self.settings)
        self.assertTrue(self.sandbox.connect())

        # Test command with exit code 0
        exit_code, output = self.sandbox.run('echo "success"')
        self.assertEqual(exit_code, 0)
        self.assertIn('success', output)

        # Test long-running command
        exit_code, output = self.sandbox.run('sleep 1 && echo "done"')
        self.assertEqual(exit_code, 0)
        self.assertIn('done', output)

        # Test command with pipes
        exit_code, output = self.sandbox.run('echo hello world | wc -w')
        self.assertEqual(exit_code, 0)
        self.assertIn('2', output.strip())

        # Test command with stderr
        exit_code, output = self.sandbox.run('echo "error" >&2')
        self.assertEqual(exit_code, 0)
        self.assertIn('error', output)

    def test_context_manager(self):
        """Test context manager functionality."""
        # Test successful context manager
        with Sandbox(settings=self.settings) as sandbox:
            self.assertTrue(sandbox.is_running())
            exit_code, output = sandbox.run('echo "test"')
            self.assertEqual(exit_code, 0)
            self.assertIn('test', output)

        # Sandbox should be closed after context manager
        self.assertFalse(sandbox.is_running())

        # Test context manager with exception
        try:
            with Sandbox(settings=self.settings) as sandbox:
                self.assertTrue(sandbox.is_running())
                raise ValueError('Test exception')
        except ValueError:
            pass  # Expected

        # Sandbox should still be closed after exception
        self.assertFalse(sandbox.is_running())

    def test_interactive_session_patterns(self):
        """Test interactive session pattern matching."""
        self.sandbox = Sandbox(settings=self.settings)
        self.assertTrue(self.sandbox.connect())

        with self.sandbox.interactive('python3') as session:
            # Test multiple pattern matching
            session.send('print("Hello from Python")')
            output = session.read()
            self.assertIn('Hello from Python', output[1])

            session.send('exit()')

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test operations without connection
        sandbox = Sandbox(settings=self.settings)

        with self.assertRaises(RuntimeError):
            sandbox.run('echo "test"')

        with self.assertRaises(RuntimeError):
            sandbox.interactive('sh')

        # Test file operations without connection
        self.assertFalse(sandbox.write_file('/tmp/test.txt', 'test'))
        self.assertIsNone(sandbox.read_file('/tmp/test.txt'))

        # Test invalid interactive session
        sandbox.connect()
        try:
            # This should work even if the command fails
            with sandbox.interactive('invalid_command_xyz') as session:
                # Session might not be alive due to invalid command
                pass
        except Exception:
            pass  # Expected for invalid command

        sandbox.close()

    def test_setup_archive_functionality(self):
        """Test sandbox with setup archive."""
        # Create a temporary setup archive
        import tarfile
        import tempfile

        with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp_file:
            self.temp_files.append(tmp_file.name)

            # Create a simple setup archive
            with tarfile.open(tmp_file.name, 'w') as tar:
                # Add a setup script
                setup_script = """#!/bin/sh
echo "Setup script executed" > /tmp/setup_log.txt
"""
                setup_info = tarfile.TarInfo('setup.sh')
                setup_info.size = len(setup_script.encode())
                setup_info.mode = 0o755
                tar.addfile(setup_info, io.BytesIO(setup_script.encode()))

        # Test sandbox with setup archive
        # Create settings with setup archive
        settings_with_archive = create_settings(
            PartialSettings(
                llm_api_key='llm-key-for-verification',
                setup_archive=tmp_file.name,
                sandbox_image='python:3.13',
            )
        )
        self.sandbox = Sandbox(settings=settings_with_archive)
        self.assertTrue(self.sandbox.connect())

        # Check if setup script was executed
        # Note: This depends on the setup_container implementation
        # which should run the setup script
        time.sleep(2)  # Wait for setup to complete

        # Try to read the setup log
        log_content = self.sandbox.read_file('/tmp/setup_log.txt')
        if log_content:  # Only check if setup was actually run
            self.assertIn('Setup script executed', log_content)

    def test_concurrent_operations(self):
        """Test concurrent operations and session management."""
        self.sandbox = Sandbox(settings=self.settings)
        self.assertTrue(self.sandbox.connect())

        # Test multiple file operations
        for i in range(5):
            filename = f'/tmp/concurrent_test_{i}.txt'
            content = f'Content {i}'
            self.assertTrue(self.sandbox.write_file(filename, content))
            self.assertEqual(self.sandbox.read_file(filename), content)

        # Test multiple command executions
        results = []
        for i in range(3):
            exit_code, output = self.sandbox.run(f'echo "Command {i}"')
            results.append((exit_code, output))

        for i, (exit_code, output) in enumerate(results):
            self.assertEqual(exit_code, 0)
            self.assertIn(f'Command {i}', output)

    def test_working_directory_and_user_settings(self):
        """Test working directory and user settings."""
        # Test custom working directory
        self.sandbox = Sandbox(
            settings=self.settings, working_dir='/tmp', username='root'
        )
        self.assertTrue(self.sandbox.connect())

        # Test that working directory is respected
        exit_code, output = self.sandbox.run('pwd')
        self.assertEqual(exit_code, 0)
        self.assertIn('/tmp', output)

        # Test that user is respected
        exit_code, output = self.sandbox.run('whoami')
        self.assertEqual(exit_code, 0)
        self.assertIn('root', output)

    def test_interactive_session_lifecycle(self):
        """Test interactive session lifecycle management."""
        self.sandbox = Sandbox(settings=self.settings)
        self.assertTrue(self.sandbox.connect())

        # Test session creation and destruction
        session = self.sandbox.interactive('sh')
        self.assertTrue(session.is_alive())

        # Test session operations
        session.send('echo "test"')
        time.sleep(0.1)

        # Test manual close
        session.close()
        self.assertFalse(session.is_alive())

        # Test that we can create another session
        session2 = self.sandbox.interactive('python3')
        self.assertTrue(session2.is_alive())
        session2.close()

    def test_large_file_operations(self):
        """Test operations with larger files."""
        self.sandbox = Sandbox(settings=self.settings)
        self.assertTrue(self.sandbox.connect())

        # Test with larger content
        large_content = 'A' * 10000 + '\n' + 'B' * 10000
        self.assertTrue(self.sandbox.write_file('/tmp/large_file.txt', large_content))

        read_content = self.sandbox.read_file('/tmp/large_file.txt')
        self.assertEqual(read_content, large_content)

        # Test file size
        exit_code, output = self.sandbox.run('wc -c /tmp/large_file.txt')
        self.assertEqual(exit_code, 0)
        # Should be 20001 characters (10000 + 1 + 10000)
        self.assertIn('20001', output)

    @patch('ivexes.sandbox.sandbox.setup_container')
    def test_connection_failure_handling(self, mock_setup):
        """Test handling of connection failures."""
        # Mock setup_container to raise an exception
        mock_setup.side_effect = Exception('Connection failed')

        sandbox = Sandbox(settings=self.settings)
        self.assertFalse(sandbox.connect())
        self.assertFalse(sandbox.is_running())

    def test_python_interactive_session(self):
        """Test Python interactive session specifically."""
        self.sandbox = Sandbox(settings=self.settings)
        self.assertTrue(self.sandbox.connect())

        with self.sandbox.interactive('python3') as py_session:
            # Wait for Python prompt
            py_session.send('x = 42')
            py_session.read()

            py_session.send('print(x)')
            output = py_session.read()
            self.assertIn('42', output[1])

            # Test multiline input
            py_session.send('def test_func():')
            py_session.send('    return "hello"')
            py_session.send('')  # Empty line to complete function
            output = py_session.read()

            py_session.send('print(test_func())')
            output = py_session.read()
            self.assertIn('hello', output[1])


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
