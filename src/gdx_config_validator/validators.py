"""
GDX Configuration Validators

This module contains all validator classes for GDX (Glue DataXpress) configuration files.
Provides comprehensive validation for YAML configurations, transformations, and operations.
"""

import yaml
import os
import re
import traceback
from typing import Dict, List, Any, Optional, Tuple

from .results import ValidationResult, ValidationSeverity
from .core import (
    BaseValidator,
    ValidationContext,
    ValidationMetrics,
    ValidationRuleEngine,
    validate_with_metrics,
    log_validation_start_end,
)
from .schemas.operations import OPERATION_REGISTRY


class GDXYamlParser(BaseValidator):
    """
    Enhanced YAML parser with centralized validation infrastructure
    Eliminates redundant code through inheritance and composition
    """

    def __init__(self, logger=None):
        super().__init__(logger, "GDXYamlParser")

        # Initialize validation infrastructure
        self.rule_engine = ValidationRuleEngine()
        self.metrics = ValidationMetrics()

        # Register validation rules
        self._register_validation_rules()

        # Configuration constants
        self.transformation_types = [
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

        self.data_type_pattern = r"^(VARCHAR|CHAR|TEXT|STRING|INTEGER|INT|BIGINT|DECIMAL|NUMERIC|FLOAT|DOUBLE|BOOLEAN|BOOL|DATE|TIMESTAMP|DATETIME|TIME|BINARY|VARBINARY|ARRAY|MAP|STRUCT)\s*(?:\([^)]*\))?\s*$"

    def _register_validation_rules(self):
        """Register all validation rules with the rule engine"""

        # Mapping structure validation rules
        self.rule_engine.register_rule(
            "validate_mapping_structure",
            self._validate_mapping_structure_rule,
            "Validate basic mapping structure and naming",
            ValidationSeverity.ERROR,
            ["structure", "mapping"],
        )

        # Transformation validation rules
        self.rule_engine.register_rule(
            "validate_transformation_structure",
            self._validate_transformation_structure_rule,
            "Validate transformation structure and required fields",
            ValidationSeverity.ERROR,
            ["structure", "transformation"],
        )

        # Operation validation rules
        self.rule_engine.register_rule(
            "validate_operation_parameters",
            self._validate_operation_parameters_rule,
            "Validate operation types and parameters",
            ValidationSeverity.ERROR,
            ["operation", "parameters"],
        )

        # Data quality rules
        self.rule_engine.register_rule(
            "check_duplicate_targets",
            self._check_duplicate_target_columns_rule,
            "Check for duplicate target column names",
            ValidationSeverity.ERROR,
            ["quality", "duplicates"],
        )

        # Performance rules
        self.rule_engine.register_rule(
            "check_complex_chains",
            self._check_complex_transformation_chains_rule,
            "Check for overly complex transformation chains",
            ValidationSeverity.WARNING,
            ["performance", "complexity"],
        )

        # Numeric operation rules
        self.rule_engine.register_rule(
            "validate_numeric_operations",
            self._validate_numeric_operations_rule,
            "Validate numeric operation chains and compatibility",
            ValidationSeverity.WARNING,
            ["numeric", "operations"],
        )

    def parse_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """Parse YAML file and return parsed content"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                yaml_content = yaml.safe_load(file)

            self.log_info(f"Successfully parsed YAML file: {file_path}")
            return yaml_content or {}

        except FileNotFoundError:
            self.log_error(f"YAML file not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            self.log_error(f"YAML parsing error in {file_path}: {str(e)}")
            raise
        except Exception as e:
            self.log_error(f"Error reading YAML file {file_path}: {str(e)}")
            raise

    def parse_yaml_string(self, yaml_string: str) -> Dict[str, Any]:
        """Parse YAML string and return parsed content"""
        try:
            yaml_content = yaml.safe_load(yaml_string)
            self.log_info("Successfully parsed YAML string")
            return yaml_content or {}

        except yaml.YAMLError as e:
            self.log_error(f"YAML parsing error: {str(e)}")
            raise

    @validate_with_metrics
    @log_validation_start_end
    def validate(self, yaml_content: Dict[str, Any]) -> ValidationResult:
        """Main validation method - implements BaseValidator.validate"""
        return self.validate_column_transformations(yaml_content)

    @validate_with_metrics
    @log_validation_start_end
    def validate_column_transformations(self, yaml_content: Dict[str, Any]) -> ValidationResult:
        """Validate column transformations using the rule engine"""

        builder = self.create_result_builder()

        # Check if mappings exist
        if "mappings" not in yaml_content:
            return builder.add_error(
                "missing_section", "No mappings section found in YAML", path="root"
            ).build()

        mappings = yaml_content["mappings"]
        self.metrics.start_validation()

        # Validate each mapping using rule engine
        for i, mapping in enumerate(mappings):
            mapping_name = mapping.get("mapping_name", f"mapping_{i}")
            self.log_info(f"Validating mapping: {mapping_name}")

            # Create validation context
            context = ValidationContext(base_path=f"mappings[{i}]", mapping_name=mapping_name)

            # Apply validation rules
            mapping_result = self.rule_engine.apply_rules(
                mapping,
                context,
                rule_categories=["structure", "mapping", "transformation", "operation", "quality"],
            )

            # Merge results
            builder.errors.extend(mapping_result.errors)
            builder.warnings.extend(mapping_result.warnings)
            builder.info.extend(mapping_result.info)

            self.metrics.increment_mappings()

        # Apply global validation rules
        global_context = ValidationContext(base_path="root")
        global_result = self.rule_engine.apply_rules(
            yaml_content, global_context, rule_categories=["performance", "numeric"]
        )

        builder.errors.extend(global_result.errors)
        builder.warnings.extend(global_result.warnings)
        builder.info.extend(global_result.info)

        # Add summary information
        total_transformations = sum(
            len(mapping.get("column_transformations", [])) for mapping in mappings
        )

        builder.add_info(
            "validation_summary",
            f"Validation completed. Total mappings: {len(mappings)}, "
            f"Total transformations: {total_transformations}",
            path="root",
        )

        self.metrics.end_validation()
        result = builder.build()
        result.performance_metrics = self.metrics.to_dict()

        self.log_info(f"Column transformations validation completed. Valid: {result.is_valid}")

        return result

    @validate_with_metrics
    def validate_comprehensive(self, yaml_content: Dict[str, Any]) -> ValidationResult:
        """Comprehensive validation with enhanced checks"""
        # Get base validation result
        base_result = self.validate_column_transformations(yaml_content)

        # Apply enhanced validation rules
        enhanced_context = ValidationContext(base_path="root")
        enhanced_result = self.rule_engine.apply_rules(
            yaml_content, enhanced_context, rule_categories=["numeric", "performance", "complexity"]
        )

        # Merge results
        final_result = base_result.merge(enhanced_result)

        return final_result

    def validate_yaml_file(self, file_path: str) -> ValidationResult:
        """Complete validation of YAML file"""
        try:
            yaml_content = self.parse_yaml_file(file_path)
            return self.validate(yaml_content)
        except Exception as e:
            return self.error_handler.safe_validation_call(
                lambda: self.validate({}), f"Failed to process YAML file: {file_path}"
            )

    def validate_yaml_string(self, yaml_string: str) -> ValidationResult:
        """Complete validation of YAML string"""
        try:
            yaml_content = self.parse_yaml_string(yaml_string)
            return self.validate(yaml_content)
        except Exception as e:
            return self.error_handler.safe_validation_call(
                lambda: self.validate({}), "Failed to process YAML string"
            )

    # Validation rule implementations
    def _validate_mapping_structure_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate basic mapping structure"""
        errors = []

        mapping_name = mapping.get("mapping_name", f"mapping_{context.transformation_index}")

        # Validate mapping_name pattern
        if "mapping_name" in mapping:
            if not re.match(r"^[a-zA-Z0-9_-]+$", mapping["mapping_name"]):
                errors.append(
                    {
                        "type": "invalid_mapping_name",
                        "message": f"Invalid mapping_name pattern: {mapping_name}",
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path("mapping_name"),
                        "mapping": mapping_name,
                        "suggestion": "Use only letters, numbers, underscores, and hyphens",
                    }
                )

        return errors

    def _validate_transformation_structure_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate transformation structure within a mapping"""
        errors = []

        if "column_transformations" not in mapping:
            return []  # Not an error - mapping might not have transformations

        transformations = mapping.get("column_transformations", [])
        mapping_name = mapping.get("mapping_name", "unknown")

        if not isinstance(transformations, list):
            errors.append(
                {
                    "type": "invalid_transformations_type",
                    "message": f"column_transformations must be a list in mapping: {mapping_name}",
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path("column_transformations"),
                    "mapping": mapping_name,
                }
            )
            return errors

        # Validate each transformation
        for i, transformation in enumerate(transformations):
            trans_context = context.create_child_context(transformation_index=i)
            trans_errors = self._validate_single_transformation(
                transformation, trans_context, mapping_name
            )
            errors.extend(trans_errors)
            self.metrics.increment_transformations()

        return errors

    def _validate_single_transformation(
        self, transformation: Dict[str, Any], context: ValidationContext, mapping_name: str
    ) -> List[Dict[str, Any]]:
        """Validate a single column transformation"""
        errors = []

        if not isinstance(transformation, dict):
            errors.append(
                {
                    "type": "invalid_transformation_type",
                    "message": "Transformation must be a dictionary",
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path(),
                    "mapping": mapping_name,
                }
            )
            return errors

        # Required fields
        required_fields = ["source_alias", "target_column", "data_type", "transformation_type"]
        for field in required_fields:
            if field not in transformation:
                errors.append(
                    {
                        "type": "missing_required_field",
                        "message": f'Missing required field "{field}" in transformation',
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path(),
                        "mapping": mapping_name,
                        "field": field,
                        "suggestion": f'Add the required "{field}" field to the transformation',
                    }
                )

        # Validate transformation_type
        if "transformation_type" in transformation:
            trans_type = transformation["transformation_type"]
            if trans_type not in self.transformation_types:
                errors.append(
                    {
                        "type": "invalid_transformation_type",
                        "message": f'Invalid transformation_type "{trans_type}"',
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path(),
                        "mapping": mapping_name,
                        "invalid_value": trans_type,
                        "valid_values": self.transformation_types,
                        "suggestion": f'Use one of the valid transformation types: {", ".join(self.transformation_types[:5])}...',
                    }
                )

        # Validate data_type pattern
        if "data_type" in transformation:
            data_type = transformation["data_type"]
            if not re.match(self.data_type_pattern, data_type, re.IGNORECASE):
                errors.append(
                    {
                        "type": "invalid_data_type_pattern",
                        "message": f'Potentially invalid data_type pattern: "{data_type}"',
                        "severity": ValidationSeverity.WARNING.value,
                        "path": context.get_path(),
                        "mapping": mapping_name,
                        "data_type": data_type,
                        "suggestion": "Ensure data type follows standard SQL patterns like VARCHAR(50), DECIMAL(10,2), etc.",
                    }
                )

        # Validate transformations array
        trans_type = transformation.get("transformation_type")
        if trans_type and trans_type != "direct_mapping":
            if "transformations" not in transformation:
                errors.append(
                    {
                        "type": "missing_transformations_array",
                        "message": 'Non-direct mappings require "transformations" array',
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path(),
                        "mapping": mapping_name,
                        "transformation_type": trans_type,
                        "suggestion": 'Add a "transformations" array with the required operations',
                    }
                )
            else:
                ops_errors = self._validate_transformation_operations(
                    transformation["transformations"], context, mapping_name
                )
                errors.extend(ops_errors)

        return errors

    def _validate_transformation_operations(
        self, operations: List[Dict[str, Any]], context: ValidationContext, mapping_name: str
    ) -> List[Dict[str, Any]]:
        """Validate transformation operations array"""
        errors = []

        if not isinstance(operations, list):
            errors.append(
                {
                    "type": "invalid_operations_type",
                    "message": "Transformations must be a list",
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path("transformations"),
                    "mapping": mapping_name,
                }
            )
            return errors

        if len(operations) == 0:
            errors.append(
                {
                    "type": "empty_transformations",
                    "message": "Empty transformations array",
                    "severity": ValidationSeverity.WARNING.value,
                    "path": context.get_path("transformations"),
                    "mapping": mapping_name,
                    "suggestion": "Remove empty transformations array or add required operations",
                }
            )
            return errors

        # Validate each operation
        for j, operation in enumerate(operations):
            op_context = context.create_child_context(operation_index=j)
            op_errors = self._validate_single_operation(operation, op_context, mapping_name)
            errors.extend(op_errors)
            self.metrics.increment_operations()

        return errors

    def _validate_single_operation(
        self, operation: Dict[str, Any], context: ValidationContext, mapping_name: str
    ) -> List[Dict[str, Any]]:
        """Validate a single transformation operation using operation registry"""
        errors = []

        if not isinstance(operation, dict):
            errors.append(
                {
                    "type": "invalid_operation_type",
                    "message": "Operation must be a dictionary",
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path(),
                    "mapping": mapping_name,
                }
            )
            return errors

        # Check for required 'type' field
        if "type" not in operation:
            errors.append(
                {
                    "type": "missing_operation_type",
                    "message": 'Operation missing required "type" field',
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path(),
                    "mapping": mapping_name,
                    "suggestion": 'Add a "type" field specifying the operation type',
                }
            )
            return errors

        op_type = operation.get("type")
        parameters = operation.get("parameters", {})

        # Use operation registry for validation
        registry_errors = OPERATION_REGISTRY.validate_operation(
            op_type, parameters, context.get_path()
        )

        # Enhance errors with mapping context
        for error in registry_errors:
            error["mapping"] = mapping_name
            if "suggestion" not in error and error.get("type") == "invalid_operation_type":
                suggestions = OPERATION_REGISTRY.get_operation_suggestions(op_type)
                if suggestions:
                    error["suggestion"] = f'Did you mean one of: {", ".join(suggestions[:3])}?'

        errors.extend(registry_errors)

        return errors

    def _validate_operation_parameters_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Rule to validate operation parameters"""
        # This is handled in _validate_single_operation, so we return empty
        # This rule is here for completeness and could be extended for global parameter validation
        return []

    def _check_duplicate_target_columns_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Check for duplicate target column names"""
        errors = []
        transformations = mapping.get("column_transformations", [])
        mapping_name = mapping.get("mapping_name", "unknown")

        target_columns = []
        for i, transformation in enumerate(transformations):
            target_col = transformation.get("target_column")
            if target_col:
                if target_col in target_columns:
                    errors.append(
                        {
                            "type": "duplicate_target_column",
                            "message": f'Duplicate target column "{target_col}" found in mapping "{mapping_name}"',
                            "severity": ValidationSeverity.ERROR.value,
                            "path": f"{context.get_path()}.column_transformations[{i}]",
                            "mapping": mapping_name,
                            "column": target_col,
                            "suggestion": f'Rename one of the duplicate "{target_col}" target columns',
                        }
                    )
                else:
                    target_columns.append(target_col)

        return errors

    def _check_complex_transformation_chains_rule(
        self, yaml_content: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Check for overly complex transformation chains"""
        warnings = []

        for i, mapping in enumerate(yaml_content.get("mappings", [])):
            mapping_name = mapping.get("mapping_name", f"mapping_{i}")

            for j, transformation in enumerate(mapping.get("column_transformations", [])):
                operations = transformation.get("transformations", [])

                if len(operations) > 5:
                    warnings.append(
                        {
                            "type": "complex_transformation_chain",
                            "message": f"Complex transformation chain with {len(operations)} operations",
                            "severity": ValidationSeverity.WARNING.value,
                            "path": f"mappings[{i}].column_transformations[{j}]",
                            "mapping": mapping_name,
                            "operation_count": len(operations),
                            "suggestion": "Consider using sql_expression for complex calculations or breaking into multiple transformations",
                        }
                    )

        return warnings

    def _validate_numeric_operations_rule(
        self, yaml_content: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate numeric operation chains and compatibility"""
        warnings = []

        numeric_ops = [
            "round",
            "ceil",
            "floor",
            "truncate_number",
            "add",
            "subtract",
            "multiply",
            "divide",
            "power",
            "sqrt",
            "abs",
            "mod",
        ]

        for i, mapping in enumerate(yaml_content.get("mappings", [])):
            mapping_name = mapping.get("mapping_name", f"mapping_{i}")

            for j, transformation in enumerate(mapping.get("column_transformations", [])):
                operations = transformation.get("transformations", [])

                if len(operations) <= 1:
                    continue

                step_types = [step.get("type") for step in operations]

                # Check for redundant rounding operations
                rounding_ops = [
                    op for op in step_types if op in ["round", "ceil", "floor", "truncate_number"]
                ]
                if len(rounding_ops) > 1:
                    warnings.append(
                        {
                            "type": "redundant_rounding",
                            "message": f"Multiple rounding operations detected: {rounding_ops}",
                            "severity": ValidationSeverity.WARNING.value,
                            "path": f"mappings[{i}].column_transformations[{j}]",
                            "mapping": mapping_name,
                            "rounding_operations": rounding_ops,
                            "suggestion": "Consider combining rounding operations - only the last one will take effect",
                        }
                    )

                # Check for potential precision loss in arithmetic chains
                arithmetic_ops = [
                    op for op in step_types if op in ["multiply", "divide", "add", "subtract"]
                ]
                if len(arithmetic_ops) > 3:
                    warnings.append(
                        {
                            "type": "complex_arithmetic_chain",
                            "message": f"Complex arithmetic chain with {len(arithmetic_ops)} operations",
                            "severity": ValidationSeverity.INFO.value,
                            "path": f"mappings[{i}].column_transformations[{j}]",
                            "mapping": mapping_name,
                            "arithmetic_operations": arithmetic_ops,
                            "suggestion": "Consider using sql_expression for complex calculations",
                        }
                    )

                # Check for canceling operations
                for k in range(len(operations) - 1):
                    current_op = operations[k]
                    next_op = operations[k + 1]

                    current_type = current_op.get("type")
                    next_type = next_op.get("type")

                    if current_type == "divide" and next_type == "multiply":
                        current_factor = current_op.get("parameters", {}).get("factor", 1)
                        next_factor = next_op.get("parameters", {}).get("factor", 1)

                        if isinstance(current_factor, (int, float)) and isinstance(
                            next_factor, (int, float)
                        ):
                            if abs(current_factor * next_factor - 1.0) < 0.0001:
                                warnings.append(
                                    {
                                        "type": "canceling_operations",
                                        "message": f"Division by {current_factor} followed by multiplication by {next_factor} largely cancel out",
                                        "severity": ValidationSeverity.WARNING.value,
                                        "path": f"mappings[{i}].column_transformations[{j}].transformations[{k}]",
                                        "mapping": mapping_name,
                                        "suggestion": "Consider simplifying or removing these operations",
                                    }
                                )

        return warnings

    def get_validation_summary(self, result: ValidationResult) -> str:
        """Generate a human-readable validation summary"""
        from .core import ValidationSummaryGenerator

        return ValidationSummaryGenerator.generate_detailed_summary(result)


class ComprehensiveYamlValidator(GDXYamlParser):
    """
    Extended validator that handles all YAML sections using the rule engine pattern
    """

    def __init__(self, logger=None):
        super().__init__(logger)
        # Register additional validation rules for new sections
        self._register_extended_validation_rules()

    def _register_extended_validation_rules(self):
        """Register validation rules for additional YAML sections"""

        # Default partition settings validation
        self.rule_engine.register_rule(
            "validate_default_partition_settings",
            self._validate_default_partition_settings_rule,
            "Validate default partition settings structure and values",
            ValidationSeverity.ERROR,
            ["structure", "partition", "settings"],
        )

        # Column mapping validation
        self.rule_engine.register_rule(
            "validate_column_mapping",
            self._validate_column_mapping_rule,
            "Validate column mapping structure and consistency",
            ValidationSeverity.ERROR,
            ["structure", "mapping", "columns"],
        )

        # Column duplications validation
        self.rule_engine.register_rule(
            "validate_column_duplications",
            self._validate_column_duplications_rule,
            "Validate column duplication configuration",
            ValidationSeverity.WARNING,
            ["structure", "duplications", "columns"],
        )

        # Source columns validation
        self.rule_engine.register_rule(
            "validate_source_columns",
            self._validate_source_columns_rule,
            "Validate source columns format and references",
            ValidationSeverity.ERROR,
            ["structure", "columns", "source"],
        )

        # Cross-section consistency rules
        self.rule_engine.register_rule(
            "validate_column_consistency",
            self._validate_column_consistency_rule,
            "Validate consistency across column sections",
            ValidationSeverity.WARNING,
            ["consistency", "columns"],
        )

        # Settings validation rules
        self.rule_engine.register_rule(
            "validate_job_settings",
            self._validate_job_settings_rule,
            "Validate job-level settings section",
            ValidationSeverity.ERROR,
            ["structure", "settings"],
        )

    def validate_comprehensive(self, yaml_content: Dict[str, Any]) -> ValidationResult:
        """
        Comprehensive validation including all YAML sections
        """
        builder = self.create_result_builder()

        # Validate job-level settings first
        if "settings" in yaml_content:
            settings_context = ValidationContext(base_path="settings")
            settings_result = self.rule_engine.apply_rules(
                yaml_content["settings"],
                settings_context,
                rule_categories=["structure", "settings", "partition"],
            )
            builder.errors.extend(settings_result.errors)
            builder.warnings.extend(settings_result.warnings)
            builder.info.extend(settings_result.info)

        # Validate mappings (includes new column sections)
        if "mappings" in yaml_content:
            for i, mapping in enumerate(yaml_content["mappings"]):
                mapping_context = ValidationContext(
                    base_path=f"mappings[{i}]",
                    mapping_name=mapping.get("mapping_name", f"mapping_{i}"),
                )

                # Apply all mapping rules (including new ones)
                mapping_result = self.rule_engine.apply_rules(
                    mapping,
                    mapping_context,
                    rule_categories=[
                        "structure",
                        "mapping",
                        "columns",
                        "duplications",
                        "source",
                        "consistency",
                    ],
                )

                builder.errors.extend(mapping_result.errors)
                builder.warnings.extend(mapping_result.warnings)
                builder.info.extend(mapping_result.info)

        # Apply transformation validation (existing functionality)
        transformation_result = self.validate_column_transformations(yaml_content)
        builder.errors.extend(transformation_result.errors)
        builder.warnings.extend(transformation_result.warnings)
        builder.info.extend(transformation_result.info)

        return builder.build()

    # ==========================================
    # VALIDATION RULE IMPLEMENTATIONS
    # ==========================================

    def _validate_default_partition_settings_rule(
        self, settings: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate default partition settings section"""
        errors = []

        if "default_partition_settings" not in settings:
            return []  # Optional section

        partition_settings = settings["default_partition_settings"]

        # Validate partition settings structure
        valid_keys = {
            "partition_enabled",
            "dynamic_partition_calculation",
            "partition_refresh_frequency",
            "average_row_size",
            "target_partition_size_mb",
            "partition_buffer_percent",
            "num_partitions",
            "num_partitions_for_delta",
            "partition_lowerbound",
            "partition_upperbound",
            "allow_num_partitions_adjustment",
            "allow_num_partitions_for_delta_adjustment",
        }

        for key, value in partition_settings.items():
            if key not in valid_keys:
                errors.append(
                    {
                        "type": "unknown_partition_setting",
                        "message": f"Unknown partition setting: {key}",
                        "severity": ValidationSeverity.WARNING.value,
                        "path": context.get_path(f"default_partition_settings.{key}"),
                        "setting": key,
                        "valid_settings": list(valid_keys),
                        "suggestion": f'Remove unknown setting "{key}" or check for typos',
                    }
                )

        # Validate specific setting values
        if "partition_enabled" in partition_settings:
            if partition_settings["partition_enabled"] not in ["Y", "N"]:
                errors.append(
                    {
                        "type": "invalid_partition_enabled_value",
                        "message": f'partition_enabled must be Y/N or true/false, got: {partition_settings["partition_enabled"]}',
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path("default_partition_settings.partition_enabled"),
                        "value": partition_settings["partition_enabled"],
                    }
                )

        # Validate numeric settings
        numeric_settings = {
            "average_row_size": (1, 1000000),
            "target_partition_size_mb": (1, 1000),
            "partition_buffer_percent": (0, 100),
            "num_partitions": (1, 10000),
            "num_partitions_for_delta": (1, 10000),
        }

        for setting, (min_val, max_val) in numeric_settings.items():
            if setting in partition_settings:
                value = partition_settings[setting]
                if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                    errors.append(
                        {
                            "type": "invalid_numeric_setting",
                            "message": f"{setting} must be between {min_val} and {max_val}, got: {value}",
                            "severity": ValidationSeverity.ERROR.value,
                            "path": context.get_path(f"default_partition_settings.{setting}"),
                            "setting": setting,
                            "value": value,
                            "min_value": min_val,
                            "max_value": max_val,
                        }
                    )

        return errors

    def _validate_column_mapping_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate column mapping section"""
        errors = []

        if "columns_mapping" not in mapping:
            return []  # Optional section

        columns_mapping = mapping["columns_mapping"]
        mapping_name = mapping.get("mapping_name", "unknown")

        if not isinstance(columns_mapping, dict):
            errors.append(
                {
                    "type": "invalid_column_mapping_type",
                    "message": f"columns_mapping must be a dictionary in mapping: {mapping_name}",
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path("columns_mapping"),
                    "mapping": mapping_name,
                }
            )
            return errors

        # Validate column name patterns
        invalid_chars_pattern = r"[^a-zA-Z0-9_]"

        for source_col, target_col in columns_mapping.items():
            # Validate source column name
            if re.search(invalid_chars_pattern, str(source_col)):
                errors.append(
                    {
                        "type": "invalid_source_column_name",
                        "message": f"Source column name contains invalid characters: {source_col}",
                        "severity": ValidationSeverity.WARNING.value,
                        "path": context.get_path("columns_mapping"),
                        "mapping": mapping_name,
                        "column": source_col,
                        "suggestion": "Use only letters, numbers, and underscores in column names",
                    }
                )

            # Validate target column name
            if re.search(invalid_chars_pattern, str(target_col)):
                errors.append(
                    {
                        "type": "invalid_target_column_name",
                        "message": f"Target column name contains invalid characters: {target_col}",
                        "severity": ValidationSeverity.WARNING.value,
                        "path": context.get_path("columns_mapping"),
                        "mapping": mapping_name,
                        "column": target_col,
                        "suggestion": "Use only letters, numbers, and underscores in column names",
                    }
                )

        # Check for duplicate target columns
        target_columns = list(columns_mapping.values())
        duplicate_targets = set([col for col in target_columns if target_columns.count(col) > 1])

        for duplicate in duplicate_targets:
            errors.append(
                {
                    "type": "duplicate_target_column_mapping",
                    "message": f'Target column "{duplicate}" is mapped from multiple source columns',
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path("columns_mapping"),
                    "mapping": mapping_name,
                    "column": duplicate,
                    "suggestion": f"Ensure each target column has only one source mapping",
                }
            )

        return errors

    def _validate_column_duplications_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate column duplications section"""
        errors = []

        if "column_duplications" not in mapping:
            return []  # Optional section

        duplications = mapping["column_duplications"]
        mapping_name = mapping.get("mapping_name", "unknown")

        if not isinstance(duplications, list):
            errors.append(
                {
                    "type": "invalid_column_duplications_type",
                    "message": f"column_duplications must be a list in mapping: {mapping_name}",
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path("column_duplications"),
                    "mapping": mapping_name,
                }
            )
            return errors

        for i, duplication in enumerate(duplications):
            if not isinstance(duplication, dict):
                errors.append(
                    {
                        "type": "invalid_duplication_entry",
                        "message": f"Duplication entry must be a dictionary in mapping: {mapping_name}",
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path(f"column_duplications[{i}]"),
                        "mapping": mapping_name,
                    }
                )
                continue

            # Validate required fields
            if "source_column" not in duplication:
                errors.append(
                    {
                        "type": "missing_source_column",
                        "message": f"Missing source_column in duplication entry",
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path(f"column_duplications[{i}]"),
                        "mapping": mapping_name,
                    }
                )

            if "additional_columns" not in duplication:
                errors.append(
                    {
                        "type": "missing_additional_columns",
                        "message": f"Missing additional_columns in duplication entry",
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path(f"column_duplications[{i}]"),
                        "mapping": mapping_name,
                    }
                )
            elif not isinstance(duplication["additional_columns"], list):
                errors.append(
                    {
                        "type": "invalid_additional_columns_type",
                        "message": f"additional_columns must be a list",
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path(f"column_duplications[{i}].additional_columns"),
                        "mapping": mapping_name,
                    }
                )
            elif len(duplication["additional_columns"]) == 0:
                errors.append(
                    {
                        "type": "empty_additional_columns",
                        "message": f"additional_columns list cannot be empty",
                        "severity": ValidationSeverity.WARNING.value,
                        "path": context.get_path(f"column_duplications[{i}].additional_columns"),
                        "mapping": mapping_name,
                        "suggestion": "Add at least one additional column or remove the duplication entry",
                    }
                )

        return errors

    def _validate_source_columns_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate source columns interested section"""
        errors = []

        if "source_columns_interested" not in mapping:
            return []  # Optional section

        source_columns = mapping["source_columns_interested"]
        mapping_name = mapping.get("mapping_name", "unknown")

        if not isinstance(source_columns, list):
            errors.append(
                {
                    "type": "invalid_source_columns_type",
                    "message": f"source_columns_interested must be a list in mapping: {mapping_name}",
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path("source_columns_interested"),
                    "mapping": mapping_name,
                }
            )
            return errors

        # Validate column format and SQL expressions
        for i, column in enumerate(source_columns):
            if not isinstance(column, str):
                errors.append(
                    {
                        "type": "invalid_column_type",
                        "message": f"Source column must be a string, got: {type(column).__name__}",
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path(f"source_columns_interested[{i}]"),
                        "mapping": mapping_name,
                    }
                )
                continue

            # Enhanced SQL injection patterns (comprehensive security check)
            dangerous_patterns = [
                r"\b(exec|execute)\s*\(",  # Exec functions
                r"\b(sp_|xp_)\w+",  # System stored procedures
                r"--.*?$",  # SQL comments
                r"/\*.*?\*/",  # Block comments
                r"\b(union|intersect|except)\s+select\b",  # Union injections
                r"\b(drop|create|alter|truncate)\s+\w+",  # DDL commands
                r"\binto\s+outfile\b",  # File operations
                r"\bload_file\s*\(",  # Load file function
                r";.*?(drop|delete|insert|update|create)",  # Command chaining
                r"\bwaitfor\s+delay\b",  # Time delays
                r"\bbenchmark\s*\(",  # Benchmark function
                r"\bsleep\s*\(",  # Sleep function
            ]
            column_upper = column.upper()

            # Enhanced security validation
            security_errors = self._validate_sql_security(column, column_upper, dangerous_patterns)
            errors.extend(security_errors)

            # Common audit column patterns to exclude
            audit_column_patterns = [
                "CREATED_BY",
                "CREATED_DT",
                "CREATED_DATE",
                "CREATE_DATE",
                "LAST_UPD",
                "LAST_UPDATE",
                "UPDATED_BY",
                "UPDATED_DT",
            ]

            # Skip validation for known audit columns
            is_audit_column = False
            for audit_pattern in audit_column_patterns:
                if audit_pattern in column_upper.replace('"', "").replace(" ", ""):
                    is_audit_column = True
                    break

            # Security validation is already done above - skip basic pattern check for audit columns
            if not is_audit_column:
                pass  # Enhanced security validation handles all cases

            # Validate alias format if present
            normalized_column = " ".join(column.split())
            alias_found = False

            # Case 1: Standard format with "as" keyword
            if " as " in normalized_column.lower():
                alias_found = True
                # Use a more robust approach for CASE expressions
                if "case" in normalized_column.lower() and "end as" in normalized_column.lower():
                    # CASE expressions are valid, extract the alias
                    parts = normalized_column.lower().split("end as ")
                    if len(parts) != 2 or not parts[1].strip():
                        errors.append(
                            {
                                "type": "invalid_alias_format",
                                "message": f"Invalid alias format in CASE expression: {column}",
                                "severity": ValidationSeverity.ERROR.value,
                                "path": context.get_path(f"source_columns_interested[{i}]"),
                                "mapping": mapping_name,
                                "column": column,
                                "suggestion": 'Use format: "CASE ... END as alias_name"',
                            }
                        )
                    else:
                        # Validate the alias format for CASE statements
                        alias = parts[1].strip()
                        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", alias):
                            errors.append(
                                {
                                    "type": "invalid_alias_name",
                                    "message": f"Invalid alias name: {alias}",
                                    "severity": ValidationSeverity.WARNING.value,
                                    "path": context.get_path(f"source_columns_interested[{i}]"),
                                    "mapping": mapping_name,
                                    "alias": alias,
                                    "suggestion": "Use valid identifier names for aliases",
                                }
                            )
                else:
                    # Standard column pattern with 'as'
                    parts = normalized_column.lower().split(" as ")
                    if len(parts) != 2:
                        errors.append(
                            {
                                "type": "invalid_alias_format",
                                "message": f"Invalid alias format in column: {column}",
                                "severity": ValidationSeverity.ERROR.value,
                                "path": context.get_path(f"source_columns_interested[{i}]"),
                                "mapping": mapping_name,
                                "column": column,
                                "suggestion": 'Use format: "column_expression as alias_name"',
                            }
                        )
                    else:
                        alias = parts[1].strip()
                        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", alias):
                            errors.append(
                                {
                                    "type": "invalid_alias_name",
                                    "message": f"Invalid alias name: {alias}",
                                    "severity": ValidationSeverity.WARNING.value,
                                    "path": context.get_path(f"source_columns_interested[{i}]"),
                                    "mapping": mapping_name,
                                    "alias": alias,
                                    "suggestion": "Use valid identifier names for aliases",
                                }
                            )

            # Case 2: Format without "as" keyword (just space between column and alias)
            elif normalized_column.count('"') >= 2 and re.search(
                r'"\s+([a-zA-Z_][a-zA-Z0-9_]*)$', normalized_column
            ):
                # This handles "column_name" alias_name format
                alias_found = True
                match = re.search(r'"\s+([a-zA-Z_][a-zA-Z0-9_]*)$', normalized_column)
                alias = match.group(1)

                # Log a warning about non-standard format
                errors.append(
                    {
                        "type": "non_standard_alias_format",
                        "message": f"Non-standard alias format detected: {column}",
                        "severity": ValidationSeverity.WARNING.value,
                        "path": context.get_path(f"source_columns_interested[{i}]"),
                        "mapping": mapping_name,
                        "column": column,
                        "suggestion": f'Consider using standard format with "as" keyword: "column_expression as {alias}"',
                    }
                )

            # Case 3: No alias at all (just use the column name)
            else:
                # This is acceptable, nothing to validate for alias
                pass

        return errors

    def _validate_column_consistency_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate consistency across different column sections"""
        warnings = []
        errors = []  # Add errors list for transformation issues
        mapping_name = mapping.get("mapping_name", "unknown")

        # Get all column references from different sections
        source_columns_set = set()
        mapped_columns_set = set()
        duplicated_source_columns_set = set()
        duplicated_additional_columns_set = set()
        transformation_columns_set = set()

        # Extract from source_columns_interested
        if "source_columns_interested" in mapping:
            for col in mapping["source_columns_interested"]:
                if isinstance(col, str):
                    normalized_col = " ".join(col.split())  # Normalize whitespace

                    # Extract alias or column name
                    if " as " in normalized_col.lower():
                        # Handle complex cases like CASE statements
                        if "case" in normalized_col.lower() and "end as" in normalized_col.lower():
                            # CASE statement - extract alias after 'end as'
                            parts = normalized_col.lower().split("end as ")
                            if len(parts) == 2:
                                alias = parts[1].strip()
                                source_columns_set.add(alias)
                        else:
                            # Standard 'as' alias
                            alias = normalized_col.lower().split(" as ")[1].strip()
                            source_columns_set.add(alias)

                    # Case 2: Format without "as" keyword (just space between column and alias)
                    elif normalized_col.count('"') >= 2 and re.search(
                        r'"\s+([a-zA-Z_][a-zA-Z0-9_]*)$', normalized_col
                    ):
                        # This handles "column_name" alias_name format
                        match = re.search(r'"\s+([a-zA-Z_][a-zA-Z0-9_]*)$', normalized_col)
                        alias = match.group(1)
                        source_columns_set.add(alias)

                    else:
                        # Simple column name
                        # Extract column name as implicit alias
                        column_parts = normalized_col.strip().split(".")
                        clean_col = column_parts[-1].strip("\"'")
                        source_columns_set.add(clean_col)

        # Extract from columns_mapping
        if "columns_mapping" in mapping:
            for source_col in mapping["columns_mapping"].keys():
                mapped_columns_set.add(str(source_col))

        # Extract from column_duplications
        if "column_duplications" in mapping:
            for dup in mapping["column_duplications"]:
                if isinstance(dup, dict):
                    if "source_column" in dup:
                        duplicated_source_columns_set.add(str(dup["source_column"]))
                    if "additional_columns" in dup and isinstance(dup["additional_columns"], list):
                        for add_col in dup["additional_columns"]:
                            duplicated_additional_columns_set.add(str(add_col))

        # Extract from column_transformations
        if "column_transformations" in mapping:
            for trans in mapping["column_transformations"]:
                if isinstance(trans, dict) and "source_alias" in trans:
                    transformation_columns_set.add(str(trans["source_alias"]))

        # Check consistency between sections
        # 1. Columns in mapping but not in source_columns_interested (WARNING)
        orphaned_mapped = mapped_columns_set - source_columns_set
        if orphaned_mapped and source_columns_set:
            warnings.append(
                {
                    "type": "orphaned_mapped_columns",
                    "message": f"Columns in mapping but not in source_columns_interested: {orphaned_mapped}",
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path("columns_mapping"),
                    "mapping": mapping_name,
                    "orphaned_columns": list(orphaned_mapped),
                    "suggestion": "Ensure mapped columns are included in source_columns_interested",
                }
            )

        # 2. Duplicated columns not in source columns (WARNING)
        orphaned_duplicated = duplicated_source_columns_set - source_columns_set
        if orphaned_duplicated and source_columns_set:
            warnings.append(
                {
                    "type": "orphaned_duplicated_columns",
                    "message": f"Duplicated columns not in source_columns_interested: {orphaned_duplicated}",
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path("column_duplications"),
                    "mapping": mapping_name,
                    "orphaned_columns": list(orphaned_duplicated),
                    "suggestion": "Ensure duplicated columns are included in source_columns_interested",
                }
            )

        # 3. CRITICAL: Transformation columns not in source columns (ERROR - not WARNING!)
        orphaned_transformations = transformation_columns_set - source_columns_set
        if orphaned_transformations and source_columns_set:
            errors.append(
                {  # Changed from warnings.append() to errors.append()
                    "type": "orphaned_transformation_columns",
                    "message": f"Column transformation source aliases not found in source_columns_interested: {orphaned_transformations}",
                    "severity": ValidationSeverity.ERROR.value,  # Changed from WARNING to ERROR
                    "path": context.get_path("column_transformations"),
                    "mapping": mapping_name,
                    "orphaned_columns": list(orphaned_transformations),
                    "available_columns": sorted(source_columns_set) if source_columns_set else [],
                    "suggestion": f"Add missing aliases to source_columns_interested or update source_alias in transformations. Available: {sorted(source_columns_set)}",
                }
            )

        # Return both warnings and errors
        return warnings + errors  # Combine both lists

    def _validate_job_settings_rule(
        self, settings: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """Validate job-level settings section"""
        errors = []

        # Validate load mode
        if "load" in settings:
            valid_modes = ["full", "delta", "incremental"]
            if settings["load"] not in valid_modes:
                errors.append(
                    {
                        "type": "invalid_load_mode",
                        "message": f'Invalid load mode: {settings["load"]}. Must be one of: {valid_modes}',
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path("load"),
                        "value": settings["load"],
                        "valid_values": valid_modes,
                    }
                )

        # Validate environment
        if "environment" in settings:
            valid_envs = ["dev", "test", "stage", "prod", "production"]
            if settings["environment"] not in valid_envs:
                errors.append(
                    {
                        "type": "invalid_environment",
                        "message": f'Invalid environment: {settings["environment"]}. Must be one of: {valid_envs}',
                        "severity": ValidationSeverity.WARNING.value,
                        "path": context.get_path("environment"),
                        "value": settings["environment"],
                        "valid_values": valid_envs,
                    }
                )

        return errors

    def _validate_sql_security(
        self, expression: str, expression_upper: str, dangerous_patterns: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Enhanced SQL security validation to prevent injection attacks

        Args:
            expression: Original SQL expression
            expression_upper: Uppercased SQL expression
            dangerous_patterns: List of regex patterns to check

        Returns:
            List of security validation errors
        """
        import re
        import traceback

        errors = []

        try:
            # Check against comprehensive dangerous patterns
            for pattern in dangerous_patterns:
                try:
                    if re.search(pattern, expression, re.IGNORECASE | re.MULTILINE):
                        errors.append(
                            {
                                "type": "sql_security_risk",
                                "message": f"Potentially dangerous SQL pattern detected: {pattern}",
                                "severity": "critical",
                                "expression": (
                                    expression[:100] + "..."
                                    if len(expression) > 100
                                    else expression
                                ),
                                "pattern": pattern,
                                "security_level": "high_risk",
                                "suggestion": "Review and sanitize SQL expression to prevent injection attacks",
                            }
                        )
                except re.error as regex_error:
                    # Handle invalid regex patterns gracefully
                    errors.append(
                        {
                            "type": "sql_security_validation_error",
                            "message": f"Error validating SQL pattern: {regex_error}",
                            "severity": "warning",
                            "pattern": pattern,
                            "suggestion": "Check regex pattern in security validation",
                        }
                    )

            # Additional context-specific security checks
            suspicious_functions = [
                "xp_cmdshell",
                "sp_configure",
                "openrowset",
                "opendatasource",
                "exec",
                "execute",
                "eval",
                "script",
                "shell",
            ]

            for func in suspicious_functions:
                if func.lower() in expression.lower():
                    errors.append(
                        {
                            "type": "suspicious_sql_function",
                            "message": f"Suspicious SQL function detected: {func}",
                            "severity": "critical",
                            "function": func,
                            "expression": (
                                expression[:100] + "..." if len(expression) > 100 else expression
                            ),
                            "suggestion": f"Remove or replace {func} function if not necessary",
                        }
                    )

            # Check for excessive complexity that might hide malicious code
            if len(expression) > 1000:  # Very long expressions
                nesting_level = expression.count("(") - expression.count(")")
                if abs(nesting_level) > 10:  # Deeply nested
                    errors.append(
                        {
                            "type": "sql_complexity_warning",
                            "message": "Extremely complex SQL expression detected",
                            "severity": "warning",
                            "expression_length": len(expression),
                            "nesting_level": abs(nesting_level),
                            "suggestion": "Consider breaking down complex expressions for security and maintainability",
                        }
                    )

        except Exception as e:
            # Ensure security validation doesn't break the overall validation
            errors.append(
                {
                    "type": "sql_security_validation_exception",
                    "message": f"Security validation failed: {str(e)}",
                    "severity": "warning",
                    "exception": str(e),
                    "traceback": traceback.format_exc(),
                    "suggestion": "Review SQL security validation logic",
                }
            )

        return errors


class SQLExpressionColumnValidator(ComprehensiveYamlValidator):
    """
    Extended validator that handles SQL expressions in column mapping validation
    """

    def __init__(self, logger=None):
        super().__init__(logger)

        # Register SQL expression specific validation rules
        self._register_sql_expression_validation_rules()

        # SQL expression patterns for better parsing
        self.sql_patterns = {
            # Basic alias pattern: "expression as alias" or "expression AS alias"
            "alias_pattern": re.compile(r"\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*$", re.IGNORECASE),
            # Quoted identifier pattern: "schema"."table" or "column"
            "quoted_identifier": re.compile(r'"[^"]*"'),
            # CASE statement pattern
            "case_statement": re.compile(
                r"\bcase\s+.*?\s+end\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE | re.DOTALL
            ),
            # Function call pattern: FUNCTION(args) as alias
            "function_call": re.compile(
                r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                re.IGNORECASE,
            ),
            # Mathematical expression pattern: col1 * col2 as alias
            "math_expression": re.compile(
                r"[^)]+[+\-*/][^(]+\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE
            ),
            # Concatenation pattern: col1 || col2 as alias
            "concat_expression": re.compile(
                r"[^)]+\|\|[^(]+\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE
            ),
        }

    def _register_sql_expression_validation_rules(self):
        """Register SQL expression specific validation rules"""

        # SQL Expression alias validation
        self.rule_engine.register_rule(
            "validate_sql_expression_aliases",
            self._validate_sql_expression_aliases_rule,
            "Validate SQL expressions have proper aliases and are used correctly in mapping",
            ValidationSeverity.ERROR,
            ["sql", "expression", "mapping", "alias"],
        )

        # Column mapping consistency with SQL expressions
        self.rule_engine.register_rule(
            "validate_column_mapping_sql_consistency",
            self._validate_column_mapping_sql_consistency_rule,
            "Validate column_mapping references match source_columns_interested including SQL expressions",
            ValidationSeverity.ERROR,
            ["sql", "mapping", "consistency"],
        )

        # Quoted identifier validation
        self.rule_engine.register_rule(
            "validate_quoted_identifiers",
            self._validate_quoted_identifiers_rule,
            "Validate proper handling of quoted identifiers in SQL expressions",
            ValidationSeverity.WARNING,
            ["sql", "identifier", "quote"],
        )

        # Complex SQL expression validation
        self.rule_engine.register_rule(
            "validate_complex_sql_expressions",
            self._validate_complex_sql_expressions_rule,
            "Validate complex SQL expressions (CASE, functions, math) are properly aliased",
            ValidationSeverity.ERROR,
            ["sql", "expression", "complex"],
        )

    def _validate_sql_expression_aliases_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """
        Validate SQL expressions have proper aliases and are correctly referenced in column_mapping
        """
        errors = []

        if "source_columns_interested" not in mapping:
            return []

        mapping_name = mapping.get("mapping_name", "unknown")
        source_columns = mapping.get("source_columns_interested", [])
        columns_mapping = mapping.get("columns_mapping", {})

        # Extract all SQL expressions and their aliases
        sql_expressions = {}  # {alias: original_expression}
        simple_columns = set()  # Non-expression columns

        for i, column_expr in enumerate(source_columns):
            if not isinstance(column_expr, str):
                continue

            # Check if this is a SQL expression with alias
            alias = self._extract_alias_from_expression(column_expr)

            if alias:
                # This is a SQL expression with alias
                sql_expressions[alias] = column_expr

                # Validate the expression structure
                expression_errors = self._validate_expression_structure(
                    column_expr, alias, i, mapping_name, context
                )
                errors.extend(expression_errors)

            else:
                # Check if this looks like a SQL expression without alias
                if self._looks_like_sql_expression(column_expr):
                    errors.append(
                        {
                            "type": "sql_expression_missing_alias",
                            "message": f'SQL expression appears to be missing alias: "{column_expr}"',
                            "severity": ValidationSeverity.ERROR.value,
                            "path": context.get_path(f"source_columns_interested[{i}]"),
                            "mapping": mapping_name,
                            "expression": column_expr,
                            "suggestion": 'Add "as alias_name" to the SQL expression',
                        }
                    )
                else:
                    # Simple column reference
                    clean_column = self._extract_column_name(column_expr)
                    simple_columns.add(clean_column)

        # Store extracted information for use in other validation rules
        if not hasattr(context, "sql_expressions"):
            context.sql_expressions = sql_expressions
            context.simple_columns = simple_columns

        return errors

    def _validate_column_mapping_sql_consistency_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """
        Validate that all column_mapping source columns exist in source_columns_interested
        This includes SQL expression aliases
        """
        errors = []

        if "columns_mapping" not in mapping:
            return []

        mapping_name = mapping.get("mapping_name", "unknown")
        columns_mapping = mapping.get("columns_mapping", {})

        # Get available columns and aliases from context or parse again
        if hasattr(context, "sql_expressions") and hasattr(context, "simple_columns"):
            available_aliases = set(context.sql_expressions.keys())
            available_simple_columns = context.simple_columns
        else:
            # Parse source columns again if context doesn't have the info
            available_aliases, available_simple_columns = self._parse_source_columns(mapping)

        all_available_columns = available_aliases | available_simple_columns

        # Validate each mapping
        for source_col, target_col in columns_mapping.items():
            if source_col not in all_available_columns:
                # Check if it might be a case sensitivity issue
                case_matches = [
                    col for col in all_available_columns if col.lower() == source_col.lower()
                ]

                if case_matches:
                    suggestion = f'Did you mean "{case_matches[0]}"? (case sensitivity issue)'
                else:
                    # Suggest available aliases if this looks like it should be one
                    if available_aliases:
                        suggestion = (
                            f'Available aliases: {", ".join(sorted(available_aliases)[:5])}'
                        )
                    else:
                        suggestion = (
                            "Ensure the column or alias exists in source_columns_interested"
                        )

                errors.append(
                    {
                        "type": "column_mapping_source_not_found",
                        "message": f'Column mapping source "{source_col}" not found in source_columns_interested',
                        "severity": ValidationSeverity.ERROR.value,
                        "path": context.get_path("columns_mapping"),
                        "mapping": mapping_name,
                        "missing_column": source_col,
                        "target_column": target_col,
                        "available_columns": sorted(all_available_columns),
                        "available_aliases": sorted(available_aliases),
                        "suggestion": suggestion,
                    }
                )

        return errors

    def _validate_quoted_identifiers_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """
        Validate proper handling of quoted identifiers in SQL expressions
        """
        warnings = []

        if "source_columns_interested" not in mapping:
            return []

        mapping_name = mapping.get("mapping_name", "unknown")
        source_columns = mapping.get("source_columns_interested", [])

        for i, column_expr in enumerate(source_columns):
            if not isinstance(column_expr, str):
                continue

            # Check for quoted identifiers
            quoted_identifiers = self.sql_patterns["quoted_identifier"].findall(column_expr)

            if quoted_identifiers:
                # Validate quoted identifier patterns
                for quoted_id in quoted_identifiers:
                    # Check for potential issues
                    if len(quoted_id) <= 2:  # Just quotes with nothing inside
                        warnings.append(
                            {
                                "type": "empty_quoted_identifier",
                                "message": f"Empty quoted identifier found: {quoted_id}",
                                "severity": ValidationSeverity.WARNING.value,
                                "path": context.get_path(f"source_columns_interested[{i}]"),
                                "mapping": mapping_name,
                                "expression": column_expr,
                                "suggestion": "Remove empty quoted identifiers or add content",
                            }
                        )

                    # Check for nested quotes (potential escaping issue)
                    inner_content = quoted_id[1:-1]  # Remove outer quotes
                    if '"' in inner_content:
                        warnings.append(
                            {
                                "type": "nested_quotes_in_identifier",
                                "message": f"Nested quotes in identifier may need escaping: {quoted_id}",
                                "severity": ValidationSeverity.WARNING.value,
                                "path": context.get_path(f"source_columns_interested[{i}]"),
                                "mapping": mapping_name,
                                "expression": column_expr,
                                "suggestion": "Ensure proper quote escaping for nested quotes",
                            }
                        )

        return warnings

    def _validate_complex_sql_expressions_rule(
        self, mapping: Dict[str, Any], context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """
        Validate complex SQL expressions (CASE, functions, mathematical operations)
        """
        errors = []

        if "source_columns_interested" not in mapping:
            return []

        mapping_name = mapping.get("mapping_name", "unknown")
        source_columns = mapping.get("source_columns_interested", [])

        for i, column_expr in enumerate(source_columns):
            if not isinstance(column_expr, str):
                continue

            # Check for different types of complex expressions
            expression_type = self._identify_expression_type(column_expr)

            if expression_type != "simple":
                # This is a complex expression, validate it has proper alias
                alias = self._extract_alias_from_expression(column_expr)

                if not alias:
                    errors.append(
                        {
                            "type": "complex_expression_missing_alias",
                            "message": f'{expression_type.title()} expression missing required alias: "{column_expr}"',
                            "severity": ValidationSeverity.ERROR.value,
                            "path": context.get_path(f"source_columns_interested[{i}]"),
                            "mapping": mapping_name,
                            "expression": column_expr,
                            "expression_type": expression_type,
                            "suggestion": f'Add "as alias_name" to the {expression_type} expression',
                        }
                    )
                else:
                    # Validate alias naming convention
                    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", alias):
                        errors.append(
                            {
                                "type": "invalid_alias_name",
                                "message": f'Invalid alias name "{alias}" for {expression_type} expression',
                                "severity": ValidationSeverity.ERROR.value,
                                "path": context.get_path(f"source_columns_interested[{i}]"),
                                "mapping": mapping_name,
                                "expression": column_expr,
                                "alias": alias,
                                "suggestion": "Use valid identifier names (letters, numbers, underscores only)",
                            }
                        )

        return errors

    # Helper methods for SQL expression parsing

    def _extract_alias_from_expression(self, expression: str) -> Optional[str]:
        """
        Extract alias from SQL expression if present
        Handles various patterns including CASE statements
        """
        # Normalize whitespace for easier processing
        normalized_expr = " ".join(expression.split())

        # Try different alias patterns

        # 1. CASE statement pattern
        case_match = self.sql_patterns["case_statement"].search(normalized_expr)
        if case_match:
            return case_match.group(1)

        # 2. Function call pattern
        func_match = self.sql_patterns["function_call"].search(normalized_expr)
        if func_match:
            return func_match.group(1)

        # 3. Mathematical expression pattern
        math_match = self.sql_patterns["math_expression"].search(normalized_expr)
        if math_match:
            return math_match.group(1)

        # 4. Concatenation pattern
        concat_match = self.sql_patterns["concat_expression"].search(normalized_expr)
        if concat_match:
            return concat_match.group(1)

        # 5. General alias pattern (should catch most cases)
        alias_match = self.sql_patterns["alias_pattern"].search(normalized_expr)
        if alias_match:
            return alias_match.group(1)

        # 6. Format without "as" keyword (just space between column and alias)
        if normalized_expr.count('"') >= 2:
            no_as_match = re.search(r'"\s+([a-zA-Z_][a-zA-Z0-9_]*)$', normalized_expr)
            if no_as_match:
                return no_as_match.group(1)

        return None

    def _extract_column_name(self, column_expr: str) -> str:
        """
        Extract clean column name from simple column expression
        Handles quoted identifiers and table prefixes
        """
        # Remove whitespace
        clean_expr = column_expr.strip()

        # If it contains 'as', take only the part before 'as'
        if " as " in clean_expr.lower():
            clean_expr = clean_expr.lower().split(" as ")[0].strip()

        # Handle table.column format
        if "." in clean_expr:
            clean_expr = clean_expr.split(".")[-1]

        # Remove quotes if present
        clean_expr = clean_expr.strip("\"'")

        return clean_expr

    def _looks_like_sql_expression(self, column_expr: str) -> bool:
        """
        Determine if a column expression looks like a SQL expression that should have an alias
        """
        # Check for SQL operators and functions that typically need aliases
        sql_indicators = [
            "CASE",
            "case",  # CASE statements
            "||",  # String concatenation
            "+",
            "-",
            "*",
            "/",  # Mathematical operators
            "(",  # Function calls
            "CONCAT",
            "concat",  # Concatenation functions
            "COALESCE",
            "coalesce",  # NULL handling
            "CAST",
            "cast",  # Type conversion
            "SUBSTRING",
            "substring",  # String functions
        ]

        return any(indicator in column_expr for indicator in sql_indicators)

    def _identify_expression_type(self, expression: str) -> str:
        """
        Identify the type of SQL expression
        """
        expr_lower = expression.lower()

        if "case" in expr_lower and "end" in expr_lower:
            return "case_statement"
        elif "||" in expression:
            return "concatenation"
        elif any(op in expression for op in ["+", "-", "*", "/"]):
            return "mathematical"
        elif "(" in expression and ")" in expression:
            return "function_call"
        else:
            return "simple"

    def _validate_expression_structure(
        self, expression: str, alias: str, index: int, mapping_name: str, context: ValidationContext
    ) -> List[Dict[str, Any]]:
        """
        Validate the structure of a SQL expression
        """
        errors = []

        # Check for balanced quotes
        quote_count = expression.count('"')
        if quote_count % 2 != 0:
            errors.append(
                {
                    "type": "unbalanced_quotes",
                    "message": f'Unbalanced quotes in SQL expression: "{expression}"',
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path(f"source_columns_interested[{index}]"),
                    "mapping": mapping_name,
                    "expression": expression,
                    "alias": alias,
                    "suggestion": "Ensure all quotes are properly paired",
                }
            )

        # Check for balanced parentheses
        paren_count = expression.count("(") - expression.count(")")
        if paren_count != 0:
            errors.append(
                {
                    "type": "unbalanced_parentheses",
                    "message": f'Unbalanced parentheses in SQL expression: "{expression}"',
                    "severity": ValidationSeverity.ERROR.value,
                    "path": context.get_path(f"source_columns_interested[{index}]"),
                    "mapping": mapping_name,
                    "expression": expression,
                    "alias": alias,
                    "suggestion": "Ensure all parentheses are properly paired",
                }
            )

        return errors

    def _parse_source_columns(self, mapping: Dict[str, Any]) -> tuple[set[str], set[str]]:
        """
        Parse source_columns_interested to extract aliases and simple column names
        """
        aliases = set()
        simple_columns = set()

        source_columns = mapping.get("source_columns_interested", [])

        for column_expr in source_columns:
            if not isinstance(column_expr, str):
                continue

            alias = self._extract_alias_from_expression(column_expr)
            if alias:
                aliases.add(alias)
            else:
                clean_column = self._extract_column_name(column_expr)
                simple_columns.add(clean_column)

        return aliases, simple_columns

    def validate_sql_expression_mapping(self, yaml_content: Dict[str, Any]) -> ValidationResult:
        """
        Main method to validate SQL expressions in column mapping
        This extends the comprehensive validation with SQL-specific checks
        """
        # Get base comprehensive validation
        base_result = self.validate_comprehensive(yaml_content)

        # Apply SQL expression specific validation
        builder = self.create_result_builder()
        builder.errors.extend(base_result.errors)
        builder.warnings.extend(base_result.warnings)
        builder.info.extend(base_result.info)

        # Add SQL expression validation summary
        if "mappings" in yaml_content:
            sql_expression_count = 0
            mappings_with_sql = 0

            for mapping in yaml_content["mappings"]:
                has_sql_expressions = False
                for column_expr in mapping.get("source_columns_interested", []):
                    if isinstance(column_expr, str) and self._extract_alias_from_expression(
                        column_expr
                    ):
                        sql_expression_count += 1
                        has_sql_expressions = True

                if has_sql_expressions:
                    mappings_with_sql += 1

            builder.add_info(
                "sql_expression_summary",
                f"SQL Expression Analysis: {sql_expression_count} expressions found across {mappings_with_sql} mappings",
                path="root",
            )

        return builder.build()


class GDXConfigValidator(BaseValidator):
    """
    Unified configuration validator using ValidationResult consistently
    Eliminates redundant methods and provides better error context
    """

    def __init__(self, logger=None):
        super().__init__(logger, "GDXConfigValidator")
        self.parser = ComprehensiveYamlValidator(logger)
        self.metrics = ValidationMetrics()

    @validate_with_metrics
    @log_validation_start_end
    def validate(self, job_config: Dict[str, Any]) -> ValidationResult:
        """Main validation method - implements BaseValidator.validate"""
        return self.validate_job_config(job_config)

    @validate_with_metrics
    @log_validation_start_end
    def validate_job_config(self, job_config: Dict[str, Any]) -> ValidationResult:
        """
        Primary job configuration validation method

        Args:
            job_config: Job configuration dictionary

        Returns:
            ValidationResult: Comprehensive validation results
        """
        try:
            # Use the enhanced parser validation
            result = self.parser.validate_comprehensive(job_config)

            # Log results
            if result.is_valid:
                self.log_info("Job configuration validation passed")

                if result.warnings:
                    self.log_warning(f"Job configuration has {len(result.warnings)} warnings")
                    for warning in result.warnings[:3]:  # Log first 3 warnings
                        self.log_warning(f"  - {warning['message']}")

            else:
                self.log_error(
                    f"Job configuration validation failed with {len(result.errors)} errors"
                )
                for error in result.errors[:3]:  # Log first 3 errors
                    self.log_error(f"  - {error['message']}")

            return result

        except Exception as e:
            error_msg = f"Configuration validation failed: {str(e)}"
            self.log_error(error_msg)
            return self._create_exception_result(e, "job_config_validation")

    @validate_with_metrics
    def validate_mapping_config(self, mapping_config: Dict[str, Any]) -> ValidationResult:
        """
        Validate individual mapping configuration

        Args:
            mapping_config: Single mapping configuration

        Returns:
            ValidationResult: Validation results for the mapping
        """
        try:
            # Wrap mapping in structure expected by parser
            wrapped_config = {"mappings": [mapping_config]}

            result = self.parser.validate_comprehensive(wrapped_config)

            mapping_name = mapping_config.get("mapping_name", "unknown")

            if not result.is_valid:
                self.log_error(f"Mapping validation failed for: {mapping_name}")
                for error in result.errors[:3]:
                    self.log_error(f"  - {error['message']}")
            else:
                self.log_info(f"Mapping validation passed for: {mapping_name}")

            # Log warnings regardless of overall validity
            if result.warnings:
                self.log_warning(f"Mapping validation warnings for {mapping_name}:")
                for warning in result.warnings[:3]:
                    self.log_warning(f"  - {warning['message']}")

            return result

        except Exception as e:
            error_msg = f"Mapping validation failed: {str(e)}"
            self.log_error(error_msg)
            return self._create_exception_result(
                e, f"mapping_validation_{mapping_config.get('mapping_name', 'unknown')}"
            )

    @validate_with_metrics
    def validate_transformation_operations(
        self, operations: List[Dict[str, Any]], data_type: str = "VARCHAR(255)"
    ) -> ValidationResult:
        """
        Validate a list of transformation operations

        Args:
            operations: List of transformation operations
            data_type: Target data type for the transformation

        Returns:
            ValidationResult: Validation results for the operations
        """
        try:
            # Create a minimal mapping structure for validation
            test_mapping = {
                "mapping_name": "test_operations",
                "column_transformations": [
                    {
                        "source_alias": "test_source",
                        "target_column": "test_target",
                        "data_type": data_type,
                        "transformation_type": "string_manipulation",
                        "transformations": operations,
                    }
                ],
            }

            result = self.validate_mapping_config(test_mapping)

            # Filter to operation-specific errors/warnings
            operation_result = self._filter_operation_messages(result, operations)

            return operation_result

        except Exception as e:
            error_msg = f"Operation validation failed: {str(e)}"
            self.log_error(error_msg)
            return self._create_exception_result(e, "transformation_operations")

    def validate_numeric_transformation_chain(
        self, operations: List[Dict[str, Any]], data_type: str = "DECIMAL(15,2)"
    ) -> ValidationResult:
        """
        Validate a chain of numeric operations with enhanced numeric analysis

        Args:
            operations: List of numeric transformation operations
            data_type: Target numeric data type

        Returns:
            ValidationResult: Enhanced validation results for numeric operations
        """
        try:
            # Create a test transformation for numeric operations
            test_transformation = {
                "source_alias": "test_numeric_source",
                "target_column": "test_numeric_target",
                "data_type": data_type,
                "transformation_type": "type_conversion",
                "transformations": operations,
            }

            # Wrap in mapping structure
            test_mapping = {
                "mapping_name": "test_numeric_chain",
                "column_transformations": [test_transformation],
            }

            # Validate using comprehensive method
            result = self.validate_job_config({"mappings": [test_mapping]})

            # Filter to numeric-specific messages and enhance them
            numeric_result = self._enhance_numeric_validation_result(result, operations, data_type)

            return numeric_result

        except Exception as e:
            error_msg = f"Numeric chain validation failed: {str(e)}"
            self.log_error(error_msg)
            return self._create_exception_result(e, "numeric_transformation_chain")

    def validate_yaml_file(self, file_path: str) -> ValidationResult:
        """
        Validate a complete YAML file

        Args:
            file_path: Path to YAML file

        Returns:
            ValidationResult: Complete file validation results
        """
        try:
            return self.parser.validate_yaml_file(file_path)
        except Exception as e:
            error_msg = f"YAML file validation failed: {str(e)}"
            self.log_error(error_msg)
            return self._create_exception_result(e, f"yaml_file_{file_path}")

    def validate_yaml_string(self, yaml_string: str) -> ValidationResult:
        """
        Validate a YAML string

        Args:
            yaml_string: YAML content as string

        Returns:
            ValidationResult: String validation results
        """
        try:
            return self.parser.validate_yaml_string(yaml_string)
        except Exception as e:
            error_msg = f"YAML string validation failed: {str(e)}"
            self.log_error(error_msg)
            return self._create_exception_result(e, "yaml_string")

    def get_validation_summary(self, result: ValidationResult) -> str:
        """
        Get human-readable validation summary

        Args:
            result: ValidationResult object

        Returns:
            Formatted summary string
        """
        try:
            return self.parser.get_validation_summary(result)
        except Exception as e:
            self.log_error(f"Error generating validation summary: {str(e)}")
            return f"Validation Summary Error: {str(e)}"

    def get_operation_help(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        Get help information for a specific operation

        Args:
            operation_name: Name of the operation

        Returns:
            Help information dictionary or None if operation not found
        """
        return OPERATION_REGISTRY.get_operation_help(operation_name)

    def get_available_operations(self, category: str = None) -> List[str]:
        """
        Get list of available operations, optionally filtered by category

        Args:
            category: Optional category filter

        Returns:
            List of operation names
        """
        if category:
            return [op.name for op in OPERATION_REGISTRY.get_operations_by_category(category)]
        else:
            return OPERATION_REGISTRY.get_all_operation_names()

    def get_operation_suggestions(self, partial_name: str) -> List[str]:
        """
        Get operation suggestions based on partial name

        Args:
            partial_name: Partial operation name

        Returns:
            List of suggested operation names
        """
        return OPERATION_REGISTRY.get_operation_suggestions(partial_name)

    # Helper methods for result processing
    def _filter_operation_messages(
        self, result: ValidationResult, operations: List[Dict[str, Any]]
    ) -> ValidationResult:
        """Filter validation result to operation-specific messages"""
        builder = self.create_result_builder()

        # Filter errors and warnings related to transformations
        for error in result.errors:
            if "transformations" in error.get("path", ""):
                builder.errors.append(error)

        for warning in result.warnings:
            if "transformations" in warning.get("path", ""):
                builder.warnings.append(warning)

        # Add operation count info
        builder.add_info(
            "operation_validation_summary",
            f"Validated {len(operations)} transformation operations",
            path="operations",
        )

        return builder.build()

    def _enhance_numeric_validation_result(
        self, result: ValidationResult, operations: List[Dict[str, Any]], data_type: str
    ) -> ValidationResult:
        """Enhance validation result with numeric-specific analysis"""
        builder = self.create_result_builder()

        # Copy existing errors and warnings
        builder.errors = result.errors.copy()
        builder.warnings = result.warnings.copy()

        # Add numeric-specific analysis
        numeric_ops = [
            op
            for op in operations
            if op.get("type")
            in [
                "round",
                "ceil",
                "floor",
                "add",
                "subtract",
                "multiply",
                "divide",
                "power",
                "sqrt",
                "abs",
                "mod",
                "parse_number",
                "parse_currency",
            ]
        ]

        if numeric_ops:
            builder.add_info(
                "numeric_analysis",
                f"Found {len(numeric_ops)} numeric operations in chain of {len(operations)} total operations",
                path="numeric_operations",
            )

            # Check for potential precision issues
            if len(numeric_ops) > 3:
                builder.add_warning(
                    "numeric_precision_risk",
                    f"Long numeric operation chain ({len(numeric_ops)} operations) may cause precision loss",
                    path="numeric_operations",
                    suggestion="Consider using fewer operations or sql_expression for complex calculations",
                )

            # Check data type compatibility
            if "DECIMAL" in data_type.upper() or "NUMERIC" in data_type.upper():
                builder.add_info(
                    "data_type_compatibility",
                    f"Numeric operations are compatible with target type: {data_type}",
                    path="data_type",
                )

        return builder.build()

    def _create_exception_result(self, exception: Exception, context: str) -> ValidationResult:
        """Create ValidationResult from exception with context"""
        return create_exception_result(exception, context=context)

    # Backward compatibility methods (DEPRECATED)
    def validate_job_config_legacy(self, job_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        DEPRECATED: Legacy method returning tuple format
        Use validate_job_config() instead for ValidationResult
        """
        self.log_warning(
            "validate_job_config_legacy is deprecated. Use validate_job_config() instead."
        )

        result = self.validate_job_config(job_config)
        error_messages = [error["message"] for error in result.errors]
        return result.is_valid, error_messages

    def validate_job_config_comprehensive_legacy(
        self, job_config: Dict[str, Any]
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        DEPRECATED: Legacy method returning complex tuple format
        Use validate_job_config() instead for ValidationResult
        """
        self.log_warning(
            "validate_job_config_comprehensive_legacy is deprecated. Use validate_job_config() instead."
        )

        result = self.validate_job_config(job_config)
        error_messages = [error["message"] for error in result.errors]

        # Build detailed results dictionary for backward compatibility
        detailed_results = {
            "validation_summary": {
                "total_errors": len(result.errors),
                "total_warnings": len(result.warnings),
                "total_info": len(result.info),
                "numeric_transformations_found": self._count_numeric_transformations(job_config),
                "complex_chains_found": self._count_complex_chains(job_config),
            },
            "errors": result.errors,
            "warnings": result.warnings,
            "info": result.info,
            "is_valid": result.is_valid,
            "transformation_analysis": self._analyze_transformations(job_config),
        }

        return result.is_valid, error_messages, detailed_results

    def validate_mapping_config_legacy(self, mapping_config: Dict[str, Any]) -> bool:
        """
        DEPRECATED: Legacy method returning simple boolean
        Use validate_mapping_config() instead for ValidationResult
        """
        self.log_warning(
            "validate_mapping_config_legacy is deprecated. Use validate_mapping_config() instead."
        )

        result = self.validate_mapping_config(mapping_config)
        return result.is_valid

    # Analysis methods for backward compatibility
    def _count_numeric_transformations(self, job_config: Dict[str, Any]) -> int:
        """Count numeric transformations in config"""
        count = 0
        numeric_ops = [
            "parse_number",
            "parse_currency",
            "round",
            "ceil",
            "floor",
            "add",
            "subtract",
            "multiply",
            "divide",
            "power",
            "sqrt",
            "abs",
            "mod",
            "min_value",
            "max_value",
            "clamp",
            "format_number",
        ]

        for mapping in job_config.get("mappings", []):
            for transform in mapping.get("column_transformations", []):
                for operation in transform.get("transformations", []):
                    if operation.get("type") in numeric_ops:
                        count += 1

        return count

    def _count_complex_chains(self, job_config: Dict[str, Any]) -> int:
        """Count complex transformation chains"""
        count = 0

        for mapping in job_config.get("mappings", []):
            for transform in mapping.get("column_transformations", []):
                operations = transform.get("transformations", [])
                if len(operations) > 3:  # Consider 4+ operations as complex
                    count += 1

        return count

    def _analyze_transformations(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transformation patterns"""
        analysis = {
            "transformation_types": {},
            "operation_types": {},
            "avg_chain_length": 0,
            "max_chain_length": 0,
            "data_type_distribution": {},
        }

        total_chains = 0
        total_operations = 0

        for mapping in job_config.get("mappings", []):
            for transform in mapping.get("column_transformations", []):
                # Track transformation types
                trans_type = transform.get("transformation_type", "unknown")
                analysis["transformation_types"][trans_type] = (
                    analysis["transformation_types"].get(trans_type, 0) + 1
                )

                # Track data types
                data_type = transform.get("data_type", "unknown").split("(")[0].upper()
                analysis["data_type_distribution"][data_type] = (
                    analysis["data_type_distribution"].get(data_type, 0) + 1
                )

                # Track operations
                operations = transform.get("transformations", [])
                if operations:
                    total_chains += 1
                    chain_length = len(operations)
                    total_operations += chain_length
                    analysis["max_chain_length"] = max(analysis["max_chain_length"], chain_length)

                    for operation in operations:
                        op_type = operation.get("type", "unknown")
                        analysis["operation_types"][op_type] = (
                            analysis["operation_types"].get(op_type, 0) + 1
                        )

        if total_chains > 0:
            analysis["avg_chain_length"] = round(total_operations / total_chains, 2)

        return analysis


class GDXJobValidator(BaseValidator):
    """
    Enterprise validation wrapper for GDX replication jobs.
    Enhanced with flexible logging and comprehensive validation capabilities.
    """

    def __init__(self, logger=None, validation_mode: str = "comprehensive", silent: bool = False):
        """
        Initialize the GDX Job Validator

        Args:
            logger: Logger instance for validation reporting (GDX framework, standard logging, etc.)
            validation_mode: "comprehensive" or "standard" validation mode
            silent: Force silent logging for this validator
        """
        super().__init__(logger, "GDXJobValidator", silent)
        self.validation_mode = validation_mode
        self.comprehensive_validator = ComprehensiveYamlValidator(logger=logger)

        # Validation metrics tracking
        self.validation_history = []
        self.performance_metrics = {}

        if self.is_logging_enabled():
            self.log_info(f"GDXJobValidator initialized with {validation_mode} mode")
            if self.has_external_logger():
                self.log_debug("Using external logger (GDX framework integration)")
            else:
                self.log_debug("Using standalone console logging")

    def validate(self, data: Any) -> ValidationResult:
        """Main validation method - implements BaseValidator.validate"""
        result = self.comprehensive_validator.validate_comprehensive(data)
        self._store_validation_result("validation", result)
        return result

    def validate_job_configuration(self, job_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate the entire job configuration

        Args:
            job_config: Complete job configuration dictionary

        Returns:
            Tuple[bool, str]: (is_valid, summary_message)
        """
        try:
            if self.is_logging_enabled():
                self.log_info("Starting comprehensive job configuration validation")

            # Perform comprehensive validation
            result = self.comprehensive_validator.validate_comprehensive(job_config)

            # Store validation result for history
            self._store_validation_result("job_config", result)

            if result.is_valid:
                if self.is_logging_enabled():
                    self.log_info("SUCCESS: Comprehensive job configuration validation PASSED")

                # Log validation insights
                self._log_job_validation_insights(result)

                summary = (
                    f"Job configuration validation passed with {len(result.warnings)} warnings"
                )
                return True, summary
            else:
                if self.is_logging_enabled():
                    self.log_error("ERROR: Comprehensive job configuration validation FAILED")

                # Enhanced error reporting
                self._report_job_validation_errors(result)

                summary = f"Job configuration validation failed with {len(result.errors)} errors"
                return False, summary

        except Exception as e:
            error_msg = f"Error during job configuration validation: {str(e)}"
            if self.is_logging_enabled():
                self.log_error(f"ERROR: {error_msg}")
                self.log_error(traceback.format_exc())
            return False, error_msg

    def validate_mapping_configuration(self, mapping_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a single mapping configuration

        Args:
            mapping_config: Single mapping configuration dictionary

        Returns:
            Tuple[bool, str]: (is_valid, summary_message)
        """
        try:
            mapping_name = mapping_config.get("mapping_name", "unknown")

            if "column_transformations" not in mapping_config:
                if self.is_logging_enabled():
                    self.log_info(
                        f"No column transformations in {mapping_name}, validating other sections..."
                    )

            # Wrap single mapping for comprehensive validation
            wrapped_config = {"mappings": [mapping_config]}
            result = self.comprehensive_validator.validate_comprehensive(wrapped_config)

            # Store validation result
            self._store_validation_result(f"mapping_{mapping_name}", result)

            if not result.is_valid:
                if self.is_logging_enabled():
                    self.log_error(f" Comprehensive validation failed for {mapping_name}")

                # Report mapping-specific errors
                self._report_mapping_validation_errors(result, mapping_name)

                summary = (
                    f"Mapping {mapping_name} validation failed with {len(result.errors)} errors"
                )
                return False, summary

            # Success case
            if self.is_logging_enabled():
                self.log_info(f"SUCCESS: Comprehensive validation passed for {mapping_name}")

            # Log insights for successful validation
            self._log_mapping_validation_insights(result, mapping_name)

            summary = (
                f"Mapping {mapping_name} validation passed with {len(result.warnings)} warnings"
            )
            return True, summary

        except Exception as e:
            error_msg = f"Error in mapping validation: {str(e)}"
            if self.is_logging_enabled():
                self.log_error(f"ERROR: {error_msg}")
                self.log_error(traceback.format_exc())
            return False, error_msg

    def validate_all_mappings(
        self, job_config: Dict[str, Any]
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate all mappings in a job configuration

        Args:
            job_config: Complete job configuration

        Returns:
            Tuple[bool, List[Dict]]: (all_valid, validation_results)
        """
        mappings = job_config.get("mappings", [])
        validation_results = []
        all_valid = True

        if self.is_logging_enabled():
            self.log_info(f" Validating {len(mappings)} mappings...")

        for i, mapping in enumerate(mappings):
            mapping_name = mapping.get("mapping_name", f"mapping_{i}")
            is_valid, summary = self.validate_mapping_configuration(mapping)

            validation_results.append(
                {"mapping_name": mapping_name, "is_valid": is_valid, "summary": summary, "index": i}
            )

            if not is_valid:
                all_valid = False

        if self.is_logging_enabled():
            valid_count = sum(1 for r in validation_results if r["is_valid"])
            self.log_info(f"Mapping validation complete: {valid_count}/{len(mappings)} valid")

        return all_valid, validation_results

    def get_validation_summary(self, job_config: Dict[str, Any]) -> str:
        """
        Generate comprehensive validation summary

        Args:
            job_config: Job configuration to analyze

        Returns:
            str: Formatted validation summary
        """
        try:
            # Perform validation to get results
            result = self.comprehensive_validator.validate_comprehensive(job_config)

            summary_lines = []
            summary_lines.append("=" * 60)
            summary_lines.append("GDX JOB COMPREHENSIVE VALIDATION SUMMARY")
            summary_lines.append("=" * 60)

            # Overall status
            status = "SUCCESS VALID" if result.is_valid else " INVALID"
            summary_lines.append(f"Overall Status: {status}")
            summary_lines.append(f"Validation Mode: {self.validation_mode.upper()}")
            summary_lines.append("")

            # Validation counts
            summary_lines.append(f"Validation Results:")
            summary_lines.append(f"  • Errors: {len(result.errors)}")
            summary_lines.append(f"  • Warnings: {len(result.warnings)}")
            summary_lines.append(f"  • Info messages: {len(result.info)}")
            summary_lines.append("")

            # Section analysis
            if "mappings" in job_config:
                mappings_count = len(job_config["mappings"])
                affected_mappings = result.get_affected_mappings()
                summary_lines.append(f"Mapping Analysis:")
                summary_lines.append(f"  • Total mappings: {mappings_count}")
                summary_lines.append(f"  • Mappings with issues: {len(affected_mappings)}")
                if affected_mappings:
                    summary_lines.append(
                        f"  • Affected mappings: {', '.join(list(affected_mappings)[:3])}"
                    )
                summary_lines.append("")

            # Settings analysis
            if "settings" in job_config:
                settings = job_config["settings"]
                summary_lines.append(f"Settings Analysis:")
                summary_lines.append(f"  • Load mode: {settings.get('load', 'not_specified')}")
                summary_lines.append(f"  • Environment: {settings.get('env', 'not_specified')}")
                summary_lines.append(
                    f"  • Has partition settings: {'default_partition_settings' in settings}"
                )
                summary_lines.append("")

            # Error breakdown
            if result.errors:
                error_summary = result.get_error_summary()
                summary_lines.append(f"Top Error Types:")
                for error_type, count in list(error_summary.items())[:5]:
                    summary_lines.append(f"  • {error_type}: {count}")
                summary_lines.append("")

            # Cross-section consistency
            consistency_issues = self._calculate_consistency_score(result)
            summary_lines.append(f" Cross-Section Consistency:")
            summary_lines.append(f"  • Consistency score: {consistency_issues['score']}/100")
            summary_lines.append(f"  • Issues found: {consistency_issues['total_issues']}")
            summary_lines.append("")

            # Performance metrics
            if result.performance_metrics:
                metrics = result.performance_metrics
                summary_lines.append(f" Performance Metrics:")
                summary_lines.append(
                    f"  • Validation time: {metrics.get('duration_seconds', 0):.3f}s"
                )
                summary_lines.append(
                    f"  • Operations validated: {metrics.get('operations_validated', 0)}"
                )
                summary_lines.append(
                    f"  • Transformations validated: {metrics.get('transformations_validated', 0)}"
                )
                summary_lines.append("")

            # Top suggestions
            suggestions = result.get_suggestions()
            if suggestions:
                summary_lines.append(f"Top Suggestions:")
                for suggestion in suggestions[:3]:
                    summary_lines.append(f"  • {suggestion}")
                summary_lines.append("")

            # Validation history summary
            if self.validation_history:
                summary_lines.append(f"📈 Validation History:")
                summary_lines.append(
                    f"  • Total validations performed: {len(self.validation_history)}"
                )
                recent_validations = [v for v in self.validation_history if v["result"].is_valid]
                summary_lines.append(
                    f"  • Recent successful validations: {len(recent_validations)}"
                )
                summary_lines.append("")

            summary_lines.append("=" * 60)

            return "\n".join(summary_lines)

        except Exception as e:
            error_msg = f"Error generating validation summary: {str(e)}"
            if self.is_logging_enabled():
                self.log_error(f" {error_msg}")
            return error_msg

    def get_validation_report(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed validation report for programmatic use

        Args:
            job_config: Job configuration to analyze

        Returns:
            Dict: Detailed validation report
        """
        try:
            result = self.comprehensive_validator.validate_comprehensive(job_config)

            return {
                "overall_status": "valid" if result.is_valid else "invalid",
                "validation_mode": self.validation_mode,
                "summary": {
                    "error_count": len(result.errors),
                    "warning_count": len(result.warnings),
                    "info_count": len(result.info),
                    "affected_mappings": list(result.get_affected_mappings()),
                    "success_rate": (1.0 if result.is_valid else 0.0),
                },
                "errors": result.errors,
                "warnings": result.warnings,
                "info": result.info,
                "error_summary": result.get_error_summary(),
                "warning_summary": result.get_warning_summary(),
                "suggestions": result.get_suggestions(),
                "performance_metrics": result.performance_metrics,
                "consistency_analysis": self._calculate_consistency_score(result),
                "validation_metadata": {
                    "timestamp": self._get_current_timestamp(),
                    "validator_version": "1.0.0",
                    "validation_history_count": len(self.validation_history),
                },
            }

        except Exception as e:
            return {
                "overall_status": "error",
                "error_message": str(e),
                "validation_mode": self.validation_mode,
            }

    def set_validation_mode(self, mode: str = "comprehensive"):
        """
        Set validation mode

        Args:
            mode: "comprehensive" or "standard"
        """
        if mode not in ["comprehensive", "standard"]:
            if self.is_logging_enabled():
                self.log_warning(f"Invalid validation mode: {mode}. Using 'comprehensive'")
            mode = "comprehensive"

        self.validation_mode = mode
        if self.is_logging_enabled():
            self.log_info(f"Validation mode set to: {mode}")

        # Recreate validator if switching modes
        if mode == "standard":
            self.comprehensive_validator = GDXYamlParser(logger=self._original_logger)
            if self.is_logging_enabled():
                self.log_info("Switched to standard validation mode")

    def clear_validation_history(self):
        """Clear validation history for memory management"""
        self.validation_history.clear()
        if self.is_logging_enabled():
            self.log_info("🧹 Validation history cleared")

    # ==========================================
    # PRIVATE HELPER METHODS
    # ==========================================

    def _store_validation_result(self, validation_type: str, result: ValidationResult):
        """Store validation result in history"""
        self.validation_history.append(
            {
                "type": validation_type,
                "timestamp": self._get_current_timestamp(),
                "result": result,
                "is_valid": result.is_valid,
                "error_count": len(result.errors),
                "warning_count": len(result.warnings),
            }
        )

        # Keep only last 50 validations for memory management
        if len(self.validation_history) > 50:
            self.validation_history = self.validation_history[-50:]

    def _report_job_validation_errors(self, result: ValidationResult):
        """Report job-level validation errors by section"""
        if not self.is_logging_enabled():
            return

        # Group errors by section
        error_by_section = {}
        warning_by_section = {}

        for error in result.errors:
            path = error.get("path", "unknown")
            section = path.split(".")[0] if "." in path else path.split("[")[0]
            if section not in error_by_section:
                error_by_section[section] = []
            error_by_section[section].append(error["message"])

        for warning in result.warnings:
            path = warning.get("path", "unknown")
            section = path.split(".")[0] if "." in path else path.split("[")[0]
            if section not in warning_by_section:
                warning_by_section[section] = []
            warning_by_section[section].append(warning["message"])

        # Report errors by section
        self.log_error(
            f"Found {len(result.errors)} validation errors across {len(error_by_section)} sections:"
        )
        for section, errors in error_by_section.items():
            self.log_error(f"  📍 {section}: {len(errors)} errors")
            for i, error_msg in enumerate(errors[:2], 1):
                self.log_error(f"    {i}. {error_msg}")
            if len(errors) > 2:
                self.log_error(f"    ... and {len(errors) - 2} more errors in {section}")

        # Report warnings by section
        if warning_by_section:
            self.log_warning(
                f"Found {len(result.warnings)} warnings across {len(warning_by_section)} sections:"
            )
            for section, warnings in warning_by_section.items():
                self.log_warning(f"  📍 {section}: {len(warnings)} warnings")

    def _report_mapping_validation_errors(self, result: ValidationResult, mapping_name: str):
        """Report mapping-specific validation errors"""
        if not self.is_logging_enabled():
            return

        # Enhanced error reporting with section details
        error_sections = set()
        for error in result.errors:
            path = error.get("path", "")
            section = path.split(".")[0] if "." in path else path.split("[")[0]
            error_sections.add(section)

            self.log_error(f"[{error.get('path', 'unknown')}] {error['message']}")

            # Log suggestions if available
            if "suggestion" in error and error["suggestion"]:
                self.log_info(f"Suggestion: {error['suggestion']}")

            # Log operation context if available
            if "operation_type" in error:
                self.log_info(f"Operation: {error['operation_type']}")

        # Report which sections had errors
        if error_sections:
            self.log_error(f" Sections with errors in {mapping_name}: {', '.join(error_sections)}")

    def _log_job_validation_insights(self, result: ValidationResult):
        """Log job-level validation insights"""
        if not self.is_logging_enabled():
            return

        # Performance metrics
        if result.performance_metrics:
            metrics = result.performance_metrics
            duration = metrics.get("duration_seconds", 0)
            mappings_validated = metrics.get("mappings_validated", 0)
            transformations_validated = metrics.get("transformations_validated", 0)
            operations_validated = metrics.get("operations_validated", 0)

            self.log_info(f"Validation Performance:")
            self.log_info(f"  • Duration: {duration:.3f}s")
            self.log_info(f"  • Mappings: {mappings_validated}")
            if transformations_validated > 0:
                self.log_info(f"  • Transformations: {transformations_validated}")
            if operations_validated > 0:
                self.log_info(f"  • Operations: {operations_validated}")

        # Section coverage analysis
        affected_mappings = result.get_affected_mappings()
        if affected_mappings:
            self.log_info(f"Mappings analyzed: {', '.join(list(affected_mappings)[:5])}")

        # Cross-section consistency
        consistency_score = self._calculate_consistency_score(result)
        if consistency_score["total_issues"] == 0:
            self.log_info(" Cross-section consistency: EXCELLENT (100/100)")
        elif consistency_score["total_issues"] <= 2:
            self.log_warning(f" Cross-section consistency: GOOD ({consistency_score['score']}/100)")
        else:
            self.log_warning(
                f"Cross-section consistency: NEEDS ATTENTION ({consistency_score['score']}/100)"
            )

    def _log_mapping_validation_insights(self, result: ValidationResult, mapping_name: str):
        """Log mapping-specific validation insights"""
        if not self.is_logging_enabled():
            return

        # Warning reporting with sections
        if result.warnings:
            warning_sections = set()
            for warning in result.warnings:
                path = warning.get("path", "")
                section = path.split(".")[0] if "." in path else path.split("[")[0]
                warning_sections.add(section)

            self.log_warning(f"{len(result.warnings)} validation warnings for {mapping_name}")
            if warning_sections:
                self.log_warning(f"Sections with warnings: {', '.join(warning_sections)}")

            # Log first few warnings with suggestions
            for i, warning in enumerate(result.warnings[:3], 1):
                self.log_warning(f"{i}. {warning['message']}")
                if "suggestion" in warning and warning["suggestion"]:
                    self.log_info(f"{warning['suggestion']}")

            if len(result.warnings) > 3:
                self.log_warning(f"... and {len(result.warnings) - 3} more warnings")

        # Performance insights
        if result.performance_metrics:
            metrics = result.performance_metrics
            ops_count = metrics.get("operations_validated", 0)
            duration = metrics.get("duration_seconds", 0)
            if ops_count > 0:
                self.log_info(
                    f"Validated {ops_count} operations in {duration:.3f}s for {mapping_name}"
                )

        # Specific validation insights
        self._log_specific_validation_insights(result)

    def _log_specific_validation_insights(self, result: ValidationResult):
        """Log specific validation insights"""
        if not self.is_logging_enabled():
            return

        # Transformation insights
        transformation_errors = result.get_errors_by_type("invalid_transformation_type")
        if transformation_errors:
            self.log_warning(f"Found {len(transformation_errors)} transformation type issues")

        # Operation insights
        operation_errors = result.get_errors_by_type("invalid_operation_type")
        if operation_errors:
            self.log_warning(f"Found {len(operation_errors)} operation type issues")

        # Cross-section consistency insights
        consistency_errors = [
            "orphaned_mapped_columns",
            "orphaned_duplicated_columns",
            "orphaned_transformation_columns",
        ]
        cross_section_issues = sum(
            len(result.get_errors_by_type(error_type)) for error_type in consistency_errors
        )
        if cross_section_issues > 0:
            self.log_warning(f" Found {cross_section_issues} cross-section consistency issues")

        # Complexity insights
        complex_warnings = result.get_warnings_by_type("complex_transformation_chain")
        if complex_warnings:
            self.log_info(
                f"Found {len(complex_warnings)} complex transformation chains - consider optimization"
            )

        # Numeric precision insights
        numeric_errors = result.get_errors_by_type("numeric_precision_risk")
        if numeric_errors:
            self.log_warning(f"Found {len(numeric_errors)} potential numeric precision issues")

    def _calculate_consistency_score(self, result: ValidationResult) -> Dict[str, Any]:
        """Calculate cross-section consistency score"""
        consistency_errors = [
            "orphaned_mapped_columns",
            "orphaned_duplicated_columns",
            "orphaned_transformation_columns",
        ]

        total_issues = sum(
            len(result.get_errors_by_type(error_type)) for error_type in consistency_errors
        )

        # Calculate score (start with 100, deduct points for issues)
        score = max(0, 100 - (total_issues * 15))  # 15 points per issue

        return {
            "score": score,
            "total_issues": total_issues,
            "error_breakdown": {
                error_type: len(result.get_errors_by_type(error_type))
                for error_type in consistency_errors
            },
        }

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for tracking"""
        import datetime

        return datetime.datetime.now().isoformat()


class ExtendedGDXJobValidator(GDXJobValidator):
    """
    Enhanced GDX Job Validator that includes SQL Expression validation
    alongside all existing comprehensive validation capabilities.
    """

    def __init__(self, logger=None, validation_mode: str = "comprehensive"):
        """
        Initialize the Enhanced GDX Job Validator

        Args:
            logger: Logger instance for validation reporting
            validation_mode: "comprehensive", "standard", or "sql_enhanced"
        """
        super().__init__(logger, validation_mode)

        # Initialize SQL expression validator for extended mode
        if validation_mode == "sql_enhanced":
            self.sql_expression_validator = SQLExpressionColumnValidator(logger=logger)
            if self.is_logging_enabled():
                self.log_info("Enhanced GDX Validator initialized with SQL Expression support")
        else:
            self.sql_expression_validator = None

    def validate_job_configuration(self, job_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Enhanced job configuration validation that includes SQL expressions

        Args:
            job_config: Complete job configuration dictionary

        Returns:
            Tuple[bool, str]: (is_valid, summary_message)
        """
        try:
            if self.is_logging_enabled():
                mode_display = self.validation_mode.upper()
                self.log_info(f"Starting {mode_display} job configuration validation")

            # Choose the appropriate validator based on mode
            if self.validation_mode == "sql_enhanced" and self.sql_expression_validator:
                # Use SQL-extended validation (includes ALL previous validations)
                result = self.sql_expression_validator.validate_sql_expression_mapping(job_config)
                validation_scope = "All YAML sections + SQL Expression validation"
            else:
                # Use the existing comprehensive validation
                result = self.comprehensive_validator.validate_comprehensive(job_config)
                validation_scope = "All YAML sections (standard comprehensive)"

            # Deduplicate errors and warnings before proceeding
            result.errors = self._deduplicate_errors(result.errors)
            result.warnings = self._deduplicate_errors(result.warnings)

            # Store validation result for history
            self._store_validation_result("job_config", result)

            if result.is_valid:
                if self.is_logging_enabled():
                    self.log_info("SUCCESS: Enhanced job configuration validation PASSED")

                # Enhanced logging with SQL expression insights
                self._log_enhanced_job_validation_insights(result, validation_scope)

                summary = f"Job configuration validation passed with {len(result.warnings)} warnings ({validation_scope})"
                return True, summary
            else:
                if self.is_logging_enabled():
                    self.log_error("ERROR: Enhanced job configuration validation FAILED")

                # Enhanced error reporting with SQL expression context
                self._report_enhanced_job_validation_errors(result)

                summary = f"Job configuration validation failed with {len(result.errors)} errors ({validation_scope})"
                return False, summary

        except Exception as e:
            error_msg = f"Error during extended job configuration validation: {str(e)}"
            if self.is_logging_enabled():
                self.log_error(f"ERROR: {error_msg}")
            return False, error_msg

    def validate_mapping_configuration(self, mapping_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Enhanced mapping configuration validation that includes SQL expressions

        Args:
            mapping_config: Single mapping configuration dictionary

        Returns:
            Tuple[bool, str]: (is_valid, summary_message)
        """
        try:
            mapping_name = mapping_config.get("mapping_name", "unknown")

            # Wrap single mapping for validation
            wrapped_config = {"mappings": [mapping_config]}

            # Choose appropriate validator - only run one type of validation
            if self.validation_mode == "sql_enhanced" and self.sql_expression_validator:
                # SQL validator already includes comprehensive validation
                result = self.sql_expression_validator.validate_sql_expression_mapping(
                    wrapped_config
                )
                validation_scope = "Standard + SQL Expression validation"
            else:
                result = self.comprehensive_validator.validate_comprehensive(wrapped_config)
                validation_scope = "Standard comprehensive validation"

            # Deduplicate errors and warnings before proceeding
            result.errors = self._deduplicate_errors(result.errors)
            result.warnings = self._deduplicate_errors(result.warnings)

            # Store validation result
            self._store_validation_result(f"mapping_{mapping_name}", result)

            if not result.is_valid:
                if self.is_logging_enabled():
                    self.log_error(f"Enhanced validation failed for {mapping_name}")

                # Enhanced error reporting with SQL context (now with deduplication)
                self._report_enhanced_mapping_validation_errors(result, mapping_name)

                summary = f"Mapping {mapping_name} validation failed with {len(result.errors)} errors ({validation_scope})"
                return False, summary

            # Success case
            if self.is_logging_enabled():
                self.log_info(f"SUCCESS: Enhanced validation passed for {mapping_name}")

            # Enhanced insights logging
            self._log_enhanced_mapping_validation_insights(result, mapping_name, validation_scope)

            summary = f"Mapping {mapping_name} validation passed with {len(result.warnings)} warnings ({validation_scope})"
            return True, summary

        except Exception as e:
            error_msg = f"Error in extended mapping validation: {str(e)}"
            if self.is_logging_enabled():
                self.log_error(f"ERROR: {error_msg}")
            return False, error_msg

    def get_validation_summary(self, job_config: Dict[str, Any]) -> str:
        """
        Generate extended validation summary with SQL expression insights
        """
        try:
            # Choose appropriate validator
            if self.validation_mode == "sql_enhanced" and self.sql_expression_validator:
                result = self.sql_expression_validator.validate_sql_expression_mapping(job_config)
            else:
                result = self.comprehensive_validator.validate_comprehensive(job_config)

            summary_lines = []
            summary_lines.append("=" * 70)
            summary_lines.append("GDX JOB VALIDATION SUMMARY")
            summary_lines.append("=" * 70)

            # Overall status with extended context
            status = "SUCCESS VALID" if result.is_valid else "INVALID"
            summary_lines.append(f"Overall Status: {status}")
            summary_lines.append(f"Validation Mode: {self.validation_mode.upper()}")

            # Enhanced scope information
            if self.validation_mode == "sql_enhanced":
                summary_lines.append(
                    f"Validation Scope: Column Transformations + All YAML Sections + SQL Expressions"
                )
            else:
                summary_lines.append(
                    f"Validation Scope: Column Transformations + All YAML Sections"
                )
            summary_lines.append("")

            # Validation counts
            summary_lines.append(f"Validation Results:")
            summary_lines.append(f"  • Errors: {len(result.errors)}")
            summary_lines.append(f"  • Warnings: {len(result.warnings)}")
            summary_lines.append(f"  • Info messages: {len(result.info)}")
            summary_lines.append("")

            # SQL Expression specific analysis (if applicable)
            if self.validation_mode == "sql_enhanced":
                sql_analysis = self._analyze_sql_expression_results(result, job_config)
                if sql_analysis["has_sql_expressions"]:
                    summary_lines.append(f"SQL Expression Analysis:")
                    summary_lines.append(
                        f"  • SQL expressions found: {sql_analysis['expression_count']}"
                    )
                    summary_lines.append(
                        f"  • Mappings with SQL expressions: {sql_analysis['mappings_with_sql']}"
                    )
                    summary_lines.append(f"  • SQL expression errors: {sql_analysis['sql_errors']}")
                    summary_lines.append(
                        f"  • SQL expression warnings: {sql_analysis['sql_warnings']}"
                    )
                    summary_lines.append("")

            # Section analysis (inherited from parent)
            if "mappings" in job_config:
                mappings_count = len(job_config["mappings"])
                affected_mappings = result.get_affected_mappings()
                summary_lines.append(f"Mapping Analysis:")
                summary_lines.append(f"  • Total mappings: {mappings_count}")
                summary_lines.append(f"  • Mappings with issues: {len(affected_mappings)}")
                if affected_mappings:
                    summary_lines.append(
                        f"  • Affected mappings: {', '.join(list(affected_mappings)[:3])}"
                    )
                summary_lines.append("")

            # Error breakdown with extended categorization
            if result.errors:
                error_summary = result.get_error_summary()
                summary_lines.append(f"Top Error Types:")

                # Categorize errors
                sql_errors = []
                standard_errors = []

                for error_type, count in list(error_summary.items())[:10]:
                    if any(
                        sql_keyword in error_type
                        for sql_keyword in ["sql", "expression", "alias", "mapping"]
                    ):
                        sql_errors.append((error_type, count))
                    else:
                        standard_errors.append((error_type, count))

                # Show SQL errors first if any
                if sql_errors:
                    summary_lines.append(f"SQL Expression Related:")
                    for error_type, count in sql_errors[:3]:
                        summary_lines.append(f"    • {error_type}: {count}")

                # Show other errors
                if standard_errors:
                    summary_lines.append(f"General Validation:")
                    for error_type, count in standard_errors[:3]:
                        summary_lines.append(f"    • {error_type}: {count}")

                summary_lines.append("")

            # Enhanced suggestions with SQL context
            suggestions = result.get_suggestions()
            if suggestions:
                summary_lines.append(f"Top Suggestions:")

                # Prioritize SQL-related suggestions
                sql_suggestions = [
                    s
                    for s in suggestions
                    if any(
                        keyword in s.lower()
                        for keyword in ["alias", "expression", "sql", "mapping"]
                    )
                ]
                other_suggestions = [s for s in suggestions if s not in sql_suggestions]

                for suggestion in (sql_suggestions + other_suggestions)[:5]:
                    summary_lines.append(f"  • {suggestion}")
                summary_lines.append("")

            # Performance metrics
            if result.performance_metrics:
                metrics = result.performance_metrics
                summary_lines.append(f"Performance Metrics:")
                summary_lines.append(
                    f"  • Validation time: {metrics.get('duration_seconds', 0):.3f}s"
                )
                summary_lines.append(
                    f"  • Operations validated: {metrics.get('operations_validated', 0)}"
                )
                summary_lines.append(
                    f"  • Transformations validated: {metrics.get('transformations_validated', 0)}"
                )
                summary_lines.append("")

            summary_lines.append("=" * 70)

            return "\n".join(summary_lines)

        except Exception as e:
            error_msg = f"Error generating extended validation summary: {str(e)}"
            if self.is_logging_enabled():
                self.log_error(f"{error_msg}")
            return error_msg

    def set_validation_mode(self, mode: str = "comprehensive"):
        """
        Set validation mode with SQL expression support

        Args:
            mode: "comprehensive", "standard", or "sql_enhanced"
        """
        if mode not in ["comprehensive", "standard", "sql_enhanced"]:
            if self.is_logging_enabled():
                self.log_warning(f"Invalid validation mode: {mode}. Using 'comprehensive'")
            mode = "comprehensive"

        self.validation_mode = mode

        # Initialize SQL expression validator if needed
        if mode == "sql_enhanced":
            self.sql_expression_validator = SQLExpressionColumnValidator(
                logger=self._original_logger
            )
            if self.is_logging_enabled():
                self.log_info("🔧 Enabled SQL Expression validation mode")
        else:
            self.sql_expression_validator = None

        if self.is_logging_enabled():
            self.log_info(f"Validation mode set to: {mode}")

    # Enhanced helper methods

    def _log_enhanced_job_validation_insights(
        self, result: ValidationResult, validation_scope: str
    ):
        """Enhanced job-level validation insights with SQL expression context"""
        if not self.is_logging_enabled():
            return

        # Call parent method first
        self._log_job_validation_insights(result)

        # Add SQL-specific insights
        if self.validation_mode == "sql_enhanced":
            sql_analysis = self._analyze_sql_expression_results(result, {})
            if sql_analysis["has_sql_expressions"]:
                self.log_info(f"SQL Expression Insights:")
                self.log_info(f"Found {sql_analysis['expression_count']} SQL expressions")
                self.log_info(f"{sql_analysis['mappings_with_sql']} mappings use SQL expressions")

                if sql_analysis["sql_errors"] == 0:
                    self.log_info("All SQL expressions properly configured")
                else:
                    self.log_warning(f"{sql_analysis['sql_errors']} SQL expression issues found")

    def _report_enhanced_job_validation_errors(self, result: ValidationResult):
        """Enhanced job-level error reporting with SQL expression context"""
        if not self.is_logging_enabled():
            return

        # Deduplicate errors before reporting
        deduplicated_errors = self._deduplicate_errors(result.errors)

        # Separate SQL expression errors from others
        sql_errors = []
        other_errors = []

        for error in deduplicated_errors:
            error_type = error.get("type", "")
            if any(keyword in error_type for keyword in ["sql", "expression", "alias", "mapping"]):
                sql_errors.append(error)
            else:
                other_errors.append(error)

        # Report SQL expression errors first
        if sql_errors:
            self.log_error(f"Found {len(sql_errors)} SQL Expression related errors:")
            for error in sql_errors[:3]:
                self.log_error(f"[{error.get('path', 'unknown')}] {error['message']}")
                if "suggestion" in error:
                    self.log_info(f"{error['suggestion']}")

        # Report other errors
        if other_errors:
            self.log_error(f"Found {len(other_errors)} general validation errors:")
            for error in other_errors[:3]:
                self.log_error(f"[{error.get('path', 'unknown')}] {error['message']}")

    def _report_enhanced_mapping_validation_errors(
        self, result: ValidationResult, mapping_name: str
    ):
        """Enhanced mapping-specific error reporting with SQL expression context"""
        if not self.is_logging_enabled():
            return

        # Deduplicate errors before reporting
        deduplicated_errors = self._deduplicate_errors(result.errors)

        # Separate SQL errors from other errors
        sql_errors = []
        other_errors = []

        for error in deduplicated_errors:
            if any(
                k in error.get("type", "").lower()
                for k in ["sql", "expression", "alias", "mapping"]
            ):
                sql_errors.append(error)
            else:
                other_errors.append(error)

        # Log SQL errors first, only once
        if sql_errors:
            self.log_error(f"SQL Expression errors in {mapping_name}:")
            for error in sql_errors:
                self.log_error(f"  [{error.get('path', 'unknown')}] {error['message']}")

                # Only show available columns once per error
                if "available_columns" in error:
                    avail = sorted(error.get("available_columns", []))
                    if avail:
                        self.log_info(f"  Available aliases: {', '.join(avail)}")

                # Show suggestion only once
                if "suggestion" in error and error["suggestion"]:
                    self.log_info(f"  Suggestion: {error['suggestion']}")

        # Log other errors without duplicating them
        if other_errors and not sql_errors:  # Only if no SQL errors were reported
            self.log_error(f"Validation errors in {mapping_name}:")
            for error in other_errors:
                self.log_error(f"  [{error.get('path', 'unknown')}] {error['message']}")

                # Only show available columns once per error
                if "available_columns" in error:
                    avail = sorted(error.get("available_columns", []))
                    if avail:
                        self.log_info(f"  Available aliases: {', '.join(avail)}")

                # Show suggestion only once
                if "suggestion" in error and error["suggestion"]:
                    self.log_info(f"  Suggestion: {error['suggestion']}")

    def _log_enhanced_mapping_validation_insights(
        self, result: ValidationResult, mapping_name: str, validation_scope: str
    ):
        """Enhanced mapping-specific insights with SQL expression context"""
        if not self.is_logging_enabled():
            return

        # Call parent method first
        self._log_mapping_validation_insights(result, mapping_name)

        # Add SQL-specific insights for this mapping
        if self.validation_mode == "sql_enhanced":
            sql_expression_count = 0
            for info in result.info:
                if "SQL Expression Analysis" in info.get("message", ""):
                    # Extract count from message if possible
                    message = info["message"]
                    if "expressions found" in message:
                        try:
                            sql_expression_count = int(message.split()[3])
                        except (IndexError, ValueError):
                            pass

            if sql_expression_count > 0:
                self.log_info(f"🔧 {mapping_name} uses {sql_expression_count} SQL expressions")

    def _analyze_sql_expression_results(
        self, result: ValidationResult, job_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze SQL expression specific results"""
        analysis = {
            "has_sql_expressions": False,
            "expression_count": 0,
            "mappings_with_sql": 0,
            "sql_errors": 0,
            "sql_warnings": 0,
        }

        # Count SQL-related errors and warnings
        sql_keywords = ["sql", "expression", "alias", "mapping"]

        for error in result.errors:
            if any(keyword in error.get("type", "").lower() for keyword in sql_keywords):
                analysis["sql_errors"] += 1

        for warning in result.warnings:
            if any(keyword in warning.get("type", "").lower() for keyword in sql_keywords):
                analysis["sql_warnings"] += 1

        # Extract SQL expression count from info messages
        for info in result.info:
            message = info.get("message", "")
            if "SQL Expression Analysis" in message:
                analysis["has_sql_expressions"] = True
                # Try to extract numbers from the message
                try:
                    parts = message.split()
                    for i, part in enumerate(parts):
                        if part.isdigit():
                            if "expressions" in " ".join(parts[i : i + 2]):
                                analysis["expression_count"] = int(part)
                            elif "mappings" in " ".join(parts[i : i + 2]):
                                analysis["mappings_with_sql"] = int(part)
                except (IndexError, ValueError):
                    pass

        return analysis

    def _deduplicate_errors(self, errors):
        """
        Remove duplicate errors based on type, message and path

        Args:
            errors: List of error dictionaries

        Returns:
            List: Deduplicated error list
        """
        unique_errors = []
        seen_errors = set()

        for error in errors:
            # Create a unique identifier for each error
            error_id = (error.get("type", ""), error.get("message", ""), error.get("path", ""))

            if error_id not in seen_errors:
                seen_errors.add(error_id)
                unique_errors.append(error)

        return unique_errors


# Convenience functions for working with validators
def create_job_validator(logger=None, mode: str = "comprehensive") -> GDXJobValidator:
    """
    Factory function to create a GDX Job Validator

    Args:
        logger: Logger instance
        mode: Validation mode

    Returns:
        GDXJobValidator: Configured validator instance
    """
    return GDXJobValidator(logger=logger, validation_mode=mode)


def validate_gdx_job_config(job_config: Dict[str, Any], logger=None) -> Tuple[bool, str]:
    """
    Quick validation function for GDX job configuration

    Args:
        job_config: Job configuration dictionary
        logger: Optional logger

    Returns:
        Tuple[bool, str]: (is_valid, summary)
    """
    validator = create_job_validator(logger=logger)
    return validator.validate_job_configuration(job_config)


def validate_gdx_mapping_config(mapping_config: Dict[str, Any], logger=None) -> Tuple[bool, str]:
    """
    Quick validation function for GDX mapping configuration

    Args:
        mapping_config: Mapping configuration dictionary
        logger: Optional logger

    Returns:
        Tuple[bool, str]: (is_valid, summary)
    """
    validator = create_job_validator(logger=logger)
    return validator.validate_mapping_configuration(mapping_config)


def create_extended_gdx_job_validator(
    logger=None, mode: str = "sql_enhanced"
) -> ExtendedGDXJobValidator:
    """
    Factory function to create an Enhanced GDX Job Validator with SQL Expression support

    Args:
        logger: Logger instance
        mode: "comprehensive", "standard", or "sql_enhanced"

    Returns:
        ExtendedGDXJobValidator: Configured validator instance
    """
    return ExtendedGDXJobValidator(logger=logger, validation_mode=mode)


def validate_gdx_job_config_with_sql(job_config: Dict[str, Any], logger=None) -> Tuple[bool, str]:
    """
    Quick validation function for GDX job configuration with SQL expression support

    Args:
        job_config: Job configuration dictionary
        logger: Optional logger

    Returns:
        Tuple[bool, str]: (is_valid, summary)
    """
    validator = create_extended_gdx_job_validator(logger=logger, mode="sql_enhanced")
    return validator.validate_job_configuration(job_config)


# Additional convenience functions for backward compatibility
def validate_job_config(job_config: Dict[str, Any], logger=None) -> ValidationResult:
    """
    Convenience function for validating job configuration (returns ValidationResult)

    Args:
        job_config: Job configuration dictionary
        logger: Optional logger (GDX framework, standard logging, etc.)

    Returns:
        ValidationResult: Complete validation results
    """
    validator = ComprehensiveYamlValidator(logger)
    return validator.validate_comprehensive(job_config)


def validate_mapping_config(mapping_config: Dict[str, Any], logger=None) -> ValidationResult:
    """
    Convenience function for validating mapping configuration (returns ValidationResult)

    Args:
        mapping_config: Single mapping configuration
        logger: Optional logger (GDX framework, standard logging, etc.)

    Returns:
        ValidationResult: Validation results for the mapping
    """
    validator = ComprehensiveYamlValidator(logger)
    wrapped_config = {"mappings": [mapping_config]}
    return validator.validate_comprehensive(wrapped_config)
