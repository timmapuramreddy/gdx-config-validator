# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The GDX Config Validator Library is a comprehensive Python library for validating GDX (Glue DataXpress) configuration files. It provides robust validation for YAML configurations with SQL injection security, performance optimization via LRU caching, and enterprise-grade features.

## Development Environment Setup

### Virtual Environment
Always use the project's virtual environment:
```bash
# Activate the venv
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt
```

### Common Development Commands

#### Testing
```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific test categories
python -m pytest src/tests/ -m unit -v           # Unit tests only
python -m pytest src/tests/ -m security -v       # Security tests only
python -m pytest src/tests/ -m performance -v    # Performance tests only

# Run tests with coverage
python -m pytest src/tests/ --cov=src/gdx_config_validator --cov-report=html

# Run comprehensive validation test directly
python src/tests/test_yaml_validation.py
```

#### Code Quality
```bash
# Format code with black
black src/ --line-length=100

# Run linting
flake8 src/

# Type checking
mypy src/gdx_config_validator/
```

#### Package Management
```bash
# Install in development mode
pip install -e .

# Build package
python setup.py sdist bdist_wheel

# Install with dev dependencies
pip install -e ".[dev]"
```

## Architecture Overview

### Core Components
- **Factory Pattern** (`factory.py`): Main entry point with `ValidatorType` constants and `create_validator()` function
- **Base Validation** (`core.py`): `BaseValidator` class with rule engine, metrics, and logging infrastructure
- **Validators** (`validators.py`): 5 main validator classes from basic YAML parsing to SQL-enhanced validation
- **Operation Registry** (`schemas/operations.py`): 20+ predefined operations with parameter validation
- **Results System** (`results.py`): `ValidationResult` and `ValidationResultBuilder` classes
- **Logging Adapter** (`logging_adapter.py`): Flexible logging that adapts to GDX Framework or standalone use

### Validator Types
1. **BASIC**: Basic YAML parsing (`GDXYamlParser`)
2. **COMPREHENSIVE**: Full structure validation (`ComprehensiveYamlValidator`)
3. **JOB**: Job-level validation (`GDXJobValidator`)
4. **EXTENDED_JOB**: Enhanced job validation (`ExtendedGDXJobValidator`)
5. **SQL_ENHANCED**: SQL security validation (`SQLExpressionColumnValidator`)

### Key Design Patterns
- Factory pattern for validator creation
- Builder pattern for validation results
- Registry pattern for operations (20+ operations across 6 categories)
- Adapter pattern for logging integration
- Decorator pattern for validation metrics and logging

## Code Organization

### Source Structure
```
src/gdx_config_validator/
├── __init__.py              # Public API with 170+ exports
├── core.py                  # Base classes, rule engine (800+ lines)
├── validators.py            # Main validator implementations (3,300+ lines)
├── factory.py              # Factory functions and high-level API (450+ lines)
├── results.py              # Validation result system (400+ lines)
├── schemas/operations.py    # Operation specifications (500+ lines)
├── logging_adapter.py       # Enhanced logging system (400+ lines)
├── config.py               # Configuration management (200+ lines)
├── parsers.py              # YAML parsing utilities (300+ lines)
└── utils.py                # Helper functions (400+ lines)
```

### Test Structure
```
src/tests/
├── conftest.py                  # Pytest fixtures and configuration
├── test_yaml_validation.py      # Comprehensive validation tests
├── test_security.py             # SQL injection and security tests
├── test_operations.py           # Operation registry tests
├── test_enhanced_logging.py     # Logging system tests
└── test.yaml                   # Sample test configuration
```

## Development Guidelines

### Adding New Validators
1. Inherit from `BaseValidator` in `core.py`
2. Use `ValidationContext` and `ValidationMetrics` 
3. Register validation rules with `ValidationRuleEngine`
4. Follow existing patterns in `validators.py`
5. Add factory method in `factory.py`

### Adding New Operations
1. Define operation in `schemas/operations.py`
2. Add to `OPERATION_REGISTRY` with proper `ParameterSpec`
3. Include parameter validation and type checking
4. Add comprehensive tests in `test_operations.py`

### Security Considerations
- The library includes SQL injection detection with 15+ security patterns
- Always validate SQL expressions in transformations
- Use the security test fixtures in `conftest.py` for testing
- SQL validation patterns are in `validators.py` around line 800+

### Performance Features
- LRU caching implemented for 50-90% speed improvements
- Performance tests available with `@pytest.mark.performance`
- Use `ValidationMetrics` for performance tracking
- Large config fixture available for performance testing

### Testing Strategy
- Comprehensive test coverage with 22+ automated tests
- Security-focused testing with SQL injection scenarios
- Performance benchmarking with large configurations
- Framework integration testing for GDX compatibility

## Library Integration

### Standalone Usage
```python
from gdx_config_validator import validate_file, ValidatorType

result = validate_file("config.yaml", ValidatorType.COMPREHENSIVE)
```

### GDX Framework Integration
```python
from gdx_config_validator import GDXJobValidator

validator = GDXJobValidator(logger=gdx_framework_logger, validation_mode="sql_enhanced")
is_valid, summary = validator.validate_job_configuration(config)
```

### Quick Validation
```python
from gdx_config_validator import quick_validate

is_valid = quick_validate("config.yaml")
```

## Configuration Files

- **pyproject.toml**: Modern Python packaging with pytest, mypy, black, coverage configuration
- **setup.py**: Comprehensive setuptools configuration with 40+ classifiers
- **requirements.txt**: Minimal runtime dependency (PyYAML>=6.0)
- **requirements-dev.txt**: Development dependencies including pytest, black, flake8, mypy

## Documentation

- **docs/README.md**: Complete library documentation (main reference)
- **docs/USAGE_EXAMPLES.md**: 18+ practical usage examples
- **docs/DEVELOPER_GUIDE.md**: Maintenance and extension guide
- **docs/API_REFERENCE.md**: Complete API documentation
- **docs/ENHANCEMENTS.md**: Security, performance, and testing improvements

## Version and Compatibility

- Current version: 1.0.0 (production ready)
- Python compatibility: 3.8+
- Single runtime dependency: PyYAML>=6.0
- Comprehensive development toolchain in requirements-dev.txt