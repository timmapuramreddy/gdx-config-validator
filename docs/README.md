# GDX Config Validator Library

A comprehensive Python library for validating GDX (Glue DataXpress) configuration files. Provides robust validation for YAML configurations with detailed error reporting, SQL expression support, flexible parameter validation, advanced security features, and performance optimization.

## 🆕 Latest Enhancements (v1.0.0)

- **🛡️ Advanced Security**: SQL injection detection with 15+ security patterns
- **⚡ Performance Optimized**: LRU caching for 50-90% speed improvement
- **🧪 Comprehensive Testing**: 22+ automated tests with full coverage
- **📊 Enhanced Operations**: 20+ operations with flexible parameter validation

👉 **[See Full Enhancement Details](ENHANCEMENTS.md)**

## 🚀 Quick Start

```python
from gdx_config_validator import validate_file, ValidatorType

# Simple validation
result = validate_file("config.yaml", ValidatorType.COMPREHENSIVE)
print(f"Valid: {result.is_valid}")

# Quick boolean check
from gdx_config_validator import quick_validate
is_valid = quick_validate("config.yaml")
```

## 📋 Table of Contents

1. [Library Overview](#library-overview)
2. [Architecture & Structure](#architecture--structure)
3. [API Reference](#api-reference)
4. [Usage Examples](#usage-examples)
5. [Developer Guide](#developer-guide)
6. [Maintenance & Enhancement](#maintenance--enhancement)

## 🏗️ Library Overview

### Key Features

- **🔍 Comprehensive Validation**: Validates YAML structure, transformations, operations, and SQL expressions
- **⚡ Multiple Validator Types**: Basic, Comprehensive, Job-level, and SQL-enhanced validators
- **🔧 Flexible Logging**: Automatic adaptation to GDX Framework, standalone, or custom loggers
- **🏭 Production Ready**: Silent mode, error handling, and performance optimization
- **🎯 Developer Friendly**: Factory pattern, clean APIs, and extensible architecture
- **📊 Detailed Reporting**: Rich error messages with suggestions and context

### Supported Validations

| Validation Type | Description | Use Case |
|-----------------|-------------|----------|
| **YAML Structure** | Basic YAML parsing and structure validation | Quick syntax checks |
| **Transformation Validation** | Column transformations, data types, operations | Data pipeline validation |
| **Cross-Reference Validation** | References between different YAML sections | Configuration consistency |
| **SQL Expression Validation** | Complex SQL expressions in transformations | Advanced data transformations |
| **Operation Registry** | 20+ predefined operations across 6 categories | Standardized operations |
| **Job Configuration** | Complete job-level validation with history | Enterprise validation |

## 🏛️ Architecture & Structure

### Project Structure

```
src/gdx_config_validator/
├── __init__.py              # Public API exports
├── results.py               # ValidationResult classes and utilities
├── core.py                  # BaseValidator and infrastructure
├── schemas/
│   └── operations.py        # Operation registry and specifications
├── validators.py            # All validator implementations
├── logging_adapter.py       # Enhanced logging system
├── config.py               # Configuration presets and management
├── parsers.py              # YAML parsing utilities
├── utils.py                # Operation registry utilities
└── factory.py              # Factory pattern implementation
```

### Core Components

#### 1. **ValidationResult System** (`results.py`)
- `ValidationResult`: Core result container with errors, warnings, and metadata
- `ValidationResultBuilder`: Builder pattern for constructing results
- `ValidationSeverity`: Enum for error severity levels
- Utility functions for creating specialized results

#### 2. **Base Infrastructure** (`core.py`)
- `BaseValidator`: Abstract base class for all validators
- `ValidationContext`: Context management for validation sessions
- `ValidationMetrics`: Performance and statistics tracking
- `ValidationRuleEngine`: Pluggable validation rule system

#### 3. **Validator Implementations** (`validators.py`)
- `GDXYamlParser`: Basic YAML parsing and validation (600+ lines)
- `ComprehensiveYamlValidator`: Advanced validation with cross-references (600+ lines)
- `SQLExpressionColumnValidator`: SQL expression validation (500+ lines)
- `GDXJobValidator`: Enterprise job validation (547+ lines)
- `ExtendedGDXJobValidator`: Enhanced with SQL support (477+ lines)

#### 4. **Operation Registry** (`schemas/operations.py`)
- 20+ predefined operations across 6 categories
- Parameter specifications with type validation
- Extensible registry for custom operations

#### 5. **Factory Pattern** (`factory.py`)
- `ValidatorType`: Constants for easy validator selection
- `create_validator()`: Factory function with multiple validator types
- High-level convenience functions for common tasks

## 📖 API Reference

### High-Level Functions

```python
# File validation
from gdx_config_validator import validate_file, ValidatorType
result = validate_file("config.yaml", ValidatorType.COMPREHENSIVE)

# String validation
from gdx_config_validator import validate_string
result = validate_string(yaml_content, ValidatorType.SQL_ENHANCED)

# Quick validation
from gdx_config_validator import quick_validate
is_valid = quick_validate("config.yaml")

# Job configuration validation
from gdx_config_validator import validate_job_config
is_valid, summary = validate_job_config(config_dict, include_sql_validation=True)
```

### Factory Functions

```python
from gdx_config_validator import create_validator, ValidatorType

# Create specific validator types
parser = create_validator(ValidatorType.BASIC, logger=my_logger)
comprehensive = create_validator(ValidatorType.COMPREHENSIVE)
job_validator = create_validator(ValidatorType.JOB, validation_mode="comprehensive")
sql_enhanced = create_validator(ValidatorType.SQL_ENHANCED)
```

### Direct Validator Usage

```python
from gdx_config_validator import GDXJobValidator, ComprehensiveYamlValidator

# Enterprise job validator
validator = GDXJobValidator(logger=gdx_logger, validation_mode="sql_enhanced")
is_valid, summary = validator.validate_job_configuration(config)

# Comprehensive validator
validator = ComprehensiveYamlValidator(logger=my_logger)
result = validator.validate_comprehensive(parsed_yaml)
```

### Configuration Management

```python
from gdx_config_validator import (
    configure_for_production, configure_for_development,
    configure_for_testing, LoggingContext
)

# Preset configurations
configure_for_production()    # Errors only
configure_for_development()   # Verbose logging
configure_for_testing()       # Silent mode

# Temporary configuration
with LoggingContext(debug=True, force_console=True):
    # Temporary debug mode
    result = validate_file("config.yaml")
```

## 🎯 Usage Examples

### Example 1: Basic File Validation

```python
from gdx_config_validator import validate_file, ValidatorType

# Validate a YAML file
result = validate_file("job_config.yaml", ValidatorType.COMPREHENSIVE)

if result.is_valid:
    print("✅ Configuration is valid!")
else:
    print(f"❌ Found {len(result.errors)} errors:")
    for error in result.errors:
        print(f"  - {error['message']}")
        if 'suggestion' in error:
            print(f"    💡 Suggestion: {error['suggestion']}")
```

### Example 2: Enterprise Job Validation

```python
from gdx_config_validator import GDXJobValidator, configure_for_production

# Configure for production environment
configure_for_production()

# Create enterprise validator
validator = GDXJobValidator(
    logger=gdx_framework_logger,
    validation_mode="sql_enhanced"
)

# Validate complete job configuration
is_valid, summary = validator.validate_job_configuration(job_config)

if not is_valid:
    print(f"Validation failed: {summary}")
    
    # Get detailed validation history
    history = validator.get_validation_history()
    for entry in history[-5:]:  # Last 5 validations
        print(f"- {entry['timestamp']}: {entry['result']}")
```

### Example 3: Custom Logging Integration

```python
from gdx_config_validator import ExtendedGDXJobValidator

# Mock GDX Framework Logger
class GDXLogger:
    def info(self, msg): print(f"GDX-INFO: {msg}")
    def warning(self, msg): print(f"GDX-WARN: {msg}")
    def error(self, msg): print(f"GDX-ERROR: {msg}")
    def debug(self, msg): print(f"GDX-DEBUG: {msg}")

gdx_logger = GDXLogger()

# Validator automatically adapts to GDX logger interface
validator = ExtendedGDXJobValidator(
    logger=gdx_logger,
    validation_mode="comprehensive"
)

result = validator.validate_job_configuration(config)
# Logs will automatically use GDX logger format
```

### Example 4: Batch Directory Validation

```python
from gdx_config_validator import validate_directory, get_validation_summary

# Validate all YAML files in directory
results = validate_directory("configs/", pattern="*.yaml", 
                           validator_type=ValidatorType.SQL_ENHANCED)

# Generate summary report
summary = get_validation_summary(results)
print(f"Validation Summary:")
print(f"  Total files: {summary['total_count']}")
print(f"  Valid files: {summary['valid_count']}")
print(f"  Success rate: {summary['success_rate']:.1%}")
print(f"  Total errors: {summary['total_errors']}")

# Show files with issues
if summary['invalid_files']:
    print("Files with errors:")
    for file_path in summary['invalid_files']:
        result = results[file_path]
        print(f"  - {file_path}: {len(result.errors)} errors")
```

### Example 5: Advanced Error Handling

```python
from gdx_config_validator import validate_file, ValidationSeverity

try:
    result = validate_file("complex_config.yaml", ValidatorType.SQL_ENHANCED)
    
    # Categorize issues by severity
    critical_errors = [e for e in result.errors if e.get('severity') == 'critical']
    warnings = result.warnings
    
    if critical_errors:
        print("🚨 Critical errors found:")
        for error in critical_errors:
            print(f"  - {error['message']}")
            if 'path' in error:
                print(f"    Location: {error['path']}")
    
    if warnings:
        print("⚠️ Warnings:")
        for warning in warnings:
            print(f"  - {warning['message']}")
    
    # Performance metrics
    if hasattr(result, 'performance_metrics'):
        metrics = result.performance_metrics
        print(f"📊 Validation took {metrics.get('duration', 0):.2f}s")
        
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

### Example 6: Configuration Presets

```python
from gdx_config_validator import (
    configure_for_development, configure_for_testing,
    configure_for_standalone, LoggingContext
)

# Development mode - verbose logging
configure_for_development()
dev_result = validate_file("config.yaml")

# Testing mode - silent
configure_for_testing()
test_result = validate_file("config.yaml")

# Standalone mode - warnings and errors only
configure_for_standalone()
standalone_result = validate_file("config.yaml")

# Temporary debug mode
with LoggingContext(debug=True):
    debug_result = validate_file("config.yaml")
    # Automatically reverts after context
```

## 🔧 Developer Guide

### Adding Custom Validators

```python
from gdx_config_validator import BaseValidator, ValidationResultBuilder

class CustomValidator(BaseValidator):
    def __init__(self, logger=None):
        super().__init__(logger, "CustomValidator")
    
    def validate(self, config_data):
        builder = ValidationResultBuilder()
        
        # Add your custom validation logic
        if 'custom_field' not in config_data:
            builder.add_error(
                'missing_custom_field',
                'Custom field is required',
                severity='error'
            )
        
        return builder.build()
```

### Extending Operation Registry

```python
from gdx_config_validator.schemas.operations import OPERATION_REGISTRY, OperationSpec, ParameterSpec, ParameterType

# Define new operation
new_operation = OperationSpec(
    name="custom_transform",
    category="custom",
    description="Custom transformation operation",
    parameters={
        "pattern": ParameterSpec(
            type=ParameterType.STRING,
            required=True,
            description="Transformation pattern"
        )
    },
    examples=["custom_transform(pattern='${value}_transformed')"]
)

# Register new operation
OPERATION_REGISTRY.register_operation(new_operation)
```

For more detailed developer information, see [Developer Guide](DEVELOPER_GUIDE.md).

## 📈 Performance & Best Practices

### Performance Tips

1. **Use appropriate validator types**: Don't use SQL_ENHANCED for simple structure validation
2. **Enable silent mode in production**: Use `configure_for_production()` or `silent=True`
3. **Batch validate directories**: Use `validate_directory()` for multiple files
4. **Cache validators**: Reuse validator instances for multiple validations

### Best Practices

1. **Error Handling**: Always check `result.is_valid` before processing
2. **Logging Configuration**: Set up logging early in your application
3. **Resource Management**: Use context managers for temporary configurations
4. **Validation Levels**: Choose the right validator type for your use case

## 📚 Additional Documentation

- [Developer Guide](DEVELOPER_GUIDE.md) - Detailed development and maintenance guide
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Examples](examples/) - Comprehensive usage examples
- [Changelog](CHANGELOG.md) - Version history and updates

## 🤝 Contributing

See [Developer Guide](DEVELOPER_GUIDE.md) for information on:
- Adding new validation rules
- Extending operation registry
- Contributing new validator types
- Testing guidelines

## 📄 License

This library is developed by Mohan Reddy for GDX (Glue DataXpress) configuration validation.