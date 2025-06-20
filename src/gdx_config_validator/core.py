"""
Base classes and common utilities for validation
Enhanced with flexible logging system for library and framework integration
"""

import functools
import traceback
from typing import Dict, List, Any, Optional, Callable, Union
from abc import ABC, abstractmethod

from .results import (
    ValidationResult,
    ValidationResultBuilder,
    ValidationSeverity,
    create_exception_result,
)
from .logging_adapter import LoggerFactory, LoggerAdapter, get_logger


class ValidationLogger:
    """Enhanced logging interface using the logging adapter system"""

    def __init__(self, logger=None, prefix: str = "", silent: bool = False):
        self.prefix = prefix
        self.logger_adapter = get_logger(logger, prefix, silent)
        self._original_logger = logger  # Keep reference for introspection

    def log_info(self, message: str):
        """Log information message"""
        formatted_message = f"[{self.prefix}] {message}" if self.prefix else message
        self.logger_adapter.info(formatted_message)

    def log_warning(self, message: str):
        """Log warning message"""
        formatted_message = f"[{self.prefix}] {message}" if self.prefix else message
        self.logger_adapter.warning(formatted_message)

    def log_error(self, message: str):
        """Log error message"""
        formatted_message = f"[{self.prefix}] {message}" if self.prefix else message
        self.logger_adapter.error(formatted_message)

    def log_debug(self, message: str):
        """Log debug message"""
        formatted_message = f"[{self.prefix}] {message}" if self.prefix else message
        self.logger_adapter.debug(formatted_message)

    def is_logging_enabled(self) -> bool:
        """Check if logging is enabled (not silent)"""
        from .logging_adapter import SilentLoggerAdapter

        return not isinstance(self.logger_adapter, SilentLoggerAdapter)

    def has_external_logger(self) -> bool:
        """Check if using external logger (GDX framework integration)"""
        return self._original_logger is not None


class ValidationErrorHandler:
    """Common error handling utilities"""

    @staticmethod
    def handle_validation_exception(func: Callable) -> Callable:
        """Decorator for handling validation exceptions consistently"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> ValidationResult:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Extract context from function and arguments
                context = f"{func.__name__}"
                if args and hasattr(args[0], "__class__"):
                    context = f"{args[0].__class__.__name__}.{func.__name__}"

                return create_exception_result(e, context=context)

        return wrapper

    @staticmethod
    def safe_validation_call(
        func: Callable, error_context: str, default_result: ValidationResult = None
    ) -> ValidationResult:
        """Safely call a validation function with error handling"""
        try:
            return func()
        except Exception as e:
            if default_result:
                return default_result
            return create_exception_result(e, context=error_context)


class BaseValidator(ABC):
    """Enhanced abstract base class for all validators with smart logging"""

    def __init__(self, logger=None, prefix: str = "", silent: bool = False):
        self.validation_logger = ValidationLogger(logger, prefix, silent)
        self.error_handler = ValidationErrorHandler()
        self.component = prefix
        self._original_logger = logger  # Keep reference for framework integration

    # Delegate logging methods
    def log_info(self, message: str):
        self.validation_logger.log_info(message)

    def log_warning(self, message: str):
        self.validation_logger.log_warning(message)

    def log_error(self, message: str):
        self.validation_logger.log_error(message)

    def log_debug(self, message: str):
        self.validation_logger.log_debug(message)

    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Main validation method - must be implemented by subclasses"""
        pass

    def create_result_builder(self) -> ValidationResultBuilder:
        """Create a new result builder"""
        return ValidationResultBuilder()

    def validate_with_error_handling(
        self, validation_func: Callable, error_context: str
    ) -> ValidationResult:
        """Execute validation function with standardized error handling"""
        return self.error_handler.safe_validation_call(validation_func, error_context)

    # Enhanced utility methods
    def is_logging_enabled(self) -> bool:
        """Check if logging is enabled (useful for performance optimizations)"""
        return self.validation_logger.is_logging_enabled()

    def has_external_logger(self) -> bool:
        """Check if using external logger (GDX framework integration)"""
        return self.validation_logger.has_external_logger()

    def get_logger_info(self) -> dict:
        """Get information about the current logger setup"""
        return {
            "has_external_logger": self.has_external_logger(),
            "logging_enabled": self.is_logging_enabled(),
            "component": self.component,
            "logger_type": type(self.validation_logger.logger_adapter).__name__,
        }


class ValidationContext:
    """Context information for validation operations"""

    def __init__(
        self,
        base_path: str = "",
        mapping_name: str = "",
        transformation_index: int = -1,
        operation_index: int = -1,
    ):
        self.base_path = base_path
        self.mapping_name = mapping_name
        self.transformation_index = transformation_index
        self.operation_index = operation_index

    def get_path(self, additional_path: str = "") -> str:
        """Get the full path for error reporting"""
        path_parts = []

        if self.base_path:
            path_parts.append(self.base_path)

        if self.transformation_index >= 0:
            path_parts.append(f"column_transformations[{self.transformation_index}]")

        if self.operation_index >= 0:
            path_parts.append(f"transformations[{self.operation_index}]")

        if additional_path:
            path_parts.append(additional_path)

        return ".".join(path_parts)

    def create_child_context(self, **kwargs) -> "ValidationContext":
        """Create a child context with updated values"""
        return ValidationContext(
            base_path=kwargs.get("base_path", self.base_path),
            mapping_name=kwargs.get("mapping_name", self.mapping_name),
            transformation_index=kwargs.get("transformation_index", self.transformation_index),
            operation_index=kwargs.get("operation_index", self.operation_index),
        )


class ValidationMetrics:
    """Track validation performance and statistics"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.operations_validated = 0
        self.transformations_validated = 0
        self.mappings_validated = 0
        self.errors_found = 0
        self.warnings_found = 0
        self.performance_data = {}

    def start_validation(self):
        """Mark start of validation"""
        import time

        self.start_time = time.time()

    def end_validation(self):
        """Mark end of validation"""
        import time

        self.end_time = time.time()

    def get_duration(self) -> float:
        """Get validation duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def increment_operations(self):
        """Increment operation count"""
        self.operations_validated += 1

    def increment_transformations(self):
        """Increment transformation count"""
        self.transformations_validated += 1

    def increment_mappings(self):
        """Increment mapping count"""
        self.mappings_validated += 1

    def add_errors(self, count: int):
        """Add to error count"""
        self.errors_found += count

    def add_warnings(self, count: int):
        """Add to warning count"""
        self.warnings_found += count

    def set_performance_data(self, key: str, value: Any):
        """Set performance metric"""
        self.performance_data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "duration_seconds": self.get_duration(),
            "operations_validated": self.operations_validated,
            "transformations_validated": self.transformations_validated,
            "mappings_validated": self.mappings_validated,
            "errors_found": self.errors_found,
            "warnings_found": self.warnings_found,
            "performance_data": self.performance_data,
        }


class ValidationRuleEngine:
    """Engine for applying validation rules consistently"""

    def __init__(self):
        self.rules: Dict[str, Callable] = {}
        self.rule_metadata: Dict[str, Dict[str, Any]] = {}

    def register_rule(
        self,
        name: str,
        rule_func: Callable,
        description: str = "",
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        categories: List[str] = None,
    ):
        """Register a validation rule"""
        self.rules[name] = rule_func
        self.rule_metadata[name] = {
            "description": description,
            "severity": severity,
            "categories": categories or [],
            "function": rule_func.__name__,
        }

    def apply_rules(
        self, data: Any, context: ValidationContext, rule_categories: List[str] = None
    ) -> ValidationResult:
        """Apply validation rules to data"""
        builder = ValidationResultBuilder()

        for rule_name, rule_func in self.rules.items():
            metadata = self.rule_metadata[rule_name]

            # Filter by categories if specified
            if rule_categories:
                rule_cats = metadata.get("categories", [])
                if not any(cat in rule_cats for cat in rule_categories):
                    continue

            try:
                # Apply the rule
                rule_result = rule_func(data, context)

                if isinstance(rule_result, ValidationResult):
                    # Merge results
                    builder.errors.extend(rule_result.errors)
                    builder.warnings.extend(rule_result.warnings)
                    builder.info.extend(rule_result.info)
                elif isinstance(rule_result, list):
                    # List of error/warning dictionaries
                    for item in rule_result:
                        severity = item.get("severity", metadata["severity"].value)
                        if severity == ValidationSeverity.ERROR.value:
                            builder.errors.append(item)
                        elif severity == ValidationSeverity.WARNING.value:
                            builder.warnings.append(item)
                        else:
                            builder.info.append(item)
                elif isinstance(rule_result, dict):
                    # Single error/warning dictionary
                    severity = rule_result.get("severity", metadata["severity"].value)
                    if severity == ValidationSeverity.ERROR.value:
                        builder.errors.append(rule_result)
                    elif severity == ValidationSeverity.WARNING.value:
                        builder.warnings.append(rule_result)
                    else:
                        builder.info.append(rule_result)

            except Exception as e:
                # Rule execution failed
                builder.add_error(
                    "rule_execution_error",
                    f'Validation rule "{rule_name}" failed: {str(e)}',
                    path=context.get_path(),
                    mapping=context.mapping_name,
                    rule=rule_name,
                    exception=str(e),
                )

        return builder.build()

    def get_available_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available rules"""
        return self.rule_metadata.copy()

    def get_rules_by_category(self, category: str) -> List[str]:
        """Get rule names by category"""
        return [
            rule_name
            for rule_name, metadata in self.rule_metadata.items()
            if category in metadata.get("categories", [])
        ]


class ValidationSummaryGenerator:
    """Generate human-readable validation summaries"""

    @staticmethod
    def generate_detailed_summary(
        result: ValidationResult, include_suggestions: bool = True
    ) -> str:
        """Generate a detailed validation summary"""
        lines = []
        lines.append("=" * 70)
        lines.append("VALIDATION SUMMARY")
        lines.append("=" * 70)

        # Overall status
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        lines.append(f"Status: {status}")
        lines.append("")

        # Counts
        lines.append(f"Errors: {len(result.errors)}")
        lines.append(f"Warnings: {len(result.warnings)}")
        lines.append(f"Info: {len(result.info)}")
        lines.append("")

        # Error summary by type
        if result.errors:
            error_summary = result.get_error_summary()
            lines.append("ERROR BREAKDOWN:")
            for error_type, count in error_summary.items():
                lines.append(f"  - {error_type}: {count}")
            lines.append("")

        # Affected mappings
        affected_mappings = result.get_affected_mappings()
        if affected_mappings:
            lines.append(f"AFFECTED MAPPINGS ({len(affected_mappings)}):")
            for mapping in affected_mappings:
                mapping_errors = len(result.get_messages_by_mapping(mapping))
                lines.append(f"  - {mapping}: {mapping_errors} issues")
            lines.append("")

        # Detailed errors
        if result.errors:
            lines.append("DETAILED ERRORS:")
            for i, error in enumerate(result.errors[:10], 1):  # Limit to first 10
                path = error.get("path", "unknown")
                message = error.get("message", "Unknown error")
                lines.append(f"  {i}. [{path}] {message}")

            if len(result.errors) > 10:
                lines.append(f"  ... and {len(result.errors) - 10} more errors")
            lines.append("")

        # Suggestions
        if include_suggestions:
            suggestions = result.get_suggestions()
            if suggestions:
                lines.append("SUGGESTIONS:")
                for suggestion in suggestions[:5]:  # Limit to first 5
                    lines.append(f"  💡 {suggestion}")
                if len(suggestions) > 5:
                    lines.append(f"  ... and {len(suggestions) - 5} more suggestions")
                lines.append("")

        # Performance metrics
        if result.performance_metrics:
            lines.append("PERFORMANCE METRICS:")
            for key, value in result.performance_metrics.items():
                lines.append(f"  - {key}: {value}")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    @staticmethod
    def generate_compact_summary(result: ValidationResult) -> str:
        """Generate a compact one-line summary"""
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        counts = f"({len(result.errors)} errors, {len(result.warnings)} warnings)"
        affected = (
            f"{len(result.get_affected_mappings())} mappings affected"
            if result.get_affected_mappings()
            else ""
        )

        parts = [status, counts]
        if affected:
            parts.append(affected)

        return " ".join(parts)

    @staticmethod
    def generate_json_summary(result: ValidationResult) -> Dict[str, Any]:
        """Generate a JSON-serializable summary"""
        return {
            "status": "valid" if result.is_valid else "invalid",
            "summary": {
                "error_count": len(result.errors),
                "warning_count": len(result.warnings),
                "info_count": len(result.info),
                "affected_mappings": list(result.get_affected_mappings()),
            },
            "error_breakdown": result.get_error_summary(),
            "warning_breakdown": result.get_warning_summary(),
            "suggestions": result.get_suggestions(),
            "performance": result.performance_metrics,
        }


# Common validation decorators
def validate_with_metrics(func: Callable) -> Callable:
    """Decorator to add performance metrics to validation functions"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> ValidationResult:
        metrics = ValidationMetrics()
        metrics.start_validation()

        try:
            result = func(*args, **kwargs)

            # Add metrics to result
            metrics.end_validation()
            metrics.add_errors(len(result.errors))
            metrics.add_warnings(len(result.warnings))

            if not result.performance_metrics:
                result.performance_metrics = {}
            result.performance_metrics.update(metrics.to_dict())

            return result

        except Exception as e:
            metrics.end_validation()
            return create_exception_result(e, context=func.__name__)

    return wrapper


def log_validation_start_end(func: Callable) -> Callable:
    """Decorator to log validation start and end"""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> ValidationResult:
        if hasattr(self, "log_info"):
            self.log_info(f"Starting {func.__name__}")

        try:
            result = func(self, *args, **kwargs)

            if hasattr(self, "log_info"):
                status = "completed successfully" if result.is_valid else "completed with errors"
                self.log_info(f"{func.__name__} {status}")

            return result

        except Exception as e:
            if hasattr(self, "log_error"):
                self.log_error(f"{func.__name__} failed: {str(e)}")
            raise

    return wrapper
