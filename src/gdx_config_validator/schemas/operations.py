"""
Centralized operation registry with metadata for validation
This eliminates redundant operation validation logic

operation_registry.py with flexible parameter validation
This fixes the validation issues by supporting:
1. Mixed type parameters (e.g., default values can be string or number)
2. Column references as strings
3. SQL expressions in parameters
"""

"""
Enhanced operation_registry.py with flexible parameter validation
This fixes the validation issues by supporting:
1. Mixed type parameters (e.g., default values can be string or number)
2. Column references as strings
3. SQL expressions in parameters
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache


class ParameterType(Enum):
    """Parameter data types with enhanced flexibility"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    CHOICE = "choice"
    # NEW: Flexible types
    NUMBER = "number"  # int or float
    STRING_OR_NUMBER = "string_or_number"  # string, int, or float
    COLUMN_REFERENCE = "column_reference"  # string that can reference columns
    SQL_EXPRESSION = "sql_expression"  # string containing SQL


@dataclass
class ParameterSpec:
    """Enhanced specification for a parameter with flexible validation"""

    name: str
    param_type: ParameterType
    required: bool = False
    default: Any = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    description: str = ""
    validator: Optional[Callable] = None
    # NEW: Enhanced validation options
    allow_column_references: bool = False
    allow_sql_expressions: bool = False

    def validate(self, value: Any, path: str) -> List[Dict[str, Any]]:
        """Enhanced parameter validation with flexible type checking"""
        errors = []

        # Check if required parameter is missing
        if self.required and value is None:
            errors.append(
                {
                    "type": "missing_required_parameter",
                    "message": f"{self.name}: required parameter is missing",
                    "path": path,
                    "parameter": self.name,
                }
            )
            return errors

        # Skip validation if optional parameter is None
        if value is None:
            return errors

        # Enhanced type validation with flexibility
        if self.param_type == ParameterType.INTEGER:
            if not isinstance(value, int):
                errors.append(
                    {
                        "type": "invalid_parameter_type",
                        "message": f"{self.name}: must be integer, got {type(value).__name__}",
                        "path": path,
                        "parameter": self.name,
                        "expected_type": "integer",
                        "actual_type": type(value).__name__,
                    }
                )
                return errors

        elif self.param_type in [ParameterType.FLOAT, ParameterType.NUMBER]:
            # Combined: Both FLOAT and NUMBER accept int or float
            if not isinstance(value, (int, float)):
                errors.append(
                    {
                        "type": "invalid_parameter_type",
                        "message": f"{self.name}: must be number, got {type(value).__name__}",
                        "path": path,
                        "parameter": self.name,
                        "expected_type": "number",
                        "actual_type": type(value).__name__,
                    }
                )
                return errors

        elif self.param_type == ParameterType.STRING:
            if not isinstance(value, str):
                errors.append(
                    {
                        "type": "invalid_parameter_type",
                        "message": f"{self.name}: must be string, got {type(value).__name__}",
                        "path": path,
                        "parameter": self.name,
                        "expected_type": "string",
                        "actual_type": type(value).__name__,
                    }
                )
                return errors

        elif self.param_type == ParameterType.STRING_OR_NUMBER:
            # NEW: Accept string, int, or float
            if not isinstance(value, (str, int, float)):
                errors.append(
                    {
                        "type": "invalid_parameter_type",
                        "message": f"{self.name}: must be string or number, got {type(value).__name__}",
                        "path": path,
                        "parameter": self.name,
                        "expected_type": "string_or_number",
                        "actual_type": type(value).__name__,
                    }
                )
                return errors

        elif self.param_type == ParameterType.COLUMN_REFERENCE:
            # NEW: String that can reference columns or be a literal value
            if not isinstance(value, (str, int, float)):
                errors.append(
                    {
                        "type": "invalid_parameter_type",
                        "message": f"{self.name}: must be string (column reference) or number, got {type(value).__name__}",
                        "path": path,
                        "parameter": self.name,
                        "expected_type": "column_reference_or_number",
                        "actual_type": type(value).__name__,
                    }
                )
                return errors

        elif self.param_type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                errors.append(
                    {
                        "type": "invalid_parameter_type",
                        "message": f"{self.name}: must be boolean, got {type(value).__name__}",
                        "path": path,
                        "parameter": self.name,
                        "expected_type": "boolean",
                        "actual_type": type(value).__name__,
                    }
                )
                return errors

        # Range validation for numeric types (only if value is numeric)
        numeric_types = [
            ParameterType.INTEGER,
            ParameterType.FLOAT,
            ParameterType.NUMBER,
            ParameterType.STRING_OR_NUMBER,
            ParameterType.COLUMN_REFERENCE,
        ]

        if isinstance(value, (int, float)) and self.param_type in numeric_types:
            if self.min_value is not None and value < self.min_value:
                errors.append(
                    {
                        "type": "parameter_below_minimum",
                        "message": f"{self.name}: must be >= {self.min_value}, got {value}",
                        "path": path,
                        "parameter": self.name,
                        "min_value": self.min_value,
                        "actual_value": value,
                    }
                )

            if self.max_value is not None and value > self.max_value:
                errors.append(
                    {
                        "type": "parameter_above_maximum",
                        "message": f"{self.name}: must be <= {self.max_value}, got {value}",
                        "path": path,
                        "parameter": self.name,
                        "max_value": self.max_value,
                        "actual_value": value,
                    }
                )

        # Choice validation (only for non-column-reference strings)
        if self.choices and not (isinstance(value, str) and self.allow_column_references):
            if value not in self.choices:
                errors.append(
                    {
                        "type": "invalid_parameter_choice",
                        "message": f"{self.name}: must be one of {self.choices}, got {value}",
                        "path": path,
                        "parameter": self.name,
                        "valid_choices": self.choices,
                        "actual_value": value,
                    }
                )

        # Custom validator
        if self.validator:
            try:
                custom_errors = self.validator(value, path, self.name)
                if custom_errors:
                    errors.extend(custom_errors)
            except Exception as e:
                errors.append(
                    {
                        "type": "parameter_validation_error",
                        "message": f"{self.name}: validation error - {str(e)}",
                        "path": path,
                        "parameter": self.name,
                        "exception": str(e),
                    }
                )

        return errors


# Continue with OperationSpec and OperationRegistry classes...
@dataclass
class OperationSpec:
    """Specification for a transformation operation"""

    name: str
    category: str
    description: str
    parameters: List[ParameterSpec]
    examples: List[Dict[str, Any]] = None
    requires_column_reference: bool = False
    output_type_rules: Optional[Callable] = None

    def get_parameter(self, name: str) -> Optional[ParameterSpec]:
        """Get parameter specification by name"""
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def get_required_parameters(self) -> List[ParameterSpec]:
        """Get all required parameters"""
        return [p for p in self.parameters if p.required]

    def get_optional_parameters(self) -> List[ParameterSpec]:
        """Get all optional parameters"""
        return [p for p in self.parameters if not p.required]

    def validate_parameters(self, parameters: Dict[str, Any], path: str) -> List[Dict[str, Any]]:
        """Validate all parameters for this operation"""
        errors = []

        # Check for unknown parameters
        known_param_names = {p.name for p in self.parameters}
        for param_name in parameters.keys():
            if param_name not in known_param_names:
                errors.append(
                    {
                        "type": "unknown_parameter",
                        "message": f'{self.name}: unknown parameter "{param_name}"',
                        "path": path,
                        "operation": self.name,
                        "parameter": param_name,
                        "valid_parameters": list(known_param_names),
                    }
                )

        # Validate each known parameter
        for param_spec in self.parameters:
            value = parameters.get(param_spec.name)
            param_errors = param_spec.validate(value, path)
            errors.extend(param_errors)

        return errors


class OperationRegistry:
    """Enhanced registry with flexible parameter validation"""

    def __init__(self):
        self.operations: Dict[str, OperationSpec] = {}
        self.categories: Dict[str, List[str]] = {}
        self._initialize_operations()

    def _initialize_operations(self):
        """Initialize all operation specifications with enhanced flexibility"""

        # String operations
        self._add_string_operations()

        # Numeric operations with enhanced parameter types
        self._add_enhanced_numeric_operations()

        # Date/time operations
        self._add_datetime_operations()

        # Conditional operations
        self._add_conditional_operations()

        # Type conversion operations
        self._add_conversion_operations()

    def _add_enhanced_numeric_operations(self):
        """Add numeric operations with flexible parameter validation"""

        # Rounding modes
        rounding_modes = ["HALF_UP", "HALF_DOWN", "HALF_EVEN", "UP", "DOWN", "CEILING", "FLOOR"]

        # Round operation
        self.register_operation(
            OperationSpec(
                name="round",
                category="numeric",
                description="Round number to specified precision",
                parameters=[
                    ParameterSpec(
                        "precision",
                        ParameterType.INTEGER,
                        default=0,
                        min_value=0,
                        max_value=15,
                        description="Number of decimal places",
                    ),
                    ParameterSpec(
                        "mode",
                        ParameterType.CHOICE,
                        default="HALF_UP",
                        choices=rounding_modes,
                        description="Rounding mode",
                    ),
                ],
            )
        )

        # Arithmetic operations with FLEXIBLE parameters
        self.register_operation(
            OperationSpec(
                name="add",
                category="numeric",
                description="Add a value to the number",
                parameters=[
                    ParameterSpec(
                        "value",
                        ParameterType.COLUMN_REFERENCE,
                        required=True,
                        description="Value to add (can be number or column reference)",
                        allow_column_references=True,
                    )
                ],
            )
        )

        self.register_operation(
            OperationSpec(
                name="subtract",
                category="numeric",
                description="Subtract a value from the number",
                parameters=[
                    ParameterSpec(
                        "value",
                        ParameterType.COLUMN_REFERENCE,
                        required=True,
                        description="Value to subtract (can be number or column reference)",
                        allow_column_references=True,
                    )
                ],
            )
        )

        self.register_operation(
            OperationSpec(
                name="multiply",
                category="numeric",
                description="Multiply the number by a factor",
                parameters=[
                    ParameterSpec(
                        "factor",
                        ParameterType.COLUMN_REFERENCE,
                        required=True,
                        description="Multiplication factor (can be number or column reference)",
                        allow_column_references=True,
                    )
                ],
            )
        )

        # Division with enhanced validation
        def validate_divisor(value, path, param_name):
            # Only validate if it's a numeric value (not a column reference)
            if isinstance(value, (int, float)) and value == 0:
                return [
                    {
                        "type": "division_by_zero",
                        "message": "divide: factor cannot be zero (division by zero)",
                        "path": path,
                        "parameter": param_name,
                    }
                ]
            return []

        self.register_operation(
            OperationSpec(
                name="divide",
                category="numeric",
                description="Divide the number by a factor",
                parameters=[
                    ParameterSpec(
                        "factor",
                        ParameterType.COLUMN_REFERENCE,
                        required=True,
                        description="Division factor (can be number or column reference)",
                        validator=validate_divisor,
                        allow_column_references=True,
                    )
                ],
            )
        )

        # Parse currency with FLEXIBLE default_value
        self.register_operation(
            OperationSpec(
                name="parse_currency",
                category="numeric",
                description="Parse currency value from string",
                parameters=[
                    ParameterSpec(
                        "currency_symbol",
                        ParameterType.STRING,
                        required=False,
                        description="Currency symbol to remove",
                    ),
                    ParameterSpec(
                        "thousands_separator",
                        ParameterType.STRING,
                        default=",",
                        description="Thousands separator character",
                    ),
                    ParameterSpec(
                        "decimal_separator",
                        ParameterType.STRING,
                        default=".",
                        description="Decimal separator character",
                    ),
                    ParameterSpec(
                        "default_value",
                        ParameterType.STRING_OR_NUMBER,
                        default=0.0,
                        description="Default value if parsing fails (can be string or number)",
                    ),
                ],
            )
        )

        # Parse number operation
        self.register_operation(
            OperationSpec(
                name="parse_number",
                category="numeric",
                description="Parse number from string",
                parameters=[
                    ParameterSpec(
                        "default_value",
                        ParameterType.STRING_OR_NUMBER,
                        default=0,
                        description="Default value if parsing fails (can be string or number)",
                    ),
                    ParameterSpec(
                        "base",
                        ParameterType.INTEGER,
                        default=10,
                        min_value=2,
                        max_value=36,
                        description="Number base for parsing (2-36)",
                    ),
                    ParameterSpec(
                        "number_type",
                        ParameterType.CHOICE,
                        default="auto",
                        choices=["auto", "integer", "float", "decimal"],
                        description="Target number type",
                    ),
                ],
            )
        )

        # Add other numeric operations...
        self._add_remaining_numeric_operations()

    def _add_remaining_numeric_operations(self):
        """Add the remaining numeric operations"""

        # Ceil operation
        self.register_operation(
            OperationSpec(
                name="ceil",
                category="numeric",
                description="Round up to next integer or specified precision",
                parameters=[
                    ParameterSpec(
                        "precision",
                        ParameterType.INTEGER,
                        default=0,
                        min_value=0,
                        description="Decimal places for precision",
                    )
                ],
            )
        )

        # Floor operation
        self.register_operation(
            OperationSpec(
                name="floor",
                category="numeric",
                description="Round down to previous integer or specified precision",
                parameters=[
                    ParameterSpec(
                        "precision",
                        ParameterType.INTEGER,
                        default=0,
                        min_value=0,
                        description="Decimal places for precision",
                    )
                ],
            )
        )

        # Min/Max value operations with flexible parameters
        self.register_operation(
            OperationSpec(
                name="min_value",
                category="numeric",
                description="Ensure minimum value",
                parameters=[
                    ParameterSpec(
                        "min_value",
                        ParameterType.COLUMN_REFERENCE,
                        required=True,
                        description="Minimum allowed value (can be number or column reference)",
                        allow_column_references=True,
                    )
                ],
            )
        )

        self.register_operation(
            OperationSpec(
                name="max_value",
                category="numeric",
                description="Ensure maximum value",
                parameters=[
                    ParameterSpec(
                        "max_value",
                        ParameterType.COLUMN_REFERENCE,
                        required=True,
                        description="Maximum allowed value (can be number or column reference)",
                        allow_column_references=True,
                    )
                ],
            )
        )

        # Clamp operation
        self.register_operation(
            OperationSpec(
                name="clamp",
                category="numeric",
                description="Constrain value to a range",
                parameters=[
                    ParameterSpec(
                        "min_value",
                        ParameterType.COLUMN_REFERENCE,
                        required=False,
                        description="Minimum value (can be number or column reference)",
                        allow_column_references=True,
                    ),
                    ParameterSpec(
                        "max_value",
                        ParameterType.COLUMN_REFERENCE,
                        required=False,
                        description="Maximum value (can be number or column reference)",
                        allow_column_references=True,
                    ),
                ],
            )
        )

    def _add_string_operations(self):
        """Add string manipulation operations"""

        # Trim operation
        self.register_operation(
            OperationSpec(
                name="trim",
                category="string",
                description="Remove whitespace from beginning and end of string",
                parameters=[],
            )
        )

        # Lowercase operation
        self.register_operation(
            OperationSpec(
                name="lowercase",
                category="string",
                description="Convert string to lowercase",
                parameters=[],
            )
        )

        # Uppercase operation
        self.register_operation(
            OperationSpec(
                name="uppercase",
                category="string",
                description="Convert string to uppercase",
                parameters=[],
            )
        )

        # Replace operation
        self.register_operation(
            OperationSpec(
                name="replace",
                category="string",
                description="Replace occurrences of search string with replacement",
                parameters=[
                    ParameterSpec(
                        "search",
                        ParameterType.STRING,
                        required=True,
                        description="String to search for",
                    ),
                    ParameterSpec(
                        "replacement",
                        ParameterType.STRING,
                        required=True,
                        description="Replacement string",
                    ),
                    ParameterSpec(
                        "case_sensitive",
                        ParameterType.BOOLEAN,
                        default=True,
                        description="Whether search is case sensitive",
                    ),
                ],
            )
        )

    def _add_datetime_operations(self):
        """Add date/time transformation operations"""

        # Date format operation
        self.register_operation(
            OperationSpec(
                name="format_date",
                category="datetime",
                description="Format date according to pattern",
                parameters=[
                    ParameterSpec(
                        "format_pattern",
                        ParameterType.STRING,
                        required=True,
                        description="Date format pattern (e.g., YYYY-MM-DD)",
                    ),
                    ParameterSpec(
                        "input_format",
                        ParameterType.STRING,
                        required=False,
                        description="Input date format if different from default",
                    ),
                ],
            )
        )

    def _add_conditional_operations(self):
        """Add conditional transformation operations"""

        # Case when operation with flexible default_value
        self.register_operation(
            OperationSpec(
                name="case_when",
                category="conditional",
                description="Conditional value assignment based on conditions",
                parameters=[
                    ParameterSpec(
                        "conditions",
                        ParameterType.LIST,
                        required=True,
                        description="List of condition-value pairs",
                    ),
                    ParameterSpec(
                        "default_value",
                        ParameterType.STRING_OR_NUMBER,
                        required=False,
                        description="Default value if no conditions match (can be string or number)",
                    ),
                ],
            )
        )

    def _add_conversion_operations(self):
        """Add type conversion operations"""

        # String to number with flexible default
        self.register_operation(
            OperationSpec(
                name="string_to_number",
                category="conversion",
                description="Convert string to number",
                parameters=[
                    ParameterSpec(
                        "number_type",
                        ParameterType.CHOICE,
                        default="decimal",
                        choices=["integer", "decimal", "float"],
                        description="Target number type",
                    ),
                    ParameterSpec(
                        "default_value",
                        ParameterType.STRING_OR_NUMBER,
                        default=0,
                        description="Default value if conversion fails (can be string or number)",
                    ),
                ],
            )
        )

        # SQL expression (advanced) with flexible parameters
        self.register_operation(
            OperationSpec(
                name="sql_expression",
                category="advanced",
                description="Execute custom SQL expression",
                parameters=[
                    ParameterSpec(
                        "expression",
                        ParameterType.SQL_EXPRESSION,
                        required=True,
                        description="SQL expression to execute",
                        allow_sql_expressions=True,
                    ),
                    ParameterSpec(
                        "column_references",
                        ParameterType.LIST,
                        required=False,
                        description="List of column names referenced in expression",
                    ),
                ],
            )
        )

    def register_operation(self, operation_spec: OperationSpec):
        """Register a new operation specification"""
        self.operations[operation_spec.name] = operation_spec

        # Update category index
        if operation_spec.category not in self.categories:
            self.categories[operation_spec.category] = []
        self.categories[operation_spec.category].append(operation_spec.name)

    @lru_cache(maxsize=128)
    def get_operation_cached(self, name: str) -> Optional[OperationSpec]:
        """Cached operation lookup for better performance"""
        return self.operations.get(name)

    def get_operation(self, name: str) -> Optional[OperationSpec]:
        """Get operation specification by name"""
        return self.get_operation_cached(name)

    def validate_operation(
        self, operation_name: str, parameters: Dict[str, Any], path: str
    ) -> List[Dict[str, Any]]:
        """Validate an operation and its parameters"""
        errors = []

        # Check if operation exists
        operation_spec = self.get_operation(operation_name)
        if not operation_spec:
            errors.append(
                {
                    "type": "invalid_operation_type",
                    "message": f'Invalid operation type "{operation_name}"',
                    "path": path,
                    "invalid_value": operation_name,
                    "valid_values": list(self.operations.keys()),
                }
            )
            return errors

        # Validate parameters
        param_errors = operation_spec.validate_parameters(parameters, path)
        errors.extend(param_errors)

        # Special validations for specific operations
        if operation_name == "clamp":
            min_val = parameters.get("min_value")
            max_val = parameters.get("max_value")

            if min_val is None and max_val is None:
                errors.append(
                    {
                        "type": "missing_clamp_bounds",
                        "message": 'clamp: requires at least "min_value" or "max_value" parameter',
                        "path": path,
                        "operation": operation_name,
                    }
                )
            elif (
                isinstance(min_val, (int, float))
                and isinstance(max_val, (int, float))
                and min_val > max_val
            ):
                errors.append(
                    {
                        "type": "invalid_clamp_range",
                        "message": f"clamp: min_value ({min_val}) cannot exceed max_value ({max_val})",
                        "path": path,
                        "operation": operation_name,
                        "min_value": min_val,
                        "max_value": max_val,
                    }
                )

        return errors

    def get_all_operation_names(self) -> List[str]:
        """Get list of all operation names"""
        return list(self.operations.keys())

    def get_operation_suggestions(self, partial_name: str, max_suggestions: int = 5) -> List[str]:
        """
        Get operation name suggestions based on partial input

        Args:
            partial_name: Partial operation name to match
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested operation names
        """
        if not partial_name:
            return []

        partial_lower = partial_name.lower()
        suggestions = []

        # Exact prefix matches first
        for op_name in self.operations.keys():
            if op_name.lower().startswith(partial_lower):
                suggestions.append(op_name)

        # Then substring matches
        if len(suggestions) < max_suggestions:
            for op_name in self.operations.keys():
                if partial_lower in op_name.lower() and op_name not in suggestions:
                    suggestions.append(op_name)
                    if len(suggestions) >= max_suggestions:
                        break

        return suggestions[:max_suggestions]

    def get_operation_help(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed help information for an operation

        Args:
            operation_name: Name of the operation

        Returns:
            Dictionary with operation details or None if not found
        """
        operation_spec = self.get_operation(operation_name)
        if not operation_spec:
            return None

        return {
            "name": operation_spec.name,
            "category": operation_spec.category,
            "description": operation_spec.description,
            "parameters": [
                {
                    "name": param.name,
                    "type": param.param_type.value,
                    "required": param.required,
                    "default": param.default,
                    "description": param.description,
                    "min_value": param.min_value,
                    "max_value": param.max_value,
                    "choices": param.choices,
                }
                for param in operation_spec.parameters
            ],
            "examples": operation_spec.examples or [],
        }

    @lru_cache(maxsize=64)
    def get_operations_by_category_cached(self, category: str) -> tuple:
        """Cached category lookup (returns tuple for hashability)"""
        return tuple(self.categories.get(category, []))

    def get_operations_by_category(self, category: str) -> List[str]:
        """Get all operation names in a specific category"""
        return list(self.get_operations_by_category_cached(category))

    def get_all_categories(self) -> List[str]:
        """Get all available operation categories"""
        return list(self.categories.keys())


# Global registry instance
OPERATION_REGISTRY = OperationRegistry()
