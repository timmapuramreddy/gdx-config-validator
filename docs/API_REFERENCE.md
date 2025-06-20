# API Reference - GDX Config Validator Library

Complete API documentation for the GDX Config Validator Library.

## 🆕 New in v1.0.0

- **🛡️ Security Validation**: SQL injection detection with `ValidatorType.SQL_ENHANCED`
- **⚡ Performance Caching**: LRU cache for operation lookups with `@lru_cache`
- **🧪 Testing Framework**: 22+ automated tests with pytest integration
- **📊 Enhanced Operations**: 20+ operations with flexible parameter validation

## 📋 Table of Contents

1. [Core Classes](#core-classes)
2. [Validator Classes](#validator-classes)
3. [Factory Functions](#factory-functions)
4. [Configuration Management](#configuration-management)
5. [Result Classes](#result-classes)
6. [Utility Functions](#utility-functions)
7. [Operation Registry](#operation-registry)
8. [Logging System](#logging-system)

## 🏗️ Core Classes

### BaseValidator

Abstract base class for all validators.

```python
class BaseValidator(ABC):
    def __init__(self, logger=None, component_name: str = "BaseValidator")
```

**Parameters:**
- `logger`: External logger instance (optional)
- `component_name`: Name for logging identification

**Abstract Methods:**
- `validate(config_data: Dict[str, Any]) -> ValidationResult`

**Methods:**
- `get_logger_info() -> Dict[str, Any]`: Get logging configuration info
- `log_info(message: str)`: Log info message
- `log_warning(message: str)`: Log warning message
- `log_error(message: str)`: Log error message
- `log_debug(message: str)`: Log debug message

### ValidationContext

Context manager for validation sessions.

```python
class ValidationContext:
    def __init__(self, config_data: Dict[str, Any], metadata: Dict = None)
```

**Parameters:**
- `config_data`: Configuration data to validate
- `metadata`: Additional context metadata

**Properties:**
- `config_data`: The configuration data
- `metadata`: Context metadata
- `start_time`: Validation start timestamp

### ValidationMetrics

Performance and statistics tracking.

```python
class ValidationMetrics:
    def __init__(self)
```

**Methods:**
- `start_timer(operation: str)`: Start timing an operation
- `end_timer(operation: str)`: End timing an operation
- `add_counter(name: str, value: int = 1)`: Add to a counter
- `get_metrics() -> Dict[str, Any]`: Get all metrics
- `reset()`: Reset all metrics

### ValidationRuleEngine

Pluggable validation rule system.

```python
class ValidationRuleEngine:
    def __init__(self)
```

**Methods:**
- `register_rule(name: str, function: Callable, description: str, severity: ValidationSeverity, categories: List[str])`: Register a validation rule
- `execute_rules(context: ValidationContext, categories: List[str] = None) -> List[Dict]`: Execute rules by category
- `get_registered_rules() -> Dict[str, Dict]`: Get all registered rules

## 🔧 Validator Classes

### GDXYamlParser

Basic YAML parsing and validation.

```python
class GDXYamlParser(BaseValidator):
    def __init__(self, logger=None)
```

**Methods:**
- `validate(config_data: Dict[str, Any]) -> ValidationResult`: Basic validation
- `parse_yaml_file(file_path: str) -> Dict[str, Any]`: Parse YAML file
- `validate_transformations(config_data: Dict) -> ValidationResult`: Validate transformations

### ComprehensiveYamlValidator

Advanced validation with cross-references.

```python
class ComprehensiveYamlValidator(BaseValidator):
    def __init__(self, logger=None)
```

**Methods:**
- `validate_comprehensive(config_data: Dict[str, Any]) -> ValidationResult`: Comprehensive validation
- `validate_cross_references(config_data: Dict) -> ValidationResult`: Cross-reference validation
- `validate_sql_expressions(config_data: Dict) -> ValidationResult`: SQL expression validation

### SQLExpressionColumnValidator

SQL expression validation support.

```python
class SQLExpressionColumnValidator(BaseValidator):
    def __init__(self, logger=None)
```

**Methods:**
- `validate_sql_expressions(expressions: List[str]) -> ValidationResult`: Validate SQL expressions
- `analyze_column_dependencies(expression: str) -> List[str]`: Analyze column dependencies
- `validate_sql_syntax(expression: str) -> bool`: Validate SQL syntax

### GDXJobValidator

Enterprise job validation with history tracking.

```python
class GDXJobValidator(BaseValidator):
    def __init__(self, logger=None, validation_mode: str = "comprehensive", silent: bool = False)
```

**Parameters:**
- `logger`: External logger instance
- `validation_mode`: Validation mode ("basic", "comprehensive", "sql_enhanced")
- `silent`: Enable silent mode

**Methods:**
- `validate_job_configuration(config_data: Dict[str, Any]) -> Tuple[bool, str]`: Validate job configuration
- `validate_mapping_configuration(mapping_config: Dict[str, Any]) -> Tuple[bool, str]`: Validate mapping configuration
- `get_validation_history() -> List[Dict]`: Get validation history
- `get_performance_metrics() -> Dict[str, Any]`: Get performance metrics

### ExtendedGDXJobValidator

Enhanced validator with SQL expression support.

```python
class ExtendedGDXJobValidator(BaseValidator):
    def __init__(self, logger=None, validation_mode: str = "comprehensive")
```

**Methods:**
- All methods from `GDXJobValidator`
- Enhanced SQL expression validation
- Advanced error reporting with suggestions

## 🏭 Factory Functions

### create_validator

Factory function to create validators.

```python
def create_validator(validator_type: str = ValidatorType.COMPREHENSIVE, 
                    logger=None, silent: bool = False, **kwargs) -> Any
```

**Parameters:**
- `validator_type`: Type of validator (ValidatorType constants)
- `logger`: External logger instance
- `silent`: Force silent logging
- `**kwargs`: Additional arguments for validator

**ValidatorType Constants:**
- `ValidatorType.BASIC`: Basic YAML parser
- `ValidatorType.COMPREHENSIVE`: Comprehensive validator
- `ValidatorType.JOB`: Job validator
- `ValidatorType.EXTENDED_JOB`: Extended job validator
- `ValidatorType.SQL_ENHANCED`: SQL-enhanced validator
- `ValidatorType.PARSER_ONLY`: Parser only

**Returns:** Configured validator instance

### validate_file

High-level file validation function.

```python
def validate_file(file_path: Union[str, Path], 
                 validator_type: str = ValidatorType.COMPREHENSIVE,
                 logger=None, silent: bool = False) -> ValidationResult
```

**Parameters:**
- `file_path`: Path to YAML file
- `validator_type`: Type of validator to use
- `logger`: External logger instance
- `silent`: Force silent logging

**Returns:** ValidationResult with complete validation results

### validate_string

High-level string validation function.

```python
def validate_string(yaml_string: str,
                   validator_type: str = ValidatorType.COMPREHENSIVE,
                   logger=None, silent: bool = False) -> ValidationResult
```

**Parameters:**
- `yaml_string`: YAML content as string
- `validator_type`: Type of validator to use
- `logger`: External logger instance
- `silent`: Force silent logging

**Returns:** ValidationResult with complete validation results

### validate_job_config

High-level job configuration validation.

```python
def validate_job_config(job_config: Dict[str, Any],
                       include_sql_validation: bool = False,
                       logger=None, silent: bool = False) -> Tuple[bool, str]
```

**Parameters:**
- `job_config`: Job configuration dictionary
- `include_sql_validation`: Whether to include SQL validation
- `logger`: External logger instance
- `silent`: Force silent logging

**Returns:** Tuple of (is_valid, summary_message)

### validate_mapping_config

High-level mapping configuration validation.

```python
def validate_mapping_config(mapping_config: Dict[str, Any],
                           include_sql_validation: bool = False,
                           logger=None, silent: bool = False) -> Tuple[bool, str]
```

**Parameters:**
- `mapping_config`: Single mapping configuration dictionary
- `include_sql_validation`: Whether to include SQL validation
- `logger`: External logger instance
- `silent`: Force silent logging

**Returns:** Tuple of (is_valid, summary_message)

### quick_validate

Quick validation function returning boolean result.

```python
def quick_validate(data: Union[str, Path, Dict[str, Any]],
                  logger=None, silent: bool = True) -> bool
```

**Parameters:**
- `data`: File path, YAML string, or config dictionary
- `logger`: External logger instance
- `silent`: Use silent logging (default True)

**Returns:** True if valid, False otherwise

### validate_directory

Validate all YAML files in a directory.

```python
def validate_directory(directory_path: Union[str, Path],
                      pattern: str = "*.yaml",
                      validator_type: str = ValidatorType.COMPREHENSIVE,
                      logger=None, silent: bool = False) -> Dict[str, ValidationResult]
```

**Parameters:**
- `directory_path`: Path to directory containing YAML files
- `pattern`: File pattern to match (default: "*.yaml")
- `validator_type`: Type of validator to use
- `logger`: External logger instance
- `silent`: Force silent logging

**Returns:** Dict mapping file paths to validation results

### get_validation_summary

Generate summary statistics from multiple validation results.

```python
def get_validation_summary(results: Dict[str, ValidationResult]) -> Dict[str, Any]
```

**Parameters:**
- `results`: Dictionary of validation results from validate_directory

**Returns:** Dict containing summary statistics:
- `total_count`: Total number of files
- `valid_count`: Number of valid files
- `invalid_count`: Number of invalid files
- `success_rate`: Success rate as decimal
- `total_errors`: Total error count
- `total_warnings`: Total warning count
- `invalid_files`: List of invalid file paths
- `files_with_warnings`: List of files with warnings
- `avg_errors_per_file`: Average errors per file
- `avg_warnings_per_file`: Average warnings per file

### get_validator_info

Get information about available validators.

```python
def get_validator_info(validator_type: str = None) -> Dict[str, Any]
```

**Parameters:**
- `validator_type`: Specific validator type (optional)

**Returns:** Dict containing validator information

## ⚙️ Configuration Management

### configure_for_production

Configure library for production environment.

```python
def configure_for_production(level: str = "ERROR")
```

**Parameters:**
- `level`: Logging level for production

### configure_for_development

Configure library for development environment.

```python
def configure_for_development(level: str = "DEBUG", force_console: bool = True)
```

**Parameters:**
- `level`: Logging level for development
- `force_console`: Force console output

### configure_for_testing

Configure library for testing environment.

```python
def configure_for_testing(silent: bool = True)
```

**Parameters:**
- `silent`: Enable silent mode for testing

### configure_for_standalone

Configure library for standalone usage.

```python
def configure_for_standalone(level: str = "WARNING")
```

**Parameters:**
- `level`: Logging level for standalone usage

### LoggingContext

Context manager for temporary logging configuration.

```python
class LoggingContext:
    def __init__(self, level: str = None, debug: bool = False, 
                 force_console: bool = False, silent: bool = False)
```

**Parameters:**
- `level`: Temporary logging level
- `debug`: Enable debug mode
- `force_console`: Force console output
- `silent`: Enable silent mode

**Usage:**
```python
with LoggingContext(debug=True):
    # Temporary debug logging
    result = validate_file("config.yaml")
```

### setup_logging_for_standalone

Configure logging for standalone usage.

```python
def setup_logging_for_standalone(level: str = "WARNING", debug: bool = False)
```

**Parameters:**
- `level`: Logging level
- `debug`: Enable debug mode

## 📊 Result Classes

### ValidationResult

Core result container with errors, warnings, and metadata.

```python
class ValidationResult:
    def __init__(self, is_valid: bool = True, errors: List = None, 
                 warnings: List = None, metadata: Dict = None)
```

**Properties:**
- `is_valid`: Boolean indicating if validation passed
- `errors`: List of error dictionaries
- `warnings`: List of warning dictionaries
- `metadata`: Additional metadata
- `error_count`: Number of errors
- `warning_count`: Number of warnings

**Methods:**
- `add_error(error_dict: Dict)`: Add an error
- `add_warning(warning_dict: Dict)`: Add a warning
- `merge(other_result: ValidationResult)`: Merge with another result
- `to_dict() -> Dict[str, Any]`: Convert to dictionary
- `get_errors_by_type(error_type: str) -> List[Dict]`: Get errors by type
- `get_errors_by_severity(severity: str) -> List[Dict]`: Get errors by severity

### ValidationResultBuilder

Builder pattern for constructing ValidationResult objects.

```python
class ValidationResultBuilder:
    def __init__(self)
```

**Methods:**
- `add_error(error_type: str, message: str, path: str = None, severity: str = 'error', **kwargs)`: Add an error
- `add_warning(warning_type: str, message: str, path: str = None, **kwargs)`: Add a warning
- `add_info(info_type: str, message: str, **kwargs)`: Add info message
- `set_metadata(key: str, value: Any)`: Set metadata
- `build() -> ValidationResult`: Build the final result

### ValidationSeverity

Enum for error severity levels.

```python
class ValidationSeverity(Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
```

### Utility Functions

#### create_success_result

Create a successful validation result.

```python
def create_success_result(message: str = "Validation passed", 
                         metadata: Dict = None) -> ValidationResult
```

#### create_error_result

Create an error validation result.

```python
def create_error_result(error_type: str, message: str, path: str = None, 
                       severity: str = 'error', **kwargs) -> ValidationResult
```

#### create_exception_result

Create a result from an exception.

```python
def create_exception_result(exception: Exception, context: str = None) -> ValidationResult
```

## 🔧 Utility Functions

### Operation Registry Utilities

#### get_supported_operations

Get list of all supported operation types.

```python
def get_supported_operations() -> List[str]
```

**Returns:** List of operation type names

#### validate_operation_type

Check if an operation type is supported.

```python
def validate_operation_type(operation_type: str) -> bool
```

**Parameters:**
- `operation_type`: Name of the operation to check

**Returns:** True if operation is supported

#### get_operation_info

Get detailed information about a specific operation.

```python
def get_operation_info(operation_type: str) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `operation_type`: Name of the operation

**Returns:** Dict containing operation information or None

#### get_operations_by_category

Get all operations in a specific category.

```python
def get_operations_by_category(category: str) -> List[OperationSpec]
```

**Parameters:**
- `category`: Category name (e.g., 'string', 'numeric', 'date')

**Returns:** List of OperationSpec objects in the category

#### get_available_categories

Get list of all available operation categories.

```python
def get_available_categories() -> List[str]
```

**Returns:** List of category names

#### get_operation_suggestions

Get operation suggestions based on partial name.

```python
def get_operation_suggestions(partial_name: str, limit: int = 5) -> List[str]
```

**Parameters:**
- `partial_name`: Partial operation name to match
- `limit`: Maximum number of suggestions

**Returns:** List of suggested operation names

#### validate_operation_parameters

Validate parameters for a specific operation.

```python
def validate_operation_parameters(operation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]
```

**Parameters:**
- `operation_type`: Name of the operation
- `parameters`: Parameters to validate

**Returns:** Dict with validation results containing 'valid', 'errors', and 'warnings'

### Data Type Utilities

#### validate_data_type

Validate a data type string against supported pattern.

```python
def validate_data_type(data_type: str) -> bool
```

#### normalize_data_type

Normalize a data type string to standard format.

```python
def normalize_data_type(data_type: str) -> str
```

#### extract_data_type_info

Extract information from a data type string.

```python
def extract_data_type_info(data_type: str) -> Dict[str, Any]
```

**Returns:** Dict containing:
- `base_type`: Base type name
- `parameters`: Type parameters
- `is_numeric`: Boolean indicating if numeric type
- `is_string`: Boolean indicating if string type
- `is_date`: Boolean indicating if date type
- `valid`: Boolean indicating if valid type

### Validation Utilities

#### is_valid_mapping_name

Check if a mapping name follows valid naming conventions.

```python
def is_valid_mapping_name(name: str) -> bool
```

#### sanitize_mapping_name

Sanitize a mapping name to follow valid conventions.

```python
def sanitize_mapping_name(name: str) -> str
```

#### get_column_name_suggestions

Get column name suggestions based on similarity.

```python
def get_column_name_suggestions(available_columns: List[str], target_column: str, 
                              max_suggestions: int = 3) -> List[str]
```

### Library Information

#### get_library_stats

Get statistics about the library capabilities.

```python
def get_library_stats() -> Dict[str, Any]
```

**Returns:** Dict containing:
- `total_operations`: Number of available operations
- `categories`: List of operation categories
- `transformation_types`: Number of transformation types
- `supports_sql_expressions`: Boolean
- `supports_comprehensive_validation`: Boolean
- `version`: Library version

## 📋 Operation Registry

### ParameterType

Enum for parameter types.

```python
class ParameterType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
```

### ParameterSpec

Specification for operation parameters.

```python
class ParameterSpec:
    def __init__(self, type: ParameterType, required: bool = False, 
                 description: str = "", allowed_values: List = None, 
                 default_value: Any = None)
```

**Properties:**
- `type`: Parameter type (ParameterType enum)
- `required`: Whether parameter is required
- `description`: Parameter description
- `allowed_values`: List of allowed values (optional)
- `default_value`: Default value (optional)

### OperationSpec

Specification for operations.

```python
class OperationSpec:
    def __init__(self, name: str, category: str, description: str,
                 parameters: Dict[str, ParameterSpec] = None, 
                 examples: List[str] = None)
```

**Properties:**
- `name`: Operation name
- `category`: Operation category
- `description`: Operation description
- `parameters`: Dict of parameter specifications
- `examples`: List of usage examples

### OperationRegistry

Registry for managing operations.

```python
class OperationRegistry:
    def __init__(self)
```

**Methods:**
- `register_operation(operation_spec: OperationSpec)`: Register a new operation
- `get_operation(name: str) -> OperationSpec`: Get operation by name
- `get_operations_by_category(category: str) -> List[OperationSpec]`: Get operations by category
- `get_all_operation_names() -> List[str]`: Get all operation names
- `get_operation_help(operation_name: str) -> Dict[str, Any]`: Get operation help
- `get_operation_suggestions(partial_name: str) -> List[str]`: Get operation suggestions

### OPERATION_REGISTRY

Global operation registry instance containing 20+ predefined operations across 6 categories:

- **String Operations**: trim, upper_case, lower_case, substring, concatenate, replace_text
- **Numeric Operations**: add, subtract, multiply, divide, round_number, absolute_value
- **Date Operations**: format_date, parse_date, date_add, date_diff, extract_date_part
- **Type Conversion**: to_string, to_integer, to_float, to_boolean
- **Conditional Operations**: if_null, case_when
- **Mathematical Operations**: power, square_root

## 🔧 Logging System

### LoggerAdapter

Abstract base class for logger adapters.

```python
class LoggerAdapter(ABC):
    def __init__(self, logger, component_name: str = "GDX-Validator")
```

**Abstract Methods:**
- `_log(level: str, message: str)`: Log message at specified level

**Methods:**
- `info(message: str)`: Log info message
- `warning(message: str)`: Log warning message
- `error(message: str)`: Log error message
- `debug(message: str)`: Log debug message

### Available Logger Adapters

#### StandardLoggerAdapter
For Python standard library loggers.

#### GlueLoggerAdapter
For AWS Glue framework loggers.

#### SilentLoggerAdapter
For silent operation (no logging).

#### ConsoleLoggerAdapter
For console-only logging.

### LoggerFactory

#### get_logger

Factory function to get appropriate logger adapter.

```python
def get_logger(external_logger=None, component_name: str = "GDX-Validator", 
               silent: bool = False) -> LoggerAdapter
```

**Parameters:**
- `external_logger`: External logger instance
- `component_name`: Component name for logging
- `silent`: Force silent logging

**Returns:** Appropriate LoggerAdapter instance

The logger factory automatically detects the type of external logger and returns the appropriate adapter, supporting:
- Standard Python loggers
- AWS Glue loggers (duck typing)
- Custom framework loggers
- Silent operation
- Console-only logging

This API reference provides complete documentation for all public interfaces in the GDX Config Validator Library.