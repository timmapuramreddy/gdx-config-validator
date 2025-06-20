"""
YAML Parsing utilities for GDX Config Validator Library

Extracted from gdx_yaml_parser.py - contains only parsing functionality
separate from validation logic.
"""

import yaml
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path

from .results import ValidationResult, create_error_result, create_exception_result
from .logging_adapter import get_logger


class YamlParser:
    """
    Pure YAML parsing functionality extracted from GDXYamlParser.
    Handles file reading, YAML parsing, and error handling without validation logic.
    """

    def __init__(self, logger=None, silent: bool = False):
        """
        Initialize YAML parser

        Args:
            logger: External logger instance (GDX framework, standard logging, etc.)
            silent: Force silent logging
        """
        self.logger_adapter = get_logger(logger, "YamlParser", silent)
        self._original_logger = logger

    def parse_yaml_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse YAML file and return configuration dictionary

        Args:
            file_path: Path to YAML file

        Returns:
            Dict containing parsed YAML configuration

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            ValueError: If file is empty or invalid
        """
        file_path = Path(file_path)

        # Check file existence
        if not file_path.exists():
            error_msg = f"YAML file not found: {file_path}"
            self.logger_adapter.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Check file size
        if file_path.stat().st_size == 0:
            error_msg = f"YAML file is empty: {file_path}"
            self.logger_adapter.error(error_msg)
            raise ValueError(error_msg)

        try:
            self.logger_adapter.debug(f"Parsing YAML file: {file_path}")

            with open(file_path, "r", encoding="utf-8") as file:
                content = yaml.safe_load(file)

            if content is None:
                error_msg = f"YAML file contains no data: {file_path}"
                self.logger_adapter.warning(error_msg)
                return {}

            if not isinstance(content, dict):
                error_msg = f"YAML file must contain a dictionary at root level: {file_path}"
                self.logger_adapter.error(error_msg)
                raise ValueError(error_msg)

            self.logger_adapter.info(f"Successfully parsed YAML file: {file_path}")
            return content

        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error in {file_path}: {str(e)}"
            self.logger_adapter.error(error_msg)
            raise yaml.YAMLError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error parsing {file_path}: {str(e)}"
            self.logger_adapter.error(error_msg)
            raise Exception(error_msg) from e

    def parse_yaml_string(self, yaml_string: str) -> Dict[str, Any]:
        """
        Parse YAML string and return configuration dictionary

        Args:
            yaml_string: YAML content as string

        Returns:
            Dict containing parsed YAML configuration

        Raises:
            yaml.YAMLError: If YAML parsing fails
            ValueError: If string is empty or invalid
        """
        if not yaml_string or not yaml_string.strip():
            error_msg = "YAML string is empty or contains only whitespace"
            self.logger_adapter.error(error_msg)
            raise ValueError(error_msg)

        try:
            self.logger_adapter.debug("Parsing YAML string")

            content = yaml.safe_load(yaml_string)

            if content is None:
                error_msg = "YAML string contains no data"
                self.logger_adapter.warning(error_msg)
                return {}

            if not isinstance(content, dict):
                error_msg = "YAML string must contain a dictionary at root level"
                self.logger_adapter.error(error_msg)
                raise ValueError(error_msg)

            self.logger_adapter.info("Successfully parsed YAML string")
            return content

        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error: {str(e)}"
            self.logger_adapter.error(error_msg)
            raise yaml.YAMLError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error parsing YAML string: {str(e)}"
            self.logger_adapter.error(error_msg)
            raise Exception(error_msg) from e

    def validate_yaml_structure(self, yaml_content: Dict[str, Any]) -> ValidationResult:
        """
        Basic structural validation of parsed YAML

        Args:
            yaml_content: Parsed YAML dictionary

        Returns:
            ValidationResult: Basic structure validation results
        """
        from .results import ValidationResultBuilder

        builder = ValidationResultBuilder()

        # Check if it's a dictionary
        if not isinstance(yaml_content, dict):
            builder.add_error(
                "invalid_yaml_structure",
                "YAML content must be a dictionary at root level",
                severity="critical",
            )
            return builder.build()

        # Check for common required sections
        if not yaml_content:
            builder.add_warning(
                "empty_yaml_content", "YAML file is empty or contains no configuration"
            )

        # Check for mappings section (common in GDX configs)
        if "mappings" in yaml_content:
            mappings = yaml_content["mappings"]
            if not isinstance(mappings, list):
                builder.add_error(
                    "invalid_mappings_structure", "mappings section must be a list", path="mappings"
                )
            elif len(mappings) == 0:
                builder.add_warning("empty_mappings", "mappings section is empty", path="mappings")

        # Check for settings section
        if "settings" in yaml_content:
            settings = yaml_content["settings"]
            if not isinstance(settings, dict):
                builder.add_error(
                    "invalid_settings_structure",
                    "settings section must be a dictionary",
                    path="settings",
                )

        self.logger_adapter.debug(
            f"YAML structure validation completed. Valid: {builder.errors == []}"
        )
        return builder.build()

    def _handle_yaml_errors(self, error: Exception, context: str) -> ValidationResult:
        """
        Handle YAML parsing errors and convert to ValidationResult

        Args:
            error: The exception that occurred
            context: Context information about where the error occurred

        Returns:
            ValidationResult: Error result with context
        """
        if isinstance(error, yaml.YAMLError):
            error_type = "yaml_parsing_error"
            message = f"YAML parsing failed in {context}: {str(error)}"
        elif isinstance(error, FileNotFoundError):
            error_type = "file_not_found"
            message = f"File not found in {context}: {str(error)}"
        elif isinstance(error, ValueError):
            error_type = "invalid_yaml_content"
            message = f"Invalid YAML content in {context}: {str(error)}"
        else:
            error_type = "unexpected_parsing_error"
            message = f"Unexpected error in {context}: {str(error)}"

        self.logger_adapter.error(message)
        return create_error_result(error_type, message, path=context)

    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about a YAML file without parsing it

        Args:
            file_path: Path to YAML file

        Returns:
            Dict containing file information
        """
        file_path = Path(file_path)

        info = {
            "file_path": str(file_path),
            "exists": file_path.exists(),
            "size_bytes": 0,
            "readable": False,
            "extension": file_path.suffix.lower(),
        }

        if file_path.exists():
            try:
                info["size_bytes"] = file_path.stat().st_size
                info["readable"] = os.access(file_path, os.R_OK)
                info["modified_time"] = file_path.stat().st_mtime
            except Exception as e:
                self.logger_adapter.warning(f"Could not get file info for {file_path}: {e}")

        return info

    def is_yaml_file(self, file_path: Union[str, Path]) -> bool:
        """
        Check if file appears to be a YAML file based on extension

        Args:
            file_path: Path to check

        Returns:
            bool: True if file has YAML extension
        """
        file_path = Path(file_path)
        yaml_extensions = {".yaml", ".yml"}
        return file_path.suffix.lower() in yaml_extensions


# Convenience functions for direct usage
def parse_yaml_file(file_path: Union[str, Path], logger=None) -> Dict[str, Any]:
    """
    Convenience function to parse a YAML file

    Args:
        file_path: Path to YAML file
        logger: Optional logger instance

    Returns:
        Dict containing parsed YAML configuration
    """
    parser = YamlParser(logger)
    return parser.parse_yaml_file(file_path)


def parse_yaml_string(yaml_string: str, logger=None) -> Dict[str, Any]:
    """
    Convenience function to parse a YAML string

    Args:
        yaml_string: YAML content as string
        logger: Optional logger instance

    Returns:
        Dict containing parsed YAML configuration
    """
    parser = YamlParser(logger)
    return parser.parse_yaml_string(yaml_string)


def validate_yaml_file_structure(file_path: Union[str, Path], logger=None) -> ValidationResult:
    """
    Convenience function to validate basic YAML file structure

    Args:
        file_path: Path to YAML file
        logger: Optional logger instance

    Returns:
        ValidationResult: Basic structure validation results
    """
    parser = YamlParser(logger)
    try:
        content = parser.parse_yaml_file(file_path)
        return parser.validate_yaml_structure(content)
    except Exception as e:
        return parser._handle_yaml_errors(e, str(file_path))
