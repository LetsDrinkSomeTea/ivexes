"""Test cases for the configuration module.

This module contains comprehensive unit tests for configuration management,
including settings validation, environment variable handling, and singleton behavior.
"""

import unittest
from unittest.mock import patch, Mock
import os
from pydantic import ValidationError

from ivexes.config.settings import (
    Settings,
    create_settings,
    get_run_config,
    PartialSettings,
)


class TestSettingsModule(unittest.TestCase):
    """Test cases for the configuration settings module."""

    def setUp(self):
        """Set up test environment."""
        # No global state to clear since we use create_settings() now
        pass

    def test_settings_default_values(self):
        """Test that settings have appropriate default values."""
        with patch.dict(os.environ, {'LLM_API_KEY': 'sk-test-key'}, clear=True):
            settings = Settings()

            # Test default values
            self.assertEqual(settings.model, 'openai/gpt-4o-mini')
            self.assertEqual(settings.model_temperature, 0.3)
            self.assertEqual(settings.reasoning_model, 'openai/o4-mini')
            self.assertEqual(settings.max_turns, 10)
            self.assertEqual(settings.log_level, 'INFO')
            self.assertEqual(settings.trace_name, 'ivexes')
            self.assertEqual(settings.sandbox_image, 'kali-ssh:latest')
            self.assertIsNone(settings.setup_archive)
            self.assertEqual(settings.chroma_path, '/tmp/ivexes/chromadb')
            self.assertEqual(settings.embedding_model, 'builtin')
            self.assertEqual(settings.embedding_provider, 'builtin')
            self.assertEqual(settings.llm_base_url, 'https://api.openai.com/v1')

    def test_settings_from_environment_variables(self):
        """Test that settings are loaded from environment variables."""
        test_env = {
            'OPENAI_API_KEY': 'sk-test-key-123',
            'LLM_API_KEY': 'llm-test-key',
            'LLM_BASE_URL': 'https://custom.api.com/v1',
            'MODEL': 'openai/gpt-4',
            'MODEL_TEMPERATURE': '0.7',
            'REASONING_MODEL': 'openai/o1-preview',
            'MAX_TURNS': '15',
            'LOG_LEVEL': 'DEBUG',
            'TRACE_NAME': 'custom-trace',
            'SANDBOX_IMAGE': 'custom-kali:latest',
            'SETUP_ARCHIVE': '/path/to/setup.tar.gz',
            'CODEBASE_PATH': '/path/to/codebase',
            'VULNERABLE_CODEBASE_FOLDER': '/path/to/vulnerable',
            'PATCHED_CODEBASE_FOLDER': '/path/to/patched',
            'CHROMA_PATH': '/custom/chroma',
            'EMBEDDING_MODEL': 'text-embedding-ada-002',
            'EMBEDDING_PROVIDER': 'openai',
        }

        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()

            # Test that environment variables are loaded
            self.assertEqual(settings.openai_api_key, 'sk-test-key-123')
            self.assertEqual(settings.llm_api_key, 'llm-test-key')
            self.assertEqual(settings.llm_base_url, 'https://custom.api.com/v1')
            self.assertEqual(settings.model, 'openai/gpt-4')
            self.assertEqual(settings.model_temperature, 0.7)
            self.assertEqual(settings.reasoning_model, 'openai/o1-preview')
            self.assertEqual(settings.max_turns, 15)
            self.assertEqual(settings.log_level, 'DEBUG')
            self.assertEqual(settings.trace_name, 'custom-trace')
            self.assertEqual(settings.sandbox_image, 'custom-kali:latest')
            self.assertEqual(settings.setup_archive, '/path/to/setup.tar.gz')
            self.assertEqual(settings.codebase_path, '/path/to/codebase')
            self.assertEqual(settings.vulnerable_folder, '/path/to/vulnerable')
            self.assertEqual(settings.patched_folder, '/path/to/patched')
            self.assertEqual(settings.chroma_path, '/custom/chroma')
            self.assertEqual(settings.embedding_model, 'text-embedding-ada-002')
            self.assertEqual(settings.embedding_provider, 'openai')

    def test_settings_validation_api_keys(self):
        """Test validation of API keys."""
        # Test empty API key validation
        with patch.dict(os.environ, {'LLM_API_KEY': ''}, clear=True):
            with self.assertRaises(ValidationError) as cm:
                Settings()
            self.assertIn('API key cannot be empty', str(cm.exception))

        # Test whitespace-only API key
        with patch.dict(os.environ, {'LLM_API_KEY': '   '}, clear=True):
            with self.assertRaises(ValidationError) as cm:
                Settings()
            self.assertIn('API key cannot be empty', str(cm.exception))

        # Test valid API key
        with patch.dict(os.environ, {'LLM_API_KEY': 'sk-valid-key'}, clear=True):
            settings = Settings()
            self.assertEqual(settings.llm_api_key, 'sk-valid-key')

    def test_settings_validation_temperature(self):
        """Test validation of temperature values."""
        # Test temperature below 0.0
        with patch.dict(
            os.environ,
            {'LLM_API_KEY': 'sk-test-key', 'MODEL_TEMPERATURE': '-0.1'},
            clear=True,
        ):
            with self.assertRaises(ValidationError) as cm:
                Settings()
            self.assertIn('Temperature must be between 0.0 and 2.0', str(cm.exception))

        # Test temperature above 2.0
        with patch.dict(
            os.environ,
            {'LLM_API_KEY': 'sk-test-key', 'MODEL_TEMPERATURE': '2.1'},
            clear=True,
        ):
            with self.assertRaises(ValidationError) as cm:
                Settings()
            self.assertIn('Temperature must be between 0.0 and 2.0', str(cm.exception))

        # Test valid temperatures
        valid_temps = ['0.0', '1.0', '2.0', '0.5', '1.5']
        for temp in valid_temps:
            with patch.dict(
                os.environ,
                {'LLM_API_KEY': 'sk-test-key', 'MODEL_TEMPERATURE': temp},
                clear=True,
            ):
                settings = Settings()
                self.assertEqual(settings.model_temperature, float(temp))

    def test_settings_validation_max_turns(self):
        """Test validation of max_turns values."""
        # Test negative max_turns
        with patch.dict(
            os.environ, {'LLM_API_KEY': 'sk-test-key', 'MAX_TURNS': '-1'}, clear=True
        ):
            with self.assertRaises(ValidationError) as cm:
                Settings()
            self.assertIn('Max turns must be a positive integer', str(cm.exception))

        # Test zero max_turns
        with patch.dict(
            os.environ, {'LLM_API_KEY': 'sk-test-key', 'MAX_TURNS': '0'}, clear=True
        ):
            with self.assertRaises(ValidationError) as cm:
                Settings()
            self.assertIn('Max turns must be a positive integer', str(cm.exception))

        # Test valid max_turns
        with patch.dict(
            os.environ, {'LLM_API_KEY': 'sk-test-key', 'MAX_TURNS': '5'}, clear=True
        ):
            settings = Settings()
            self.assertEqual(settings.max_turns, 5)

    def test_settings_validation_log_level(self):
        """Test validation of log level values."""
        # Test invalid log level
        with patch.dict(
            os.environ,
            {'LLM_API_KEY': 'sk-test-key', 'LOG_LEVEL': 'INVALID'},
            clear=True,
        ):
            with self.assertRaises(ValidationError) as cm:
                Settings()
            self.assertIn(
                "Input should be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'",
                str(cm.exception),
            )
        # Test valid log levels
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        for level in valid_levels:
            with patch.dict(
                os.environ,
                {'LLM_API_KEY': 'sk-test-key', 'LOG_LEVEL': level},
                clear=True,
            ):
                settings = Settings()
                self.assertEqual(settings.log_level, level)

        # Test case insensitive log levels
        with patch.dict(
            os.environ, {'LLM_API_KEY': 'sk-test-key', 'LOG_LEVEL': 'debug'}, clear=True
        ):
            with self.assertRaises(ValidationError) as cm:
                settings = Settings()
            self.assertIn(
                "Input should be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'",
                str(cm.exception),
            )

    def test_settings_validation_base_url(self):
        """Test validation of base URL values."""
        # Test invalid base URL (no protocol)
        with patch.dict(
            os.environ,
            {'LLM_API_KEY': 'sk-test-key', 'LLM_BASE_URL': 'api.openai.com'},
            clear=True,
        ):
            with self.assertRaises(ValidationError) as cm:
                Settings()
            self.assertIn(
                'Base URL must start with http:// or https://', str(cm.exception)
            )

        # Test valid base URLs
        valid_urls = [
            'https://api.openai.com/v1',
            'http://localhost:8000',
            'https://custom.api.com',
        ]
        for url in valid_urls:
            with patch.dict(
                os.environ,
                {'LLM_API_KEY': 'sk-test-key', 'LLM_BASE_URL': url},
                clear=True,
            ):
                settings = Settings()
                self.assertEqual(settings.llm_base_url, url)

    def test_create_settings_validation_error_handling(self):
        """Test that create_settings properly handles validation errors."""
        with patch.dict(os.environ, {'LLM_API_KEY': ''}, clear=True):
            with self.assertRaises(RuntimeError) as cm:
                create_settings()
            self.assertIn('Configuration validation failed', str(cm.exception))

    def test_llm_api_key_fallback(self):
        """Test that LLM_API_KEY falls back to OPENAI_API_KEY if not set."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-openai-key'}, clear=True):
            settings = Settings()
            self.assertEqual(settings.llm_api_key, 'sk-openai-key')

        # Test that LLM_API_KEY takes precedence
        with patch.dict(
            os.environ,
            {'OPENAI_API_KEY': 'sk-openai-key', 'LLM_API_KEY': 'sk-llm-key'},
            clear=True,
        ):
            settings = Settings()
            self.assertEqual(settings.llm_api_key, 'sk-llm-key')

    def test_trace_name_lowercase(self):
        """Test that trace_name is converted to lowercase."""
        with patch.dict(
            os.environ,
            {'LLM_API_KEY': 'sk-test-key', 'TRACE_NAME': 'CUSTOM-TRACE'},
            clear=True,
        ):
            settings = Settings()
            self.assertEqual(settings.trace_name, 'custom-trace')

    def test_optional_fields(self):
        """Test that optional fields can be None."""
        with patch.dict(os.environ, {'LLM_API_KEY': 'sk-test-key'}, clear=True):
            settings = Settings()
            self.assertIsNone(settings.codebase_path)
            self.assertIsNone(settings.vulnerable_folder)
            self.assertIsNone(settings.patched_folder)

    def test_get_run_config_basic(self):
        """Test get_run_config returns a proper RunConfig."""
        with patch.dict(
            os.environ,
            {
                'OPENAI_API_KEY': 'sk-test-key',
                'LLM_API_KEY': 'sk-llm-key',
                'MODEL_TEMPERATURE': '0.8',
            },
            clear=True,
        ):
            with patch('ivexes.config.settings.AsyncOpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client

                settings = create_settings()
                run_config = get_run_config(settings)

                # Verify AsyncOpenAI was called with correct parameters
                mock_openai.assert_called_once_with(
                    base_url='https://api.openai.com/v1', api_key='sk-llm-key'
                )

                # Verify run_config has correct model
                self.assertIsNotNone(run_config.model_settings)
                self.assertEqual(run_config.model_settings.temperature, 0.8)

    def test_environment_variable_types(self):
        """Test that environment variables are properly converted to correct types."""
        with patch.dict(
            os.environ,
            {
                'LLM_API_KEY': 'sk-test-key',
                'MODEL_TEMPERATURE': '0.9',
                'MAX_TURNS': '20',
            },
            clear=True,
        ):
            settings = Settings()

            # Verify types are correct
            self.assertIsInstance(settings.model_temperature, float)
            self.assertIsInstance(settings.max_turns, int)
            self.assertEqual(settings.model_temperature, 0.9)
            self.assertEqual(settings.max_turns, 20)

    def test_field_validator_edge_cases(self):
        """Test edge cases in field validators."""
        # Test exact boundary values for temperature
        with patch.dict(
            os.environ,
            {'LLM_API_KEY': 'sk-test-key', 'MODEL_TEMPERATURE': '0.0'},
            clear=True,
        ):
            settings = Settings()
            self.assertEqual(settings.model_temperature, 0.0)

        with patch.dict(
            os.environ,
            {'LLM_API_KEY': 'sk-test-key', 'MODEL_TEMPERATURE': '2.0'},
            clear=True,
        ):
            settings = Settings()
            self.assertEqual(settings.model_temperature, 2.0)

        # Test minimum valid max_turns
        with patch.dict(
            os.environ, {'LLM_API_KEY': 'sk-test-key', 'MAX_TURNS': '1'}, clear=True
        ):
            settings = Settings()
            self.assertEqual(settings.max_turns, 1)

    def test_settings_with_all_fields(self):
        """Test settings initialization with all fields provided."""
        full_env = {
            'OPENAI_API_KEY': 'sk-openai-key',
            'BRAVE_SEARCH_API_KEY': 'brave-key',
            'LLM_API_KEY': 'llm-key',
            'LLM_BASE_URL': 'https://custom.api.com/v1',
            'MODEL': 'openai/gpt-4-turbo',
            'MODEL_TEMPERATURE': '0.5',
            'REASONING_MODEL': 'openai/o1-mini',
            'MAX_TURNS': '25',
            'LOG_LEVEL': 'WARNING',
            'TRACE_NAME': 'production-trace',
            'SANDBOX_IMAGE': 'production-kali:v2',
            'SETUP_ARCHIVE': '/prod/setup.tar.gz',
            'CODEBASE_PATH': '/prod/codebase',
            'VULNERABLE_CODEBASE_FOLDER': '/prod/vulnerable',
            'PATCHED_CODEBASE_FOLDER': '/prod/patched',
            'CHROMA_PATH': '/prod/chroma',
            'EMBEDDING_MODEL': 'text-embedding-3-large',
            'EMBEDDING_PROVIDER': 'openai',
        }

        with patch.dict(os.environ, full_env, clear=True):
            settings = Settings()

            # Verify all fields are set correctly
            self.assertEqual(settings.openai_api_key, 'sk-openai-key')
            self.assertEqual(settings.llm_api_key, 'llm-key')
            self.assertEqual(settings.llm_base_url, 'https://custom.api.com/v1')
            self.assertEqual(settings.model, 'openai/gpt-4-turbo')
            self.assertEqual(settings.model_temperature, 0.5)
            self.assertEqual(settings.reasoning_model, 'openai/o1-mini')
            self.assertEqual(settings.max_turns, 25)
            self.assertEqual(settings.log_level, 'WARNING')
            self.assertEqual(settings.trace_name, 'production-trace')
            self.assertEqual(settings.sandbox_image, 'production-kali:v2')
            self.assertEqual(settings.setup_archive, '/prod/setup.tar.gz')
            self.assertEqual(settings.codebase_path, '/prod/codebase')
            self.assertEqual(settings.vulnerable_folder, '/prod/vulnerable')
            self.assertEqual(settings.patched_folder, '/prod/patched')
            self.assertEqual(settings.chroma_path, '/prod/chroma')
            self.assertEqual(settings.embedding_model, 'text-embedding-3-large')
            self.assertEqual(settings.embedding_provider, 'openai')

    def test_create_settings_partial_override(self):
        """Test create_settings with partial settings override."""
        with patch.dict(os.environ, {'LLM_API_KEY': 'sk-test-key'}, clear=True):
            # Override some settings
            partial_settings: PartialSettings = {
                'model': 'openai/gpt-4',
                'model_temperature': 0.8,
                'max_turns': 25,
            }
            settings = create_settings(partial_settings)

            # Verify overridden fields
            self.assertEqual(settings.model, 'openai/gpt-4')
            self.assertEqual(settings.model_temperature, 0.8)
            self.assertEqual(settings.max_turns, 25)

            # Verify non-overridden fields use defaults
            self.assertEqual(settings.log_level, 'INFO')  # Default value
            self.assertEqual(settings.llm_api_key, 'sk-test-key')

    def test_create_settings_validation(self):
        """Test that create_settings validates the updated settings."""
        with patch.dict(os.environ, {'LLM_API_KEY': 'sk-test-key'}, clear=True):
            # Test invalid temperature
            with self.assertRaises(RuntimeError) as cm:
                create_settings({'model_temperature': 3.0})
            self.assertIn('Temperature must be between 0.0 and 2.0', str(cm.exception))

            # Test invalid max_turns
            with self.assertRaises(RuntimeError) as cm:
                create_settings({'max_turns': -1})
            self.assertIn('Max turns must be a positive integer', str(cm.exception))

    def test_create_settings_empty_dict(self):
        """Test create_settings with empty dictionary."""
        with patch.dict(os.environ, {'LLM_API_KEY': 'sk-test-key'}, clear=True):
            # Create settings with empty dictionary - should use defaults
            settings = create_settings({})

            # Settings should use defaults
            self.assertEqual(settings.model, 'openai/gpt-4o-mini')  # Default
            self.assertEqual(settings.llm_api_key, 'sk-test-key')

    def test_create_settings_environment_vs_partial(self):
        """Test create_settings with environment variables vs partial overrides."""
        with patch.dict(
            os.environ,
            {
                'LLM_API_KEY': 'sk-test-key',
                'MODEL': 'openai/gpt-3.5-turbo',
                'MODEL_TEMPERATURE': '0.5',
            },
            clear=True,
        ):
            # Get settings from environment only
            env_settings = create_settings()
            self.assertEqual(env_settings.model, 'openai/gpt-3.5-turbo')
            self.assertEqual(env_settings.model_temperature, 0.5)

            # Override with partial settings
            partial_settings = create_settings(
                {'model': 'openai/gpt-4', 'model_temperature': 0.9}
            )
            self.assertEqual(partial_settings.model, 'openai/gpt-4')
            self.assertEqual(partial_settings.model_temperature, 0.9)

            # Original environment settings should be unchanged
            self.assertEqual(env_settings.model, 'openai/gpt-3.5-turbo')
            self.assertEqual(env_settings.model_temperature, 0.5)

    def test_partial_settings_type_hints(self):
        """Test that PartialSettings type hints work correctly."""
        # This test ensures the type works with type checkers
        # All fields should be optional
        partial: PartialSettings = {}
        self.assertEqual(partial, {})

        partial_with_values: PartialSettings = {
            'model': 'openai/gpt-4',
            'model_temperature': 0.7,
        }
        self.assertEqual(partial_with_values['model'], 'openai/gpt-4')
        self.assertEqual(partial_with_values['model_temperature'], 0.7)

    def test_create_settings_with_all_fields(self):
        """Test create_settings with all possible fields."""
        with patch.dict(os.environ, {'LLM_API_KEY': 'sk-test-key'}, clear=True):
            full_partial: PartialSettings = {
                'openai_api_key': 'sk-new-openai',
                'llm_api_key': 'sk-new-llm',
                'llm_base_url': 'https://new.api.com/v1',
                'model': 'openai/gpt-4-turbo',
                'model_temperature': 0.7,
                'reasoning_model': 'openai/o1-preview',
                'max_turns': 30,
                'log_level': 'DEBUG',
                'trace_name': 'new-trace',
                'sandbox_image': 'new-kali:latest',
                'setup_archive': '/new/setup.tar.gz',
                'codebase_path': '/new/codebase',
                'vulnerable_folder': '/new/vulnerable',
                'patched_folder': '/new/patched',
                'chroma_path': '/new/chroma',
                'embedding_model': 'new-embedding',
                'embedding_provider': 'builtin',
            }

            settings = create_settings(full_partial)

            # Verify all fields were set
            self.assertEqual(settings.openai_api_key, 'sk-new-openai')
            self.assertEqual(settings.llm_api_key, 'sk-new-llm')
            self.assertEqual(settings.llm_base_url, 'https://new.api.com/v1')
            self.assertEqual(settings.model, 'openai/gpt-4-turbo')
            self.assertEqual(settings.model_temperature, 0.7)
            self.assertEqual(settings.reasoning_model, 'openai/o1-preview')
            self.assertEqual(settings.max_turns, 30)
            self.assertEqual(settings.log_level, 'DEBUG')
            self.assertEqual(settings.trace_name, 'new-trace')
            self.assertEqual(settings.sandbox_image, 'new-kali:latest')
            self.assertEqual(settings.setup_archive, '/new/setup.tar.gz')
            self.assertEqual(settings.codebase_path, '/new/codebase')
            self.assertEqual(settings.vulnerable_folder, '/new/vulnerable')
            self.assertEqual(settings.patched_folder, '/new/patched')
            self.assertEqual(settings.chroma_path, '/new/chroma')
            self.assertEqual(settings.embedding_model, 'new-embedding')
            self.assertEqual(settings.embedding_provider, 'builtin')


if __name__ == '__main__':
    unittest.main()
