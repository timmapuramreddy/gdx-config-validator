#!/usr/bin/env python3
"""
Comprehensive test script for the Enhanced Logging System

Demonstrates the flexible logging capabilities of the GDX Config Validator Library
for different integration scenarios.
"""

import sys
import os
sys.path.insert(0, 'src')

from gdx_config_validator import (
    GDXJobValidator, ExtendedGDXJobValidator,
    validate_gdx_job_config, validate_gdx_job_config_with_sql,
    configure_logging, get_library_logger
)
from gdx_config_validator.config import (
    configure_for_production, configure_for_development, 
    configure_for_testing, configure_for_standalone,
    LoggingContext, reset_logging_config
)

def main():
    print("🧪 GDX Config Validator - Enhanced Logging System Demo")
    print("=" * 60)
    
    # Test configuration
    test_config = {
        'mappings': [{
            'mapping_name': 'test_mapping',
            'source_table': 'source_table',
            'target_table': 'target_table',
            'column_transformations': [{
                'source_alias': 'col1',
                'target_column': 'target_col1',
                'data_type': 'VARCHAR(100)',
                'transformation_type': 'direct_mapping'
            }]
        }]
    }
    
    print("\n1. 🔇 SILENT MODE (No logging overhead)")
    print("-" * 40)
    configure_for_testing()  # Silent mode
    validator = GDXJobValidator(silent=True)
    print(f"Logger Info: {validator.get_logger_info()}")
    is_valid, summary = validate_gdx_job_config(test_config)
    print(f"Result: {is_valid} - {summary}")
    
    print("\n2. 🏭 PRODUCTION MODE (Errors only)")
    print("-" * 40)
    configure_for_production()
    validator = GDXJobValidator()
    print(f"Logger Info: {validator.get_logger_info()}")
    is_valid, summary = validate_gdx_job_config(test_config)
    print(f"Result: {is_valid} - {summary}")
    
    print("\n3. 🔧 DEVELOPMENT MODE (Verbose logging)")
    print("-" * 40)
    configure_for_development()
    validator = GDXJobValidator()
    print(f"Logger Info: {validator.get_logger_info()}")
    is_valid, summary = validate_gdx_job_config(test_config)
    print(f"Result: {is_valid} - {summary}")
    
    print("\n4. 🌐 STANDALONE MODE (Warnings and errors)")
    print("-" * 40)
    configure_for_standalone()
    validator = GDXJobValidator()
    print(f"Logger Info: {validator.get_logger_info()}")
    is_valid, summary = validate_gdx_job_config(test_config)
    print(f"Result: {is_valid} - {summary}")
    
    print("\n5. 🔄 FRAMEWORK INTEGRATION (Mock GDX logger)")
    print("-" * 40)
    
    class MockGDXLogger:
        """Mock GDX framework logger"""
        def info(self, msg): print(f"    🟢 GDX-INFO: {msg}")
        def warning(self, msg): print(f"    🟡 GDX-WARN: {msg}")
        def error(self, msg): print(f"    🔴 GDX-ERROR: {msg}")
        def debug(self, msg): print(f"    🔵 GDX-DEBUG: {msg}")
    
    reset_logging_config()  # Reset to defaults
    mock_logger = MockGDXLogger()
    validator = GDXJobValidator(logger=mock_logger)
    print(f"Logger Info: {validator.get_logger_info()}")
    is_valid, summary = validate_gdx_job_config(test_config, logger=mock_logger)
    print(f"Result: {is_valid} - {summary}")
    
    print("\n6. ⚡ TEMPORARY CONFIGURATION (Context manager)")
    print("-" * 40)
    configure_for_testing()  # Start silent
    
    with LoggingContext(debug=True, force_console=True):
        print("  📍 Inside LoggingContext (debug mode):")
        validator = GDXJobValidator()
        print(f"    Logger Info: {validator.get_logger_info()}")
        is_valid, summary = validate_gdx_job_config(test_config)
        print(f"    Result: {is_valid}")
    
    print("  📍 Outside LoggingContext (back to silent):")
    validator = GDXJobValidator()
    print(f"    Logger Info: {validator.get_logger_info()}")
    
    print("\n7. 🔬 SQL-ENHANCED VALIDATION (Extended validator)")
    print("-" * 40)
    configure_for_standalone()
    extended_validator = ExtendedGDXJobValidator(validation_mode="sql_enhanced")
    print(f"Logger Info: {extended_validator.get_logger_info()}")
    is_valid, summary = validate_gdx_job_config_with_sql(test_config)
    print(f"Result: {is_valid} - {summary}")
    
    print("\n8. 📝 CUSTOM LOGGER USAGE")
    print("-" * 40)
    logger = get_library_logger("custom-component")
    logger.info("This is a custom library logger message")
    logger.warning("This is a warning from custom component")
    logger.error("This is an error from custom component")
    
    print("\n✅ Enhanced Logging System Demo Complete!")
    print("=" * 60)
    print("\nKey Benefits:")
    print("• 🔄 Automatic adaptation to GDX framework loggers")
    print("• 🔇 Silent mode for production with zero logging overhead")
    print("• 🔧 Development mode with verbose debugging")
    print("• ⚡ Temporary configuration with context managers")
    print("• 🏭 Production-ready with configurable log levels")
    print("• 🌐 Seamless standalone usage")

if __name__ == "__main__":
    main()