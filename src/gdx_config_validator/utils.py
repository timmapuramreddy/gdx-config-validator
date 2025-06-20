"""
Utility functions for GDX Config Validator Library

Contains operation registry utilities and common helper functions
extracted from operation_registry.py and other utility functions.
"""

from typing import List, Dict, Any, Optional, Set
from .schemas.operations import OPERATION_REGISTRY, ParameterType, OperationSpec


def get_supported_operations() -> List[str]:
    """
    Get list of all supported operation types

    Returns:
        List of operation type names
    """
    return OPERATION_REGISTRY.get_all_operation_names()


def validate_operation_type(operation_type: str) -> bool:
    """
    Check if an operation type is supported

    Args:
        operation_type: Name of the operation to check

    Returns:
        bool: True if operation is supported, False otherwise
    """
    return operation_type in OPERATION_REGISTRY.operations


def get_operation_info(operation_type: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific operation

    Args:
        operation_type: Name of the operation

    Returns:
        Dict containing operation information or None if not found
    """
    return OPERATION_REGISTRY.get_operation_help(operation_type)


def get_operations_by_category(category: str) -> List[OperationSpec]:
    """
    Get all operations in a specific category

    Args:
        category: Category name (e.g., 'string', 'numeric', 'date')

    Returns:
        List of OperationSpec objects in the category
    """
    return OPERATION_REGISTRY.get_operations_by_category(category)


def get_available_categories() -> List[str]:
    """
    Get list of all available operation categories

    Returns:
        List of category names
    """
    categories = set()
    for operation in OPERATION_REGISTRY.operations.values():
        categories.add(operation.category)
    return sorted(list(categories))


def get_operation_suggestions(partial_name: str, limit: int = 5) -> List[str]:
    """
    Get operation suggestions based on partial name

    Args:
        partial_name: Partial operation name to match
        limit: Maximum number of suggestions to return

    Returns:
        List of suggested operation names
    """
    return OPERATION_REGISTRY.get_operation_suggestions(partial_name)[:limit]


def validate_operation_parameters(
    operation_type: str, parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate parameters for a specific operation

    Args:
        operation_type: Name of the operation
        parameters: Parameters to validate

    Returns:
        Dict with validation results:
        {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str]
        }
    """
    result = {"valid": True, "errors": [], "warnings": []}

    if not validate_operation_type(operation_type):
        result["valid"] = False
        result["errors"].append(f"Unknown operation type: {operation_type}")
        return result

    operation_spec = OPERATION_REGISTRY.operations[operation_type]

    # Check required parameters
    for param_name, param_spec in operation_spec.parameters.items():
        if param_spec.required and param_name not in parameters:
            result["valid"] = False
            result["errors"].append(f"Missing required parameter: {param_name}")
        elif param_name in parameters:
            # Validate parameter type and value
            param_validation = _validate_parameter_value(
                param_name, parameters[param_name], param_spec
            )
            if not param_validation["valid"]:
                result["valid"] = False
                result["errors"].extend(param_validation["errors"])
            result["warnings"].extend(param_validation.get("warnings", []))

    # Check for unexpected parameters
    for param_name in parameters:
        if param_name not in operation_spec.parameters:
            result["warnings"].append(f"Unexpected parameter: {param_name}")

    return result


def _validate_parameter_value(param_name: str, value: Any, param_spec) -> Dict[str, Any]:
    """
    Validate a single parameter value against its specification

    Args:
        param_name: Name of the parameter
        value: Value to validate
        param_spec: Parameter specification

    Returns:
        Dict with validation results
    """
    result = {"valid": True, "errors": [], "warnings": []}

    # Type validation
    if param_spec.type == ParameterType.STRING:
        if not isinstance(value, str):
            result["valid"] = False
            result["errors"].append(f"Parameter {param_name} must be a string")
    elif param_spec.type == ParameterType.INTEGER:
        if not isinstance(value, int):
            result["valid"] = False
            result["errors"].append(f"Parameter {param_name} must be an integer")
    elif param_spec.type == ParameterType.FLOAT:
        if not isinstance(value, (int, float)):
            result["valid"] = False
            result["errors"].append(f"Parameter {param_name} must be a number")
    elif param_spec.type == ParameterType.BOOLEAN:
        if not isinstance(value, bool):
            result["valid"] = False
            result["errors"].append(f"Parameter {param_name} must be a boolean")
    elif param_spec.type == ParameterType.LIST:
        if not isinstance(value, list):
            result["valid"] = False
            result["errors"].append(f"Parameter {param_name} must be a list")
    elif param_spec.type == ParameterType.DICT:
        if not isinstance(value, dict):
            result["valid"] = False
            result["errors"].append(f"Parameter {param_name} must be a dictionary")

    # Value validation (if type check passed)
    if result["valid"] and hasattr(param_spec, "allowed_values") and param_spec.allowed_values:
        if value not in param_spec.allowed_values:
            result["valid"] = False
            result["errors"].append(
                f"Parameter {param_name} must be one of: {param_spec.allowed_values}"
            )

    return result


def get_transformation_types() -> List[str]:
    """
    Get list of supported transformation types

    Returns:
        List of transformation type names
    """
    return [
        "direct_mapping",
        "string_manipulation",
        "date_formatting",
        "value_mapping",
        "data_type_conversion",
        "conditional",
        "expression",
        "complex",
        "type_conversion",
        "numeric_transformation",
        "financial_calculation",
        "mathematical_operation",
    ]


def validate_transformation_type(transformation_type: str) -> bool:
    """
    Check if a transformation type is supported

    Args:
        transformation_type: Transformation type to check

    Returns:
        bool: True if supported, False otherwise
    """
    return transformation_type in get_transformation_types()


def get_data_type_pattern() -> str:
    """
    Get the regex pattern for validating data types

    Returns:
        str: Regex pattern for data type validation
    """
    return r"^(VARCHAR|CHAR|TEXT|STRING|INTEGER|INT|BIGINT|DECIMAL|NUMERIC|FLOAT|DOUBLE|BOOLEAN|BOOL|DATE|TIMESTAMP|DATETIME|TIME|BINARY|VARBINARY|ARRAY|MAP|STRUCT)\s*(?:\([^)]*\))?\s*$"


def validate_data_type(data_type: str) -> bool:
    """
    Validate a data type string against the supported pattern

    Args:
        data_type: Data type string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    import re

    pattern = get_data_type_pattern()
    return bool(re.match(pattern, data_type.upper()))


def normalize_data_type(data_type: str) -> str:
    """
    Normalize a data type string to standard format

    Args:
        data_type: Data type string to normalize

    Returns:
        str: Normalized data type string
    """
    return data_type.upper().strip()


def extract_data_type_info(data_type: str) -> Dict[str, Any]:
    """
    Extract information from a data type string

    Args:
        data_type: Data type string (e.g., "VARCHAR(100)", "DECIMAL(10,2)")

    Returns:
        Dict containing:
        {
            'base_type': str,      # e.g., 'VARCHAR', 'DECIMAL'
            'parameters': List[str], # e.g., ['100'] or ['10', '2']
            'is_numeric': bool,
            'is_string': bool,
            'is_date': bool
        }
    """
    import re

    normalized = normalize_data_type(data_type)

    # Extract base type and parameters
    match = re.match(r"^([A-Z]+)(?:\(([^)]*)\))?\s*$", normalized)
    if not match:
        return {
            "base_type": normalized,
            "parameters": [],
            "is_numeric": False,
            "is_string": False,
            "is_date": False,
            "valid": False,
        }

    base_type = match.group(1)
    params_str = match.group(2)
    parameters = [p.strip() for p in params_str.split(",")] if params_str else []

    # Categorize type
    numeric_types = {"INTEGER", "INT", "BIGINT", "DECIMAL", "NUMERIC", "FLOAT", "DOUBLE"}
    string_types = {"VARCHAR", "CHAR", "TEXT", "STRING"}
    date_types = {"DATE", "TIMESTAMP", "DATETIME", "TIME"}

    return {
        "base_type": base_type,
        "parameters": parameters,
        "is_numeric": base_type in numeric_types,
        "is_string": base_type in string_types,
        "is_date": base_type in date_types,
        "valid": True,
    }


def get_library_stats() -> Dict[str, Any]:
    """
    Get statistics about the library capabilities

    Returns:
        Dict containing library statistics
    """
    return {
        "total_operations": len(OPERATION_REGISTRY.operations),
        "categories": get_available_categories(),
        "transformation_types": len(get_transformation_types()),
        "supports_sql_expressions": True,
        "supports_comprehensive_validation": True,
        "version": "1.0.0",
    }


def format_operation_help(operation_type: str) -> str:
    """
    Format operation help information as a readable string

    Args:
        operation_type: Operation type to get help for

    Returns:
        str: Formatted help text
    """
    info = get_operation_info(operation_type)
    if not info:
        return f"Operation '{operation_type}' not found."

    lines = [
        f"Operation: {operation_type}",
        f"Category: {info.get('category', 'Unknown')}",
        f"Description: {info.get('description', 'No description available')}",
        "",
    ]

    if "parameters" in info and info["parameters"]:
        lines.append("Parameters:")
        for param_name, param_info in info["parameters"].items():
            required = " (required)" if param_info.get("required", False) else ""
            lines.append(
                f"  - {param_name}: {param_info.get('description', 'No description')}{required}"
            )
        lines.append("")

    if "examples" in info and info["examples"]:
        lines.append("Examples:")
        for example in info["examples"]:
            lines.append(f"  {example}")

    return "\n".join(lines)


# Additional utility functions for common validation tasks
def is_valid_mapping_name(name: str) -> bool:
    """
    Check if a mapping name follows valid naming conventions

    Args:
        name: Mapping name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False

    # Basic rules: non-empty, no special characters except underscore and hyphen
    import re

    pattern = r"^[a-zA-Z][a-zA-Z0-9_-]*$"
    return bool(re.match(pattern, name))


def sanitize_mapping_name(name: str) -> str:
    """
    Sanitize a mapping name to follow valid conventions

    Args:
        name: Original mapping name

    Returns:
        str: Sanitized mapping name
    """
    if not name:
        return "unnamed_mapping"

    import re

    # Replace invalid characters with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", str(name))

    # Ensure it starts with a letter
    if not sanitized[0].isalpha():
        sanitized = f"mapping_{sanitized}"

    return sanitized


def get_column_name_suggestions(
    available_columns: List[str], target_column: str, max_suggestions: int = 3
) -> List[str]:
    """
    Get column name suggestions based on similarity

    Args:
        available_columns: List of available column names
        target_column: Target column name to find matches for
        max_suggestions: Maximum number of suggestions to return

    Returns:
        List of suggested column names
    """
    if not target_column or not available_columns:
        return []

    # Simple similarity matching (case-insensitive, partial matches)
    target_lower = target_column.lower()
    suggestions = []

    # Exact case-insensitive match
    for col in available_columns:
        if col.lower() == target_lower:
            return [col]

    # Partial matches
    for col in available_columns:
        col_lower = col.lower()
        if target_lower in col_lower or col_lower in target_lower:
            suggestions.append(col)

    # Limit suggestions
    return suggestions[:max_suggestions]
