"""
Configuration module for GDX Config Validator Library

Provides easy configuration of library-wide settings, especially logging behavior.
"""

from .logging_adapter import LoggerFactory, get_logger


def configure_logging(
    level: str = "WARNING", silent: bool = False, force_console: bool = False, debug: bool = False
):
    """
    Configure library-wide logging behavior

    Args:
        level: Logging level for standalone usage ("DEBUG", "INFO", "WARNING", "ERROR")
        silent: Disable all logging completely
        force_console: Force console logging even when external logger is provided
        debug: Enable debug logging (overrides level to DEBUG)

    Examples:
        # Verbose standalone usage (see all info messages)
        configure_logging(level="INFO")

        # Production standalone usage (only errors)
        configure_logging(level="ERROR")

        # Completely silent (no logging overhead)
        configure_logging(silent=True)

        # Force console for debugging (ignore external loggers)
        configure_logging(force_console=True, debug=True)

        # Debug mode (maximum verbosity)
        configure_logging(debug=True)
    """
    LoggerFactory.configure(
        standalone_level=level, silent_mode=silent, force_console=force_console, debug_mode=debug
    )


def get_library_logger(component: str = "gdx-validator"):
    """
    Get a library logger for direct use outside of validators

    Args:
        component: Component name for logging context

    Returns:
        LoggerAdapter: Configured logger adapter

    Example:
        from gdx_config_validator.config import get_library_logger

        logger = get_library_logger("my-component")
        logger.info("Custom logging message")
    """
    return get_logger(component=component)


def reset_logging_config():
    """
    Reset logging configuration to library defaults

    Useful for testing or when you want to clear custom configurations.
    """
    LoggerFactory.reset_config()


def get_logging_config() -> dict:
    """
    Get current logging configuration

    Returns:
        dict: Current logging configuration settings

    Example:
        config = get_logging_config()
        print(f"Current level: {config['standalone_level']}")
        print(f"Silent mode: {config['silent_mode']}")
    """
    return LoggerFactory.get_config()


# Pre-configured logging setups for common use cases
def configure_for_production():
    """Configure logging for production use (errors only, minimal overhead)"""
    configure_logging(level="ERROR", silent=False)


def configure_for_development():
    """Configure logging for development (debug mode, verbose output)"""
    configure_logging(debug=True, force_console=True)


def configure_for_testing():
    """Configure logging for testing (silent mode to avoid test output pollution)"""
    configure_logging(silent=True)


def configure_for_standalone():
    """Configure logging for standalone usage (warnings and errors only)"""
    configure_logging(level="WARNING")


# Integration helpers
class LoggingContext:
    """Context manager for temporary logging configuration"""

    def __init__(self, **config):
        self.config = config
        self.original_config = None

    def __enter__(self):
        self.original_config = get_logging_config()
        configure_logging(**self.config)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        LoggerFactory.configure(**self.original_config)


# Usage examples in docstring
"""
Common Usage Patterns:

1. GDX Framework Integration:
   # In GDX framework, pass the Glue logger
   from gdx_config_validator import GDXJobValidator
   
   validator = GDXJobValidator(logger=glue_context.get_logger())
   # Library automatically adapts to Glue logger format

2. Standalone Script (Verbose):
   from gdx_config_validator.config import configure_logging
   from gdx_config_validator import validate_gdx_job_config
   
   configure_logging(level="INFO")  # Show detailed validation steps
   result = validate_gdx_job_config(config)

3. Standalone Script (Quiet):
   from gdx_config_validator.config import configure_logging
   from gdx_config_validator import validate_gdx_job_config
   
   configure_logging(level="ERROR")  # Only show errors
   result = validate_gdx_job_config(config)

4. Production/Silent Mode:
   from gdx_config_validator.config import configure_for_production
   from gdx_config_validator import validate_gdx_job_config
   
   configure_for_production()  # Minimal logging
   result = validate_gdx_job_config(config)

5. Temporary Configuration:
   from gdx_config_validator.config import LoggingContext
   
   with LoggingContext(debug=True):
       # Debug logging enabled only in this block
       result = validate_gdx_job_config(config)
   # Returns to previous logging configuration

6. Testing Environment:
   from gdx_config_validator.config import configure_for_testing
   
   configure_for_testing()  # Silent mode for clean test output
   # Run tests...
"""
