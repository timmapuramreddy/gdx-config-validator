"""
GDX Config Validator Library

A comprehensive library for validating GDX (Glue DataXpress) configuration files.
Provides robust validation for YAML configurations with detailed error reporting,
SQL expression support, and flexible parameter validation.
"""

# Version management with fallback
try:
    from importlib.metadata import version, PackageNotFoundError

    try:
        __version__ = version("gdx-config-validator")
    except PackageNotFoundError:
        __version__ = "1.0.0"  # Fallback version
except ImportError:
    # Python < 3.8 fallback
    __version__ = "1.0.0"

__author__ = "Mohan Reddy"
__description__ = "A comprehensive library for validating GDX configuration files"
__email__ = "mohan.reddy@company.com"  # Update with actual email
__license__ = "Proprietary"  # Update as needed
__url__ = "https://github.com/your-org/gdx-config-validator"  # Update as needed

# Core validation results and utilities
from .results import (
    ValidationResult,
    ValidationResultBuilder,
    ValidationSeverity,
    create_success_result,
    create_error_result,
    create_exception_result,
)

# Core validation classes and utilities
from .core import (
    BaseValidator,
    ValidationContext,
    ValidationMetrics,
    ValidationRuleEngine,
    ValidationSummaryGenerator,
    ValidationLogger,
    ValidationErrorHandler,
    validate_with_metrics,
    log_validation_start_end,
)

# Operation specifications and registry
from .schemas.operations import (
    ParameterType,
    ParameterSpec,
    OperationSpec,
    OperationRegistry,
    OPERATION_REGISTRY,
)

# Main validator classes
from .validators import (
    GDXYamlParser,
    ComprehensiveYamlValidator,
    SQLExpressionColumnValidator,
    GDXJobValidator,
    ExtendedGDXJobValidator,
    # Convenience functions
    validate_job_config,
    validate_mapping_config,
    create_job_validator,
    validate_gdx_job_config,
    validate_gdx_mapping_config,
    create_extended_gdx_job_validator,
    validate_gdx_job_config_with_sql,
)

# Configuration and logging
from .config import (
    configure_logging,
    get_library_logger,
    reset_logging_config,
    get_logging_config,
    configure_for_production,
    configure_for_development,
    configure_for_testing,
    configure_for_standalone,
    LoggingContext,
)

# Factory functions and high-level API
from .factory import (
    ValidatorType,
    create_validator,
    validate_file,
    validate_string,
    validate_job_config,
    validate_mapping_config,
    quick_validate,
    get_validator_info,
    setup_logging_for_standalone,
    validate_directory,
    get_validation_summary,
)

# Public API exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    # Core validation results
    "ValidationResult",
    "ValidationResultBuilder",
    "ValidationSeverity",
    "create_success_result",
    "create_error_result",
    "create_exception_result",
    # Core validation classes
    "BaseValidator",
    "ValidationContext",
    "ValidationMetrics",
    "ValidationRuleEngine",
    "ValidationSummaryGenerator",
    "ValidationLogger",
    "ValidationErrorHandler",
    # Decorators
    "validate_with_metrics",
    "log_validation_start_end",
    # Operation registry
    "ParameterType",
    "ParameterSpec",
    "OperationSpec",
    "OperationRegistry",
    "OPERATION_REGISTRY",
    # Main validator classes
    "GDXYamlParser",
    "ComprehensiveYamlValidator",
    "SQLExpressionColumnValidator",
    "GDXJobValidator",
    "ExtendedGDXJobValidator",
    # Convenience functions
    "validate_job_config",
    "validate_mapping_config",
    "create_job_validator",
    "validate_gdx_job_config",
    "validate_gdx_mapping_config",
    "create_extended_gdx_job_validator",
    "validate_gdx_job_config_with_sql",
    # Configuration and logging
    "configure_logging",
    "get_library_logger",
    "reset_logging_config",
    "get_logging_config",
    "configure_for_production",
    "configure_for_development",
    "configure_for_testing",
    "configure_for_standalone",
    "LoggingContext",
    # Factory functions and high-level API
    "ValidatorType",
    "create_validator",
    "validate_file",
    "validate_string",
    "validate_job_config",
    "validate_mapping_config",
    "quick_validate",
    "get_validator_info",
    "setup_logging_for_standalone",
    "validate_directory",
    "get_validation_summary",
]


# Package metadata and version management
def get_version():
    """Get the current version of the library"""
    return __version__


def check_version_compatibility(required_version: str) -> bool:
    """Check if current version meets requirements"""
    try:
        from packaging import version as pkg_version

        return pkg_version.parse(__version__) >= pkg_version.parse(required_version)
    except ImportError:
        # Fallback to simple string comparison
        return __version__ >= required_version


def get_info():
    """Get comprehensive library information"""
    import sys
    import platform

    info = {
        "name": "gdx-config-validator",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "modules": {
            "results": "Validation result classes and utilities",
            "core": "Base validation classes and common utilities",
            "schemas": "Operation specifications and parameter validation",
            "validators": "Main validator implementations",
            "factory": "Factory pattern for validator creation",
            "logging_adapter": "Enhanced logging system",
            "config": "Configuration management",
            "parsers": "YAML parsing utilities",
            "utils": "Helper functions and utilities",
        },
        "features": {
            "validator_types": 6,
            "operation_count": "20+",
            "operation_categories": 6,
            "logging_adapters": 5,
            "documentation_pages": 5,
        },
    }

    # Add dependency information if available
    try:
        import yaml

        info["dependencies"] = {"pyyaml": getattr(yaml, "__version__", "unknown")}
    except ImportError:
        info["dependencies"] = {"pyyaml": "not_installed"}

    return info
