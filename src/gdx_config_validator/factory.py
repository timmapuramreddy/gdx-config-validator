"""
Factory Module for GDX Config Validator Library

Serves as the primary entry point and convenience layer for users.
Implements the Factory Design Pattern to provide simple, intuitive ways
to create validators and perform validation tasks.

This module provides:
- Simple factory functions for creating validators
- High-level convenience functions for common validation tasks
- Unified interface that abstracts away implementation details
- Easy-to-use API for both standalone and framework integration
"""

import os
from typing import Dict, Any, Optional, Union, List, Tuple
from pathlib import Path

from .validators import (
    GDXYamlParser,
    ComprehensiveYamlValidator,
    SQLExpressionColumnValidator,
    GDXJobValidator,
    ExtendedGDXJobValidator,
)
from .parsers import YamlParser, parse_yaml_file, parse_yaml_string
from .results import ValidationResult
from .config import configure_logging
from .utils import validate_operation_type, get_supported_operations


# Validator type constants
class ValidatorType:
    """Constants for validator types"""

    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    JOB = "job"
    EXTENDED_JOB = "extended_job"
    SQL_ENHANCED = "sql_enhanced"
    PARSER_ONLY = "parser_only"


def create_validator(
    validator_type: str = ValidatorType.COMPREHENSIVE, logger=None, silent: bool = False, **kwargs
) -> Any:
    """
    Factory function to create validators based on type

    Args:
        validator_type: Type of validator to create (use ValidatorType constants)
        logger: External logger instance (GDX framework, standard logging, etc.)
        silent: Force silent logging
        **kwargs: Additional arguments passed to validator constructor

    Returns:
        Configured validator instance

    Raises:
        ValueError: If validator_type is not supported

    Examples:
        # Basic YAML parser
        parser = create_validator(ValidatorType.BASIC, logger=my_logger)

        # Comprehensive validator
        validator = create_validator(ValidatorType.COMPREHENSIVE)

        # Job validator with SQL support
        job_validator = create_validator(ValidatorType.SQL_ENHANCED, silent=True)
    """

    if validator_type == ValidatorType.BASIC:
        return GDXYamlParser(logger=logger, **kwargs)

    elif validator_type == ValidatorType.COMPREHENSIVE:
        return ComprehensiveYamlValidator(logger=logger, **kwargs)

    elif validator_type == ValidatorType.JOB:
        validation_mode = kwargs.get("validation_mode", "comprehensive")
        return GDXJobValidator(
            logger=logger,
            validation_mode=validation_mode,
            silent=silent,
            **{k: v for k, v in kwargs.items() if k != "validation_mode"},
        )

    elif validator_type == ValidatorType.EXTENDED_JOB:
        validation_mode = kwargs.get("validation_mode", "comprehensive")
        return ExtendedGDXJobValidator(
            logger=logger,
            validation_mode=validation_mode,
            **{k: v for k, v in kwargs.items() if k != "validation_mode"},
        )

    elif validator_type == ValidatorType.SQL_ENHANCED:
        validation_mode = kwargs.get("validation_mode", "sql_enhanced")
        return ExtendedGDXJobValidator(
            logger=logger,
            validation_mode=validation_mode,
            **{k: v for k, v in kwargs.items() if k != "validation_mode"},
        )

    elif validator_type == ValidatorType.PARSER_ONLY:
        return YamlParser(logger=logger, silent=silent)

    else:
        raise ValueError(
            f"Unknown validator type: {validator_type}. "
            f"Supported types: {list(vars(ValidatorType).values())}"
        )


def validate_file(
    file_path: Union[str, Path],
    validator_type: str = ValidatorType.COMPREHENSIVE,
    logger=None,
    silent: bool = False,
) -> ValidationResult:
    """
    High-level function to validate a YAML file

    Args:
        file_path: Path to YAML file to validate
        validator_type: Type of validator to use
        logger: External logger instance
        silent: Force silent logging

    Returns:
        ValidationResult: Complete validation results

    Examples:
        # Basic file validation
        result = validate_file("config.yaml")

        # Comprehensive validation with custom logger
        result = validate_file("job.yaml", ValidatorType.COMPREHENSIVE, my_logger)

        # SQL-enhanced validation
        result = validate_file("complex.yaml", ValidatorType.SQL_ENHANCED)
    """
    try:
        # Parse the file first
        parser = YamlParser(logger=logger, silent=silent)
        config_data = parser.parse_yaml_file(file_path)

        # Create appropriate validator and validate
        validator = create_validator(validator_type, logger=logger, silent=silent)

        if hasattr(validator, "validate_comprehensive"):
            return validator.validate_comprehensive(config_data)
        elif hasattr(validator, "validate"):
            return validator.validate(config_data)
        else:
            # Fallback for basic parsers
            return parser.validate_yaml_structure(config_data)

    except Exception as e:
        from .results import create_exception_result

        return create_exception_result(e, context=f"validate_file({file_path})")


def validate_string(
    yaml_string: str,
    validator_type: str = ValidatorType.COMPREHENSIVE,
    logger=None,
    silent: bool = False,
) -> ValidationResult:
    """
    High-level function to validate a YAML string

    Args:
        yaml_string: YAML content as string
        validator_type: Type of validator to use
        logger: External logger instance
        silent: Force silent logging

    Returns:
        ValidationResult: Complete validation results

    Examples:
        # Validate YAML string
        yaml_content = '''
        mappings:
          - mapping_name: test
            source_table: src
        '''
        result = validate_string(yaml_content)
    """
    try:
        # Parse the string first
        parser = YamlParser(logger=logger, silent=silent)
        config_data = parser.parse_yaml_string(yaml_string)

        # Create appropriate validator and validate
        validator = create_validator(validator_type, logger=logger, silent=silent)

        if hasattr(validator, "validate_comprehensive"):
            return validator.validate_comprehensive(config_data)
        elif hasattr(validator, "validate"):
            return validator.validate(config_data)
        else:
            # Fallback for basic parsers
            return parser.validate_yaml_structure(config_data)

    except Exception as e:
        from .results import create_exception_result

        return create_exception_result(e, context="validate_string")


def validate_job_config(
    job_config: Dict[str, Any],
    include_sql_validation: bool = False,
    logger=None,
    silent: bool = False,
) -> Tuple[bool, str]:
    """
    High-level function to validate a job configuration

    Args:
        job_config: Job configuration dictionary
        include_sql_validation: Whether to include SQL expression validation
        logger: External logger instance
        silent: Force silent logging

    Returns:
        Tuple[bool, str]: (is_valid, summary_message)

    Examples:
        # Standard job validation
        is_valid, summary = validate_job_config(config)

        # With SQL validation
        is_valid, summary = validate_job_config(config, include_sql_validation=True)
    """
    if include_sql_validation:
        validator = create_validator(ValidatorType.SQL_ENHANCED, logger=logger, silent=silent)
    else:
        validator = create_validator(ValidatorType.JOB, logger=logger, silent=silent)

    return validator.validate_job_configuration(job_config)


def validate_mapping_config(
    mapping_config: Dict[str, Any],
    include_sql_validation: bool = False,
    logger=None,
    silent: bool = False,
) -> Tuple[bool, str]:
    """
    High-level function to validate a mapping configuration

    Args:
        mapping_config: Single mapping configuration dictionary
        include_sql_validation: Whether to include SQL expression validation
        logger: External logger instance
        silent: Force silent logging

    Returns:
        Tuple[bool, str]: (is_valid, summary_message)

    Examples:
        # Standard mapping validation
        is_valid, summary = validate_mapping_config(mapping)

        # With SQL validation
        is_valid, summary = validate_mapping_config(mapping, include_sql_validation=True)
    """
    if include_sql_validation:
        validator = create_validator(ValidatorType.SQL_ENHANCED, logger=logger, silent=silent)
    else:
        validator = create_validator(ValidatorType.JOB, logger=logger, silent=silent)

    return validator.validate_mapping_configuration(mapping_config)


def quick_validate(
    data: Union[str, Path, Dict[str, Any]], logger=None, silent: bool = True
) -> bool:
    """
    Quick validation function that returns just a boolean result

    Args:
        data: File path, YAML string, or config dictionary to validate
        logger: External logger instance
        silent: Use silent logging (default True for quick validation)

    Returns:
        bool: True if valid, False otherwise

    Examples:
        # Quick file check
        if quick_validate("config.yaml"):
            print("Config is valid!")

        # Quick string check
        is_valid = quick_validate("mappings: []")

        # Quick dict check
        is_valid = quick_validate({"mappings": []})
    """
    try:
        if isinstance(data, (str, Path)):
            if isinstance(data, str) and not Path(data).exists():
                # Assume it's a YAML string if file doesn't exist
                result = validate_string(data, ValidatorType.COMPREHENSIVE, logger, silent)
            else:
                # It's a file path
                result = validate_file(data, ValidatorType.COMPREHENSIVE, logger, silent)
        elif isinstance(data, dict):
            # It's already a parsed config
            validator = create_validator(ValidatorType.COMPREHENSIVE, logger=logger, silent=silent)
            result = validator.validate_comprehensive(data)
        else:
            return False

        return result.is_valid

    except Exception:
        return False


def get_validator_info(validator_type: str = None) -> Dict[str, Any]:
    """
    Get information about available validators

    Args:
        validator_type: Specific validator type to get info for (optional)

    Returns:
        Dict containing validator information

    Examples:
        # Get all validator info
        info = get_validator_info()

        # Get specific validator info
        info = get_validator_info(ValidatorType.SQL_ENHANCED)
    """
    all_validators = {
        ValidatorType.BASIC: {
            "class": "GDXYamlParser",
            "description": "Basic YAML parsing and validation",
            "features": ["yaml_parsing", "basic_validation", "transformation_validation"],
        },
        ValidatorType.COMPREHENSIVE: {
            "class": "ComprehensiveYamlValidator",
            "description": "Comprehensive YAML validation with advanced features",
            "features": [
                "yaml_parsing",
                "comprehensive_validation",
                "cross_section_validation",
                "sql_expressions",
            ],
        },
        ValidatorType.JOB: {
            "class": "GDXJobValidator",
            "description": "Enterprise job validation with history tracking",
            "features": [
                "job_validation",
                "validation_history",
                "performance_metrics",
                "enhanced_reporting",
            ],
        },
        ValidatorType.EXTENDED_JOB: {
            "class": "ExtendedGDXJobValidator",
            "description": "Extended job validator with SQL expression support",
            "features": [
                "job_validation",
                "sql_expressions",
                "enhanced_validation",
                "error_deduplication",
            ],
        },
        ValidatorType.SQL_ENHANCED: {
            "class": "ExtendedGDXJobValidator",
            "description": "SQL-enhanced validation with comprehensive features",
            "features": [
                "sql_expressions",
                "comprehensive_validation",
                "advanced_sql_analysis",
                "enterprise_features",
            ],
        },
        ValidatorType.PARSER_ONLY: {
            "class": "YamlParser",
            "description": "Pure YAML parsing without validation",
            "features": ["yaml_parsing", "structure_validation", "error_handling"],
        },
    }

    if validator_type:
        return all_validators.get(validator_type, {})

    return all_validators


def setup_logging_for_standalone(level: str = "WARNING", debug: bool = False):
    """
    Configure logging for standalone usage

    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
        debug: Enable debug mode (overrides level)

    Examples:
        # Quiet standalone usage
        setup_logging_for_standalone("ERROR")

        # Verbose standalone usage
        setup_logging_for_standalone("INFO")

        # Debug mode
        setup_logging_for_standalone(debug=True)
    """
    if debug:
        configure_logging(debug=True, force_console=True)
    else:
        configure_logging(level=level)


def validate_directory(
    directory_path: Union[str, Path],
    pattern: str = "*.yaml",
    validator_type: str = ValidatorType.COMPREHENSIVE,
    logger=None,
    silent: bool = False,
) -> Dict[str, ValidationResult]:
    """
    Validate all YAML files in a directory

    Args:
        directory_path: Path to directory containing YAML files
        pattern: File pattern to match (default: "*.yaml")
        validator_type: Type of validator to use
        logger: External logger instance
        silent: Force silent logging

    Returns:
        Dict mapping file paths to validation results

    Examples:
        # Validate all YAML files in a directory
        results = validate_directory("configs/")

        # Validate specific pattern
        results = validate_directory("jobs/", "job_*.yml")
    """
    directory_path = Path(directory_path)
    results = {}

    if not directory_path.exists() or not directory_path.is_dir():
        return results

    # Find matching files
    for file_path in directory_path.glob(pattern):
        if file_path.is_file():
            try:
                result = validate_file(file_path, validator_type, logger, silent)
                results[str(file_path)] = result
            except Exception as e:
                from .results import create_exception_result

                results[str(file_path)] = create_exception_result(e, context=str(file_path))

    return results


def get_validation_summary(results: Dict[str, ValidationResult]) -> Dict[str, Any]:
    """
    Generate summary statistics from multiple validation results

    Args:
        results: Dictionary of validation results from validate_directory

    Returns:
        Dict containing summary statistics

    Examples:
        results = validate_directory("configs/")
        summary = get_validation_summary(results)
        print(f"Valid files: {summary['valid_count']}/{summary['total_count']}")
    """
    total_count = len(results)
    valid_count = sum(1 for result in results.values() if result.is_valid)

    total_errors = sum(len(result.errors) for result in results.values())
    total_warnings = sum(len(result.warnings) for result in results.values())

    # Find files with issues
    invalid_files = [path for path, result in results.items() if not result.is_valid]
    files_with_warnings = [path for path, result in results.items() if result.warnings]

    return {
        "total_count": total_count,
        "valid_count": valid_count,
        "invalid_count": total_count - valid_count,
        "success_rate": valid_count / total_count if total_count > 0 else 0,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "invalid_files": invalid_files,
        "files_with_warnings": files_with_warnings,
        "avg_errors_per_file": total_errors / total_count if total_count > 0 else 0,
        "avg_warnings_per_file": total_warnings / total_count if total_count > 0 else 0,
    }


# Convenience aliases for backward compatibility
create_job_validator = lambda logger=None, mode="comprehensive", silent=False: create_validator(
    ValidatorType.JOB, logger=logger, validation_mode=mode, silent=silent
)
create_comprehensive_validator = lambda logger=None, silent=False: create_validator(
    ValidatorType.COMPREHENSIVE, logger=logger, silent=silent
)
create_sql_validator = lambda logger=None, silent=False: create_validator(
    ValidatorType.SQL_ENHANCED, logger=logger, silent=silent
)
