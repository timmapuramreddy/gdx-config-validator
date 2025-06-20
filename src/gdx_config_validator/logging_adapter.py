"""
Logging Adapter for GDX Config Validator Library

Provides flexible logging that works seamlessly with:
- AWS Glue loggers (GDX Framework integration)
- Standard Python logging
- Standalone console logging
- Silent mode for production
"""

import logging
import sys
from typing import Optional, Union, Any
from abc import ABC, abstractmethod


class LoggerAdapter(ABC):
    """Abstract logger adapter for different logging backends"""

    @abstractmethod
    def info(self, message: str, *args, **kwargs):
        pass

    @abstractmethod
    def warning(self, message: str, *args, **kwargs):
        pass

    @abstractmethod
    def error(self, message: str, *args, **kwargs):
        pass

    @abstractmethod
    def debug(self, message: str, *args, **kwargs):
        pass


class StandardLoggerAdapter(LoggerAdapter):
    """Adapter for standard Python logging"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)


class GlueLoggerAdapter(LoggerAdapter):
    """Adapter for AWS Glue logger (duck-typed for GDX Framework)"""

    def __init__(self, glue_logger):
        self.logger = glue_logger

    def info(self, message: str, *args, **kwargs):
        if hasattr(self.logger, "info"):
            self.logger.info(message)
        elif hasattr(self.logger, "getLogger"):
            # Handle Glue context logger pattern
            self.logger.getLogger().info(message)

    def warning(self, message: str, *args, **kwargs):
        if hasattr(self.logger, "warning"):
            self.logger.warning(message)
        elif hasattr(self.logger, "warn"):
            self.logger.warn(message)
        elif hasattr(self.logger, "getLogger"):
            self.logger.getLogger().warning(message)

    def error(self, message: str, *args, **kwargs):
        if hasattr(self.logger, "error"):
            self.logger.error(message)
        elif hasattr(self.logger, "getLogger"):
            self.logger.getLogger().error(message)

    def debug(self, message: str, *args, **kwargs):
        if hasattr(self.logger, "debug"):
            self.logger.debug(message)
        elif hasattr(self.logger, "getLogger"):
            self.logger.getLogger().debug(message)


class SilentLoggerAdapter(LoggerAdapter):
    """Silent logger for production use without logging overhead"""

    def info(self, message: str, *args, **kwargs):
        pass

    def warning(self, message: str, *args, **kwargs):
        pass

    def error(self, message: str, *args, **kwargs):
        pass

    def debug(self, message: str, *args, **kwargs):
        pass


class ConsoleLoggerAdapter(LoggerAdapter):
    """Simple console logger for standalone usage"""

    def __init__(self, level: str = "WARNING"):
        self.level = level.upper()
        self.levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        self.min_level = self.levels.get(self.level, 2)  # Default to WARNING

    def _log(self, level: str, message: str):
        if self.levels.get(level, 1) >= self.min_level:
            prefix = {"INFO": "ℹ️ ", "WARNING": "⚠️ ", "ERROR": "❌", "DEBUG": "🔍"}
            timestamp = self._get_timestamp()
            print(
                f"{prefix.get(level, '•')} [{timestamp}] [GDX-Validator] {message}", file=sys.stderr
            )

    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        import datetime

        return datetime.datetime.now().strftime("%H:%M:%S")

    def info(self, message: str, *args, **kwargs):
        self._log("INFO", message)

    def warning(self, message: str, *args, **kwargs):
        self._log("WARNING", message)

    def error(self, message: str, *args, **kwargs):
        self._log("ERROR", message)

    def debug(self, message: str, *args, **kwargs):
        self._log("DEBUG", message)


class LoggerFactory:
    """Factory to create appropriate logger adapters based on context"""

    _default_config = {
        "standalone_level": "WARNING",  # Only show warnings/errors in standalone by default
        "silent_mode": False,
        "force_console": False,
        "debug_mode": False,
    }

    @classmethod
    def configure(cls, **config):
        """
        Configure default logging behavior for the library

        Args:
            standalone_level: Logging level for standalone usage ("DEBUG", "INFO", "WARNING", "ERROR")
            silent_mode: Disable all logging completely
            force_console: Force console logging even with external logger
            debug_mode: Enable debug logging
        """
        cls._default_config.update(config)

    @classmethod
    def create_logger(
        cls, logger: Optional[Any] = None, component: str = "", silent: bool = False
    ) -> LoggerAdapter:
        """
        Create appropriate logger adapter based on context

        Args:
            logger: External logger instance (from GDX framework, standard logging, etc.)
            component: Component name for logging context
            silent: Force silent logging for this instance

        Returns:
            LoggerAdapter: Appropriate logger adapter for the context

        Priority:
            1. Silent mode (if requested or configured)
            2. External logger (GDX Framework integration)
            3. Force console (for debugging/testing)
            4. Default standalone console logger
        """

        # Priority 1: Silent mode
        if silent or cls._default_config["silent_mode"]:
            return SilentLoggerAdapter()

        # Priority 2: External logger (GDX Framework integration)
        if logger is not None:
            return cls._adapt_external_logger(logger, component)

        # Priority 3: Force console (for testing/debugging)
        if cls._default_config["force_console"]:
            level = (
                "DEBUG"
                if cls._default_config["debug_mode"]
                else cls._default_config["standalone_level"]
            )
            return ConsoleLoggerAdapter(level)

        # Priority 4: Default standalone behavior
        level = (
            "DEBUG"
            if cls._default_config["debug_mode"]
            else cls._default_config["standalone_level"]
        )
        return ConsoleLoggerAdapter(level)

    @classmethod
    def _adapt_external_logger(cls, logger: Any, component: str) -> LoggerAdapter:
        """
        Adapt external logger to our LoggerAdapter interface

        Supports:
        - Standard Python logging.Logger
        - AWS Glue loggers (duck-typed)
        - Any logger with info/warning/error/debug methods
        """

        # Standard Python logger (has handlers attribute)
        if hasattr(logger, "info") and hasattr(logger, "handlers"):
            return StandardLoggerAdapter(logger)

        # AWS Glue logger or similar (duck-typed - has logging methods)
        elif hasattr(logger, "info") or hasattr(logger, "getLogger"):
            return GlueLoggerAdapter(logger)

        # Fallback to console if logger doesn't match expected interface
        else:
            level = (
                "DEBUG"
                if cls._default_config["debug_mode"]
                else cls._default_config["standalone_level"]
            )
            return ConsoleLoggerAdapter(level)

    @classmethod
    def reset_config(cls):
        """Reset logging configuration to defaults"""
        cls._default_config = {
            "standalone_level": "WARNING",
            "silent_mode": False,
            "force_console": False,
            "debug_mode": False,
        }

    @classmethod
    def get_config(cls) -> dict:
        """Get current logging configuration"""
        return cls._default_config.copy()


# Convenience function for direct logger creation
def get_logger(
    logger: Optional[Any] = None, component: str = "gdx-validator", silent: bool = False
) -> LoggerAdapter:
    """
    Convenience function to get a logger adapter

    Args:
        logger: External logger instance
        component: Component name for logging context
        silent: Force silent logging

    Returns:
        LoggerAdapter: Configured logger adapter
    """
    return LoggerFactory.create_logger(logger, component, silent)
