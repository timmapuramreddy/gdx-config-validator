"""
Enhanced ValidationResult with utility methods and better error handling
"""

import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation messages"""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Enhanced result of a validation operation with utility methods"""

    is_valid: bool
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    info: List[Dict[str, Any]] = field(default_factory=list)

    # Optional enhancement fields
    performance_metrics: Optional[Dict[str, Any]] = None
    validation_metadata: Optional[Dict[str, Any]] = None

    def has_errors(self) -> bool:
        """Check if validation has any errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if validation has any warnings"""
        return len(self.warnings) > 0

    def has_info(self) -> bool:
        """Check if validation has any info messages"""
        return len(self.info) > 0

    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Get all validation messages combined"""
        return self.errors + self.warnings + self.info

    def get_errors_by_type(self, error_type: str) -> List[Dict[str, Any]]:
        """Get errors of a specific type"""
        return [e for e in self.errors if e.get("type") == error_type]

    def get_warnings_by_type(self, warning_type: str) -> List[Dict[str, Any]]:
        """Get warnings of a specific type"""
        return [w for w in self.warnings if w.get("type") == warning_type]

    def get_critical_errors(self) -> List[Dict[str, Any]]:
        """Get only critical severity errors"""
        return [e for e in self.errors if e.get("severity") == ValidationSeverity.CRITICAL.value]

    def get_messages_by_severity(self, severity: ValidationSeverity) -> List[Dict[str, Any]]:
        """Get all messages of a specific severity"""
        severity_value = severity.value
        return [msg for msg in self.get_all_messages() if msg.get("severity") == severity_value]

    def get_messages_by_path(self, path_prefix: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific path or path prefix"""
        return [
            msg for msg in self.get_all_messages() if msg.get("path", "").startswith(path_prefix)
        ]

    def get_messages_by_mapping(self, mapping_name: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific mapping"""
        return [msg for msg in self.get_all_messages() if msg.get("mapping") == mapping_name]

    def has_operation_errors(self) -> bool:
        """Check if there are any operation-related errors"""
        return any("operation" in e.get("type", "") for e in self.errors)

    def has_parameter_errors(self) -> bool:
        """Check if there are any parameter-related errors"""
        return any("parameter" in e.get("type", "") for e in self.errors)

    def get_suggestions(self) -> List[str]:
        """Get all suggestions from errors and warnings"""
        suggestions = []
        for msg in self.get_all_messages():
            if "suggestion" in msg and msg["suggestion"]:
                suggestions.append(msg["suggestion"])
        return suggestions

    def get_error_types(self) -> Set[str]:
        """Get unique error types"""
        return {e.get("type", "unknown") for e in self.errors}

    def get_warning_types(self) -> Set[str]:
        """Get unique warning types"""
        return {w.get("type", "unknown") for w in self.warnings}

    def get_affected_mappings(self) -> Set[str]:
        """Get names of all mappings that have issues"""
        mappings = set()
        for msg in self.get_all_messages():
            if "mapping" in msg and msg["mapping"]:
                mappings.add(msg["mapping"])
        return mappings

    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of error counts by type"""
        summary = {}
        for error in self.errors:
            error_type = error.get("type", "unknown")
            summary[error_type] = summary.get(error_type, 0) + 1
        return summary

    def get_warning_summary(self) -> Dict[str, int]:
        """Get summary of warning counts by type"""
        summary = {}
        for warning in self.warnings:
            warning_type = warning.get("type", "unknown")
            summary[warning_type] = summary.get(warning_type, 0) + 1
        return summary

    def filter_by_severity(self, min_severity: ValidationSeverity) -> "ValidationResult":
        """Create a new ValidationResult with only messages above minimum severity"""
        severity_order = {
            ValidationSeverity.INFO: 0,
            ValidationSeverity.WARNING: 1,
            ValidationSeverity.ERROR: 2,
            ValidationSeverity.CRITICAL: 3,
        }

        min_level = severity_order[min_severity]

        filtered_errors = []
        filtered_warnings = []
        filtered_info = []

        for msg in self.get_all_messages():
            msg_severity = ValidationSeverity(msg.get("severity", "info"))
            if severity_order[msg_severity] >= min_level:
                if msg_severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                    filtered_errors.append(msg)
                elif msg_severity == ValidationSeverity.WARNING:
                    filtered_warnings.append(msg)
                else:
                    filtered_info.append(msg)

        return ValidationResult(
            is_valid=len(filtered_errors) == 0,
            errors=filtered_errors,
            warnings=filtered_warnings,
            info=filtered_info,
            performance_metrics=self.performance_metrics,
            validation_metadata=self.validation_metadata,
        )

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge with another ValidationResult"""
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            info=self.info + other.info,
            performance_metrics=self.performance_metrics or other.performance_metrics,
            validation_metadata=self.validation_metadata or other.validation_metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "info_count": len(self.info),
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "suggestions": self.get_suggestions(),
            "error_summary": self.get_error_summary(),
            "warning_summary": self.get_warning_summary(),
            "affected_mappings": list(self.get_affected_mappings()),
            "performance_metrics": self.performance_metrics,
            "validation_metadata": self.validation_metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def __str__(self) -> str:
        """Human-readable string representation"""
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        counts = (
            f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}, Info: {len(self.info)}"
        )
        return f"ValidationResult({status}, {counts})"

    def __bool__(self) -> bool:
        """Allow using ValidationResult in boolean context"""
        return self.is_valid


class ValidationResultBuilder:
    """Builder pattern for creating ValidationResult objects"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.performance_metrics = None
        self.validation_metadata = None

    def add_error(
        self,
        error_type: str,
        message: str,
        path: str = None,
        mapping: str = None,
        severity: str = ValidationSeverity.ERROR.value,
        **kwargs,
    ) -> "ValidationResultBuilder":
        """Add an error message"""
        error = {
            "type": error_type,
            "message": message,
            "severity": severity,
            "path": path,
            "mapping": mapping,
            **kwargs,
        }
        # Remove None values
        error = {k: v for k, v in error.items() if v is not None}
        self.errors.append(error)
        return self

    def add_warning(
        self, warning_type: str, message: str, path: str = None, mapping: str = None, **kwargs
    ) -> "ValidationResultBuilder":
        """Add a warning message"""
        warning = {
            "type": warning_type,
            "message": message,
            "severity": ValidationSeverity.WARNING.value,
            "path": path,
            "mapping": mapping,
            **kwargs,
        }
        # Remove None values
        warning = {k: v for k, v in warning.items() if v is not None}
        self.warnings.append(warning)
        return self

    def add_info(
        self, info_type: str, message: str, path: str = None, mapping: str = None, **kwargs
    ) -> "ValidationResultBuilder":
        """Add an info message"""
        info = {
            "type": info_type,
            "message": message,
            "severity": ValidationSeverity.INFO.value,
            "path": path,
            "mapping": mapping,
            **kwargs,
        }
        # Remove None values
        info = {k: v for k, v in info.items() if v is not None}
        self.info.append(info)
        return self

    def set_performance_metrics(self, metrics: Dict[str, Any]) -> "ValidationResultBuilder":
        """Set performance metrics"""
        self.performance_metrics = metrics
        return self

    def set_validation_metadata(self, metadata: Dict[str, Any]) -> "ValidationResultBuilder":
        """Set validation metadata"""
        self.validation_metadata = metadata
        return self

    def build(self) -> ValidationResult:
        """Build the ValidationResult"""
        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            info=self.info,
            performance_metrics=self.performance_metrics,
            validation_metadata=self.validation_metadata,
        )


# Convenience functions for creating ValidationResult objects
def create_success_result(info_message: str = None) -> ValidationResult:
    """Create a successful validation result"""
    builder = ValidationResultBuilder()
    if info_message:
        builder.add_info("validation_success", info_message)
    return builder.build()


def create_error_result(
    error_type: str, message: str, path: str = None, mapping: str = None, **kwargs
) -> ValidationResult:
    """Create a validation result with a single error"""
    return ValidationResultBuilder().add_error(error_type, message, path, mapping, **kwargs).build()


def create_exception_result(
    exception: Exception, path: str = None, context: str = None
) -> ValidationResult:
    """Create a validation result from an exception"""
    error_message = f"{context}: {str(exception)}" if context else str(exception)
    return create_error_result(
        "validation_exception",
        error_message,
        path=path,
        exception=str(exception),
        severity=ValidationSeverity.CRITICAL.value,
    )
