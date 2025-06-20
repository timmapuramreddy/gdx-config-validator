# Developer Guide - GDX Config Validator Library

A comprehensive guide for developers to maintain, enhance, and extend the GDX Config Validator Library.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Adding New Validation Rules](#adding-new-validation-rules)
3. [Extending Operation Registry](#extending-operation-registry)
4. [Creating Custom Validators](#creating-custom-validators)
5. [Enhancing Logging System](#enhancing-logging-system)
6. [Testing Guidelines](#testing-guidelines)
7. [Performance Optimization](#performance-optimization)
8. [Maintenance Best Practices](#maintenance-best-practices)

## 🏗️ Architecture Overview

### Core Design Principles

1. **Modular Architecture**: Each component has a single responsibility
2. **Extensibility**: Easy to add new validators, rules, and operations
3. **Backward Compatibility**: Changes don't break existing code
4. **Performance**: Optimized for production use with minimal overhead
5. **Logging Flexibility**: Adapts to different logging frameworks

### Component Relationships

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Factory       │───▶│   Validators     │───▶│   Core Base     │
│   (factory.py)  │    │  (validators.py) │    │   (core.py)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Results       │    │   Operations     │    │   Logging       │
│  (results.py)   │    │ (operations.py)  │    │(logging_adapter)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### File Structure Deep Dive

```
src/gdx_config_validator/
├── __init__.py              # Public API exports and version info
├── results.py               # ValidationResult system (400+ lines)
├── core.py                  # BaseValidator infrastructure (800+ lines)
├── schemas/
│   └── operations.py        # Operation registry (500+ lines, 20+ operations)
├── validators.py            # All validator implementations (3,300+ lines)
├── logging_adapter.py       # Enhanced logging system (400+ lines)
├── config.py               # Configuration management (200+ lines)
├── parsers.py              # YAML parsing utilities (300+ lines)
├── utils.py                # Helper functions (400+ lines)
└── factory.py              # Factory pattern (450+ lines)
```

## ✨ Adding New Validation Rules

### Step 1: Understanding the Rule Engine

The `ValidationRuleEngine` in `core.py` provides a pluggable system for validation rules:

```python
class ValidationRuleEngine:
    def register_rule(self, rule_name, rule_function, description, severity, categories):
        """Register a new validation rule"""
        pass
    
    def execute_rules(self, context, categories=None):
        """Execute rules by category"""
        pass
```

### Step 2: Creating a New Validation Rule

#### Example: Adding a "Naming Convention" Rule

1. **Define the rule function** in your validator class:

```python
def _validate_naming_convention_rule(self, context: ValidationContext) -> List[Dict]:
    """
    Validate that mapping names follow naming conventions
    
    Args:
        context: ValidationContext with config data
        
    Returns:
        List of validation errors
    """
    errors = []
    config = context.config_data
    
    if 'mappings' not in config:
        return errors
    
    # Define naming pattern (example: lowercase with underscores)
    import re
    valid_pattern = re.compile(r'^[a-z][a-z0-9_]*$')
    
    for i, mapping in enumerate(config['mappings']):
        mapping_name = mapping.get('mapping_name', '')
        
        if not mapping_name:
            errors.append({
                'type': 'missing_mapping_name',
                'message': 'Mapping name is required',
                'severity': 'error',
                'path': f'mappings[{i}].mapping_name'
            })
        elif not valid_pattern.match(mapping_name):
            errors.append({
                'type': 'invalid_naming_convention',
                'message': f'Mapping name "{mapping_name}" must be lowercase with underscores only',
                'severity': 'warning',
                'path': f'mappings[{i}].mapping_name',
                'suggestion': f'Consider renaming to: {mapping_name.lower().replace("-", "_")}'
            })
    
    return errors
```

2. **Register the rule** in your validator's `_register_validation_rules()` method:

```python
def _register_validation_rules(self):
    # ... existing rules ...
    
    # Register naming convention rule
    self.rule_engine.register_rule(
        'validate_naming_convention',
        self._validate_naming_convention_rule,
        'Validate mapping naming conventions',
        ValidationSeverity.WARNING,
        ['naming', 'conventions', 'best_practices']
    )
```

3. **Execute rules by category** in validation methods:

```python
def validate_comprehensive(self, config_data):
    context = ValidationContext(config_data)
    builder = ValidationResultBuilder()
    
    # Execute all naming and convention rules
    naming_errors = self.rule_engine.execute_rules(
        context, 
        categories=['naming', 'conventions']
    )
    
    for error in naming_errors:
        builder.add_error(**error)
    
    return builder.build()
```

### Step 3: Adding Complex Validation Rules

#### Example: Cross-Reference Validation Rule

```python
def _validate_column_references_rule(self, context: ValidationContext) -> List[Dict]:
    """
    Validate that all column references are consistent across sections
    """
    errors = []
    config = context.config_data
    
    for i, mapping in enumerate(config.get('mappings', [])):
        # Extract available columns from source_columns_interested
        source_columns = set()
        for col_expr in mapping.get('source_columns_interested', []):
            # Extract alias from expressions like 'table.column as alias'
            alias = self._extract_column_alias(col_expr)
            if alias:
                source_columns.add(alias)
        
        # Check column transformations
        for j, transform in enumerate(mapping.get('column_transformations', [])):
            source_alias = transform.get('source_alias')
            if source_alias and source_alias not in source_columns:
                errors.append({
                    'type': 'undefined_column_reference',
                    'message': f'Column "{source_alias}" referenced in transformation but not defined in source_columns_interested',
                    'severity': 'error',
                    'path': f'mappings[{i}].column_transformations[{j}].source_alias',
                    'available_columns': list(source_columns),
                    'suggestion': f'Add "{source_alias}" to source_columns_interested or use one of: {list(source_columns)[:3]}'
                })
    
    return errors

def _extract_column_alias(self, column_expression: str) -> str:
    """Extract alias from SQL column expression"""
    import re
    # Match patterns like 'table.column as alias' or 'expression AS alias'
    alias_match = re.search(r'\\s+as\\s+([\\w_]+)\\s*$', column_expression, re.IGNORECASE)
    if alias_match:
        return alias_match.group(1)
    
    # Handle simple column names
    simple_match = re.search(r'([\\w_]+)\\s*$', column_expression)
    if simple_match:
        return simple_match.group(1)
    
    return None
```

## 🔧 Extending Operation Registry

### Step 1: Understanding Operation Structure

Operations are defined in `schemas/operations.py` using these classes:

```python
class ParameterSpec:
    type: ParameterType          # STRING, INTEGER, FLOAT, etc.
    required: bool               # Is parameter required?
    description: str             # Parameter description
    allowed_values: List[Any]    # Optional: allowed values
    default_value: Any           # Optional: default value

class OperationSpec:
    name: str                    # Operation name
    category: str                # Category (string, numeric, date, etc.)
    description: str             # What the operation does
    parameters: Dict[str, ParameterSpec]  # Parameters
    examples: List[str]          # Usage examples
```

### Step 2: Adding New Operations

#### Example: Adding a "Phone Number Formatting" Operation

```python
from gdx_config_validator.schemas.operations import OPERATION_REGISTRY, OperationSpec, ParameterSpec, ParameterType

# Define the new operation
phone_format_operation = OperationSpec(
    name="format_phone_number",
    category="formatting",
    description="Format phone numbers to a specific pattern",
    parameters={
        "format_pattern": ParameterSpec(
            type=ParameterType.STRING,
            required=True,
            description="Phone number format pattern (e.g., '(###) ###-####')",
            allowed_values=["(###) ###-####", "###-###-####", "+1-###-###-####"],
            default_value="(###) ###-####"
        ),
        "country_code": ParameterSpec(
            type=ParameterType.STRING,
            required=False,
            description="Country code to add if missing",
            default_value="+1"
        ),
        "remove_invalid": ParameterSpec(
            type=ParameterType.BOOLEAN,
            required=False,
            description="Remove invalid phone numbers instead of erroring",
            default_value=False
        )
    },
    examples=[
        "format_phone_number(format_pattern='(###) ###-####')",
        "format_phone_number(format_pattern='###-###-####', country_code='+1')",
        "format_phone_number(format_pattern='+1-###-###-####', remove_invalid=true)"
    ]
)

# Register the operation
OPERATION_REGISTRY.register_operation(phone_format_operation)
```

#### Example: Adding a "Data Quality Score" Operation

```python
data_quality_operation = OperationSpec(
    name="calculate_data_quality_score",
    category="data_quality",
    description="Calculate data quality score based on completeness and validity rules",
    parameters={
        "completeness_weight": ParameterSpec(
            type=ParameterType.FLOAT,
            required=False,
            description="Weight for completeness in final score (0.0-1.0)",
            default_value=0.5
        ),
        "validity_rules": ParameterSpec(
            type=ParameterType.LIST,
            required=True,
            description="List of validity rules to apply",
        ),
        "min_score_threshold": ParameterSpec(
            type=ParameterType.FLOAT,
            required=False,
            description="Minimum score threshold for acceptance",
            default_value=0.8
        )
    },
    examples=[
        "calculate_data_quality_score(validity_rules=['not_null', 'email_format'])",
        "calculate_data_quality_score(completeness_weight=0.7, validity_rules=['not_null', 'phone_format'], min_score_threshold=0.9)"
    ]
)

OPERATION_REGISTRY.register_operation(data_quality_operation)
```

### Step 3: Adding New Operation Categories

```python
# Add new category operations in bulk
financial_operations = [
    OperationSpec(
        name="calculate_compound_interest",
        category="financial",
        description="Calculate compound interest",
        parameters={
            "principal": ParameterSpec(ParameterType.FLOAT, True, "Principal amount"),
            "rate": ParameterSpec(ParameterType.FLOAT, True, "Interest rate (decimal)"),
            "time": ParameterSpec(ParameterType.FLOAT, True, "Time period"),
            "frequency": ParameterSpec(ParameterType.INTEGER, False, "Compounding frequency", default_value=12)
        },
        examples=["calculate_compound_interest(principal=${amount}, rate=0.05, time=2, frequency=12)"]
    ),
    
    OperationSpec(
        name="calculate_loan_payment",
        category="financial",
        description="Calculate monthly loan payment",
        parameters={
            "principal": ParameterSpec(ParameterType.FLOAT, True, "Loan principal"),
            "rate": ParameterSpec(ParameterType.FLOAT, True, "Annual interest rate"),
            "months": ParameterSpec(ParameterType.INTEGER, True, "Loan term in months")
        },
        examples=["calculate_loan_payment(principal=${loan_amount}, rate=0.045, months=360)"]
    )
]

# Register all financial operations
for operation in financial_operations:
    OPERATION_REGISTRY.register_operation(operation)
```

### Step 4: Operation Validation Enhancement

Add custom validation for new operations in `utils.py`:

```python
def validate_financial_operation_parameters(operation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Custom validation for financial operations
    """
    result = validate_operation_parameters(operation_type, parameters)
    
    if operation_type == "calculate_compound_interest":
        rate = parameters.get('rate', 0)
        if rate < 0 or rate > 1:
            result['errors'].append("Interest rate must be between 0 and 1 (decimal format)")
        
        time = parameters.get('time', 0)
        if time <= 0:
            result['errors'].append("Time period must be positive")
    
    elif operation_type == "calculate_loan_payment":
        principal = parameters.get('principal', 0)
        if principal <= 0:
            result['errors'].append("Principal amount must be positive")
    
    return result
```

## 🏗️ Creating Custom Validators

### Step 1: Basic Custom Validator

```python
from gdx_config_validator import BaseValidator, ValidationResultBuilder, ValidationContext

class CustomBusinessRuleValidator(BaseValidator):
    """
    Custom validator for business-specific rules
    """
    
    def __init__(self, logger=None, business_rules_config: Dict = None):
        super().__init__(logger, "CustomBusinessRuleValidator")
        self.business_rules = business_rules_config or {}
        self._register_business_rules()
    
    def _register_business_rules(self):
        """Register custom business validation rules"""
        
        self.rule_engine.register_rule(
            'validate_business_constraints',
            self._validate_business_constraints_rule,
            'Validate business-specific constraints',
            ValidationSeverity.ERROR,
            ['business', 'constraints']
        )
        
        self.rule_engine.register_rule(
            'validate_data_retention_policy',
            self._validate_data_retention_rule,
            'Validate data retention policies',
            ValidationSeverity.WARNING,
            ['business', 'compliance']
        )
    
    def validate(self, config_data: Dict[str, Any]) -> ValidationResult:
        """
        Main validation method
        """
        context = ValidationContext(config_data)
        builder = ValidationResultBuilder()
        
        # Execute business rule validations
        business_errors = self.rule_engine.execute_rules(
            context, 
            categories=['business']
        )
        
        for error in business_errors:
            if error.get('severity') == 'error':
                builder.add_error(**error)
            else:
                builder.add_warning(**error)
        
        return builder.build()
    
    def _validate_business_constraints_rule(self, context: ValidationContext) -> List[Dict]:
        """
        Validate business-specific constraints
        """
        errors = []
        config = context.config_data
        
        # Example: Validate that certain tables are not used together
        forbidden_combinations = self.business_rules.get('forbidden_table_combinations', [])
        
        for mapping in config.get('mappings', []):
            source_table = mapping.get('source_table', '').lower()
            target_table = mapping.get('target_table', '').lower()
            
            for forbidden_combo in forbidden_combinations:
                if (source_table in forbidden_combo and target_table in forbidden_combo):
                    errors.append({
                        'type': 'forbidden_table_combination',
                        'message': f'Tables {source_table} and {target_table} cannot be used together per business rules',
                        'severity': 'error',
                        'path': f'mapping: {mapping.get("mapping_name", "unnamed")}',
                        'business_rule': forbidden_combo
                    })
        
        return errors
    
    def _validate_data_retention_rule(self, context: ValidationContext) -> List[Dict]:
        """
        Validate data retention policies
        """
        warnings = []
        config = context.config_data
        
        max_retention_days = self.business_rules.get('max_retention_days', 2555)  # 7 years
        
        for mapping in config.get('mappings', []):
            # Check if partition settings might exceed retention policy
            if 'partition_upperbound' in mapping:
                # This is a simplified check - in reality you'd parse the date
                warnings.append({
                    'type': 'potential_retention_violation',
                    'message': f'Partition upper bound may exceed data retention policy of {max_retention_days} days',
                    'severity': 'warning',
                    'path': f'mappings.{mapping.get("mapping_name")}.partition_upperbound',
                    'recommendation': 'Review partition bounds against data retention policy'
                })
        
        return warnings
```

### Step 2: Integrating Custom Validator with Factory

```python
# Add to factory.py
class ValidatorType:
    # ... existing types ...
    BUSINESS_RULES = "business_rules"

def create_validator(validator_type: str = ValidatorType.COMPREHENSIVE, 
                    logger=None, silent: bool = False, **kwargs) -> Any:
    # ... existing validator creation ...
    
    elif validator_type == ValidatorType.BUSINESS_RULES:
        business_config = kwargs.get('business_rules_config', {})
        return CustomBusinessRuleValidator(
            logger=logger, 
            business_rules_config=business_config
        )
```

### Step 3: Advanced Validator with Plugin System

```python
class PluggableValidator(BaseValidator):
    """
    Validator that supports plugins for extensibility
    """
    
    def __init__(self, logger=None):
        super().__init__(logger, "PluggableValidator")
        self.plugins = []
        self._load_default_plugins()
    
    def register_plugin(self, plugin_instance):
        """Register a validation plugin"""
        if hasattr(plugin_instance, 'validate_config'):
            self.plugins.append(plugin_instance)
            self.log_info(f"Registered plugin: {plugin_instance.__class__.__name__}")
        else:
            raise ValueError("Plugin must implement validate_config method")
    
    def validate(self, config_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate using all registered plugins
        """
        builder = ValidationResultBuilder()
        
        for plugin in self.plugins:
            try:
                plugin_result = plugin.validate_config(config_data)
                
                # Merge plugin results
                if hasattr(plugin_result, 'errors'):
                    for error in plugin_result.errors:
                        builder.add_error(**error)
                
                if hasattr(plugin_result, 'warnings'):
                    for warning in plugin_result.warnings:
                        builder.add_warning(**warning)
                        
            except Exception as e:
                builder.add_error(
                    'plugin_validation_error',
                    f'Plugin {plugin.__class__.__name__} failed: {str(e)}',
                    severity='warning'
                )
        
        return builder.build()
    
    def _load_default_plugins(self):
        """Load default validation plugins"""
        # This could load plugins from a configuration file
        # or discover them automatically
        pass

# Example plugin
class SecurityValidationPlugin:
    """Plugin for security-related validations"""
    
    def validate_config(self, config_data: Dict[str, Any]) -> ValidationResult:
        builder = ValidationResultBuilder()
        
        # Check for potential security issues
        for mapping in config_data.get('mappings', []):
            # Example: Check for SQL injection risks in where clauses
            where_clause = mapping.get('where_clause', '')
            if self._has_sql_injection_risk(where_clause):
                builder.add_error(
                    'potential_sql_injection',
                    'Where clause may contain SQL injection risk',
                    path=f'mappings.{mapping.get("mapping_name")}.where_clause',
                    severity='critical'
                )
        
        return builder.build()
    
    def _has_sql_injection_risk(self, sql_clause: str) -> bool:
        """Basic SQL injection detection"""
        if not sql_clause:
            return False
        
        # Simple patterns that might indicate SQL injection
        dangerous_patterns = [
            r"';.*--",          # Comment injection
            r"union\s+select",  # Union injection
            r"drop\s+table",    # Drop table
            r"exec\s*\(",       # Exec function
        ]
        
        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, sql_clause, re.IGNORECASE):
                return True
        
        return False
```

## 📊 Enhancing Logging System

### Step 1: Adding New Logger Adapters

```python
# Add to logging_adapter.py
class CustomFrameworkLoggerAdapter(LoggerAdapter):
    """
    Adapter for custom framework loggers
    """
    
    def __init__(self, logger, component_name: str = "GDX-Validator"):
        super().__init__(logger, component_name)
        self.framework_logger = logger
    
    def _log(self, level: str, message: str):
        """Route to custom framework logger methods"""
        if hasattr(self.framework_logger, 'log_message'):
            self.framework_logger.log_message(level.upper(), f"[{self.component_name}] {message}")
        elif hasattr(self.framework_logger, 'write_log'):
            self.framework_logger.write_log(f"{level.upper()}: [{self.component_name}] {message}")
        else:
            # Fallback to standard methods
            super()._log(level, message)

class DatabaseLoggerAdapter(LoggerAdapter):
    """
    Adapter that logs to database
    """
    
    def __init__(self, db_connection, component_name: str = "GDX-Validator"):
        super().__init__(None, component_name)
        self.db_connection = db_connection
    
    def _log(self, level: str, message: str):
        """Log to database table"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "INSERT INTO validation_logs (timestamp, level, component, message) VALUES (?, ?, ?, ?)",
                (datetime.now(), level.upper(), self.component_name, message)
            )
            self.db_connection.commit()
        except Exception as e:
            # Fallback to console if database logging fails
            print(f"DB Log Error: {e}")
            print(f"{level.upper()}: [{self.component_name}] {message}")
```

### Step 2: Enhanced Logger Factory

```python
# Update get_logger function in logging_adapter.py
def get_logger(external_logger=None, component_name: str = "GDX-Validator", 
               silent: bool = False, logger_type: str = "auto") -> LoggerAdapter:
    """
    Enhanced logger factory with explicit logger type selection
    """
    if silent:
        return SilentLoggerAdapter(component_name)
    
    if external_logger is None:
        return _get_default_logger(component_name)
    
    # Explicit logger type selection
    if logger_type == "database" and hasattr(external_logger, 'cursor'):
        return DatabaseLoggerAdapter(external_logger, component_name)
    elif logger_type == "custom_framework":
        return CustomFrameworkLoggerAdapter(external_logger, component_name)
    
    # Auto-detection (existing logic)
    logger_type_name = type(external_logger).__name__.lower()
    
    if 'glue' in logger_type_name or hasattr(external_logger, 'log_to_driver'):
        return GlueLoggerAdapter(external_logger, component_name)
    elif hasattr(external_logger, 'log_message'):
        return CustomFrameworkLoggerAdapter(external_logger, component_name)
    else:
        return StandardLoggerAdapter(external_logger, component_name)
```

## 🧪 Testing Guidelines

### Step 1: Test Structure

```
tests/
├── unit/
│   ├── test_validators.py
│   ├── test_operations.py
│   ├── test_logging.py
│   └── test_factory.py
├── integration/
│   ├── test_full_validation.py
│   └── test_yaml_files/
└── performance/
    └── test_performance.py
```

### Step 2: Unit Test Examples

```python
# tests/unit/test_custom_validators.py
import pytest
from gdx_config_validator import ValidationResultBuilder
from your_custom_validators import CustomBusinessRuleValidator

class TestCustomBusinessRuleValidator:
    
    def setup_method(self):
        """Setup for each test method"""
        self.business_rules = {
            'forbidden_table_combinations': [
                ['sensitive_table', 'public_table']
            ],
            'max_retention_days': 2555
        }
        self.validator = CustomBusinessRuleValidator(
            business_rules_config=self.business_rules
        )
    
    def test_forbidden_table_combination_detection(self):
        """Test detection of forbidden table combinations"""
        config = {
            'mappings': [{
                'mapping_name': 'test_mapping',
                'source_table': 'sensitive_table',
                'target_table': 'public_table'
            }]
        }
        
        result = self.validator.validate(config)
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0]['type'] == 'forbidden_table_combination'
    
    def test_allowed_table_combination(self):
        """Test that allowed combinations pass validation"""
        config = {
            'mappings': [{
                'mapping_name': 'test_mapping',
                'source_table': 'allowed_source',
                'target_table': 'allowed_target'
            }]
        }
        
        result = self.validator.validate(config)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    @pytest.mark.parametrize("source,target,should_fail", [
        ('sensitive_table', 'public_table', True),
        ('public_table', 'sensitive_table', True),
        ('allowed_source', 'allowed_target', False),
    ])
    def test_table_combinations(self, source, target, should_fail):
        """Parameterized test for various table combinations"""
        config = {
            'mappings': [{
                'mapping_name': 'test_mapping',
                'source_table': source,
                'target_table': target
            }]
        }
        
        result = self.validator.validate(config)
        
        if should_fail:
            assert not result.is_valid
        else:
            assert result.is_valid
```

### Step 3: Integration Test Example

```python
# tests/integration/test_full_validation.py
import pytest
from pathlib import Path
from gdx_config_validator import validate_file, ValidatorType

class TestFullValidationWorkflow:
    
    def setup_class(self):
        """Setup test YAML files"""
        self.test_yaml_dir = Path(__file__).parent / "test_yaml_files"
        self.test_yaml_dir.mkdir(exist_ok=True)
        
        # Create test YAML files
        self._create_valid_config()
        self._create_invalid_config()
    
    def _create_valid_config(self):
        """Create a valid test configuration"""
        valid_config = '''
settings:
  env: test
  load: full

mappings:
  - mapping_name: test_mapping
    source_table: source_test
    target_table: target_test
    source_columns_interested:
      - "id as test_id"
      - "name as test_name"
    column_transformations:
      - source_alias: test_name
        target_column: processed_name
        data_type: VARCHAR(100)
        transformation_type: string_manipulation
'''
        with open(self.test_yaml_dir / "valid_config.yaml", "w") as f:
            f.write(valid_config)
    
    def _create_invalid_config(self):
        """Create an invalid test configuration"""
        invalid_config = '''
settings:
  env: test

mappings:
  - mapping_name: test_mapping
    source_table: source_test
    target_table: target_test
    source_columns_interested:
      - "id as test_id"
    column_transformations:
      - source_alias: missing_column  # This column is not in source_columns_interested
        target_column: processed_name
        data_type: VARCHAR(100)
        transformation_type: string_manipulation
'''
        with open(self.test_yaml_dir / "invalid_config.yaml", "w") as f:
            f.write(invalid_config)
    
    def test_valid_config_validation(self):
        """Test validation of valid configuration"""
        result = validate_file(
            self.test_yaml_dir / "valid_config.yaml",
            ValidatorType.COMPREHENSIVE
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_invalid_config_validation(self):
        """Test validation of invalid configuration"""
        result = validate_file(
            self.test_yaml_dir / "invalid_config.yaml",
            ValidatorType.COMPREHENSIVE
        )
        
        assert not result.is_valid
        assert len(result.errors) > 0
        
        # Check that the specific error is detected
        error_types = [error.get('type') for error in result.errors]
        assert 'orphaned_transformation_columns' in error_types
```

### Step 4: Performance Test Example

```python
# tests/performance/test_performance.py
import time
import pytest
from gdx_config_validator import validate_file, ValidatorType, configure_for_testing

class TestPerformance:
    
    def setup_method(self):
        """Setup for performance tests"""
        configure_for_testing()  # Silent mode for performance testing
    
    def test_large_config_validation_performance(self):
        """Test performance with large configuration file"""
        # Generate large config
        large_config = self._generate_large_config(num_mappings=100)
        
        start_time = time.time()
        result = validate_file(large_config, ValidatorType.COMPREHENSIVE)
        end_time = time.time()
        
        validation_time = end_time - start_time
        
        # Performance assertions
        assert validation_time < 5.0  # Should complete within 5 seconds
        assert result is not None
        
        print(f"Validation of 100 mappings took {validation_time:.2f} seconds")
    
    def _generate_large_config(self, num_mappings: int) -> str:
        """Generate a large test configuration"""
        mappings = []
        for i in range(num_mappings):
            mapping = f'''
  - mapping_name: test_mapping_{i}
    source_table: source_table_{i}
    target_table: target_table_{i}
    source_columns_interested:
      - "id as test_id_{i}"
      - "name as test_name_{i}"
    column_transformations:
      - source_alias: test_name_{i}
        target_column: processed_name_{i}
        data_type: VARCHAR(100)
        transformation_type: string_manipulation'''
            mappings.append(mapping)
        
        config = f'''
settings:
  env: test
  load: full

mappings:{chr(10).join(mappings)}
'''
        
        # Write to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config)
            return f.name
    
    @pytest.mark.benchmark
    def test_validation_benchmark(self, benchmark):
        """Benchmark validation performance using pytest-benchmark"""
        config_path = self._generate_large_config(50)
        
        def validate_config():
            return validate_file(config_path, ValidatorType.COMPREHENSIVE)
        
        result = benchmark(validate_config)
        assert result is not None
```

## ⚡ Performance Optimization

### Step 1: Caching Strategies

```python
# Add to core.py
class CachedValidator(BaseValidator):
    """
    Validator with caching for improved performance
    """
    
    def __init__(self, logger=None, cache_size: int = 100):
        super().__init__(logger, "CachedValidator")
        self.cache = {}
        self.cache_size = cache_size
        self.cache_hits = 0
        self.cache_misses = 0
    
    def validate_with_cache(self, config_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate with caching based on config hash
        """
        config_hash = self._calculate_config_hash(config_data)
        
        if config_hash in self.cache:
            self.cache_hits += 1
            self.log_debug(f"Cache hit for config hash: {config_hash}")
            return self.cache[config_hash]
        
        self.cache_misses += 1
        self.log_debug(f"Cache miss for config hash: {config_hash}")
        
        # Perform actual validation
        result = self.validate(config_data)
        
        # Store in cache (with size limit)
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[config_hash] = result
        return result
    
    def _calculate_config_hash(self, config_data: Dict[str, Any]) -> str:
        """Calculate hash of configuration for caching"""
        import hashlib
        import json
        
        # Convert to JSON and hash
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache)
        }
```

### Step 2: Parallel Validation

```python
# Add to factory.py
def validate_directory_parallel(directory_path: Union[str, Path],
                               pattern: str = "*.yaml",
                               validator_type: str = ValidatorType.COMPREHENSIVE,
                               max_workers: int = None,
                               logger=None) -> Dict[str, ValidationResult]:
    """
    Validate directory with parallel processing
    """
    import concurrent.futures
    from pathlib import Path
    
    directory_path = Path(directory_path)
    results = {}
    
    if not directory_path.exists() or not directory_path.is_dir():
        return results
    
    # Find all matching files
    files_to_validate = list(directory_path.glob(pattern))
    
    def validate_single_file(file_path):
        """Validate a single file"""
        try:
            return str(file_path), validate_file(file_path, validator_type, logger, silent=True)
        except Exception as e:
            from .results import create_exception_result
            return str(file_path), create_exception_result(e, context=str(file_path))
    
    # Use ThreadPoolExecutor for I/O bound validation
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(validate_single_file, file_path): file_path 
            for file_path in files_to_validate
        }
        
        for future in concurrent.futures.as_completed(future_to_file):
            file_path, result = future.result()
            results[file_path] = result
    
    return results
```

## 🛠️ Maintenance Best Practices

### Step 1: Version Management

```python
# Update __init__.py for version management
__version__ = "1.1.0"
__api_version__ = "1.0"  # API compatibility version

def check_compatibility(required_version: str) -> bool:
    """
    Check if current version is compatible with required version
    """
    from packaging import version
    return version.parse(__api_version__) >= version.parse(required_version)

class VersionInfo:
    """Version information helper"""
    
    @staticmethod
    def get_full_info():
        return {
            'version': __version__,
            'api_version': __api_version__,
            'python_version': sys.version,
            'dependencies': {
                'pyyaml': yaml.__version__ if hasattr(yaml, '__version__') else 'unknown'
            }
        }
```

### Step 2: Deprecation Management

```python
# Add to core.py
import warnings
from functools import wraps

def deprecated(reason: str, version: str = None):
    """
    Decorator to mark functions as deprecated
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warning_msg = f"Function {func.__name__} is deprecated"
            if reason:
                warning_msg += f": {reason}"
            if version:
                warning_msg += f" (deprecated since version {version})"
            
            warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Example usage
@deprecated("Use validate_comprehensive instead", "1.1.0")
def old_validation_method(config):
    """Legacy validation method"""
    pass
```

### Step 3: Configuration Management

```python
# Add to config.py
class LibraryConfig:
    """
    Central configuration management for the library
    """
    
    def __init__(self):
        self.settings = {
            'default_validator_type': ValidatorType.COMPREHENSIVE,
            'max_cache_size': 100,
            'enable_performance_logging': False,
            'validation_timeout': 300,  # 5 minutes
            'max_file_size_mb': 50
        }
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.settings[key] = value
    
    def load_from_file(self, config_file: str):
        """Load configuration from file"""
        import json
        with open(config_file, 'r') as f:
            file_config = json.load(f)
            self.settings.update(file_config)
    
    def save_to_file(self, config_file: str):
        """Save configuration to file"""
        import json
        with open(config_file, 'w') as f:
            json.dump(self.settings, f, indent=2)

# Global configuration instance
config = LibraryConfig()
```

### Step 4: Monitoring and Metrics

```python
# Add to core.py
class ValidationMetrics:
    """
    Enhanced metrics collection for monitoring
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics"""
        self.metrics = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'avg_validation_time': 0.0,
            'validator_type_usage': {},
            'error_types': {},
            'start_time': time.time()
        }
    
    def record_validation(self, validator_type: str, result: ValidationResult, 
                         duration: float):
        """Record validation metrics"""
        self.metrics['total_validations'] += 1
        
        if result.is_valid:
            self.metrics['successful_validations'] += 1
        else:
            self.metrics['failed_validations'] += 1
        
        self.metrics['total_errors'] += len(result.errors)
        self.metrics['total_warnings'] += len(result.warnings)
        
        # Update average validation time
        total_time = (self.metrics['avg_validation_time'] * 
                     (self.metrics['total_validations'] - 1) + duration)
        self.metrics['avg_validation_time'] = total_time / self.metrics['total_validations']
        
        # Track validator type usage
        self.metrics['validator_type_usage'][validator_type] = (
            self.metrics['validator_type_usage'].get(validator_type, 0) + 1
        )
        
        # Track error types
        for error in result.errors:
            error_type = error.get('type', 'unknown')
            self.metrics['error_types'][error_type] = (
                self.metrics['error_types'].get(error_type, 0) + 1
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        uptime = time.time() - self.metrics['start_time']
        success_rate = (self.metrics['successful_validations'] / 
                       self.metrics['total_validations'] 
                       if self.metrics['total_validations'] > 0 else 0)
        
        return {
            **self.metrics,
            'uptime_seconds': uptime,
            'success_rate': success_rate,
            'validations_per_second': self.metrics['total_validations'] / uptime if uptime > 0 else 0
        }

# Global metrics instance
global_metrics = ValidationMetrics()
```

This comprehensive developer guide provides everything needed to maintain, enhance, and extend the GDX Config Validator Library. The modular architecture makes it easy to add new features while maintaining backward compatibility and performance.