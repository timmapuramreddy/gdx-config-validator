"""
Pytest configuration and fixtures for GDX Config Validator tests

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# Add the library to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import gdx_config_validator
from gdx_config_validator import (
    ValidationResult, ValidationResultBuilder, 
    configure_for_testing, reset_logging_config
)

@pytest.fixture(scope="session", autouse=True)
def setup_testing_environment():
    """Setup testing environment with silent logging"""
    configure_for_testing()
    yield
    reset_logging_config()

@pytest.fixture
def sample_valid_config() -> Dict[str, Any]:
    """Sample valid GDX configuration for testing"""
    return {
        'settings': {
            'env': 'test',
            'load': 'full'
        },
        'mappings': [{
            'mapping_name': 'test_mapping',
            'source_table': 'source_test',
            'target_table': 'target_test',
            'source_columns_interested': [
                'id as test_id',
                'name as test_name',
                'email as test_email'
            ],
            'column_transformations': [{
                'source_alias': 'test_name',
                'target_column': 'processed_name',
                'data_type': 'VARCHAR(100)',
                'transformation_type': 'string_manipulation',
                'transformations': [
                    {'type': 'trim'}
                ]
            }]
        }]
    }

@pytest.fixture
def sample_invalid_config() -> Dict[str, Any]:
    """Sample invalid GDX configuration for testing"""
    return {
        'settings': {
            'env': 'invalid_env',
            'load': 'invalid_load'
        },
        'mappings': [{
            'mapping_name': 'test_mapping',
            'source_table': 'source_test',
            'target_table': 'target_test',
            'source_columns_interested': [
                'id as test_id'
            ],
            'column_transformations': [{
                'source_alias': 'missing_column',  # This column is not in source_columns_interested
                'target_column': 'processed_name',
                'data_type': 'INVALID_TYPE',
                'transformation_type': 'invalid_transformation'
            }]
        }]
    }

@pytest.fixture
def sql_injection_config() -> Dict[str, Any]:
    """Configuration with potential SQL injection for security testing"""
    return {
        'settings': {
            'env': 'test'
        },
        'mappings': [{
            'mapping_name': 'security_test',
            'source_table': 'test_table',
            'target_table': 'target_table',
            'source_columns_interested': [
                "id; DROP TABLE users; --",  # SQL injection attempt
                "name'; EXEC xp_cmdshell('dir'); --",  # Command injection
                "email UNION SELECT password FROM admin_users"  # Union injection
            ]
        }]
    }

@pytest.fixture
def test_yaml_file_path() -> Path:
    """Path to the test YAML file"""
    return Path(__file__).parent / "test.yaml"

@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    class MockLogger:
        def __init__(self):
            self.messages = []
        
        def info(self, msg):
            self.messages.append(('INFO', msg))
        
        def warning(self, msg):
            self.messages.append(('WARNING', msg))
        
        def error(self, msg):
            self.messages.append(('ERROR', msg))
        
        def debug(self, msg):
            self.messages.append(('DEBUG', msg))
        
        def get_messages(self):
            return self.messages
        
        def clear(self):
            self.messages.clear()
    
    return MockLogger()

@pytest.fixture
def validation_result_builder():
    """Fresh ValidationResultBuilder for testing"""
    return ValidationResultBuilder()

# Performance test fixture
@pytest.fixture
def large_config() -> Dict[str, Any]:
    """Large configuration for performance testing"""
    mappings = []
    for i in range(100):
        mappings.append({
            'mapping_name': f'mapping_{i}',
            'source_table': f'source_{i}',
            'target_table': f'target_{i}',
            'source_columns_interested': [
                f'id_{i} as mapped_id_{i}',
                f'name_{i} as mapped_name_{i}',
                f'value_{i} as mapped_value_{i}'
            ],
            'column_transformations': [{
                'source_alias': f'mapped_name_{i}',
                'target_column': f'processed_name_{i}',
                'data_type': 'VARCHAR(255)',
                'transformation_type': 'string_manipulation'
            }]
        })
    
    return {
        'settings': {
            'env': 'test',
            'load': 'full'
        },
        'mappings': mappings
    }

# Marks for test categorization
def pytest_configure(config):
    """Configure custom pytest marks"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interaction"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and benchmarking tests"
    )
    config.addinivalue_line(
        "markers", "security: Security validation tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )