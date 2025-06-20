#!/usr/bin/env python3
"""
Test script to validate test.yaml using the GDX Config Validator Library

Demonstrates various validation methods and approaches available in the library.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gdx_config_validator import (
    # Factory functions
    validate_file, validate_string, quick_validate,
    create_validator, ValidatorType,
    # Direct validator classes
    GDXYamlParser, ComprehensiveYamlValidator, GDXJobValidator, ExtendedGDXJobValidator,
    # Configuration
    configure_for_development, configure_for_testing,
    # Results
    ValidationResult
)
from gdx_config_validator.factory import (
    validate_job_config, validate_mapping_config,
    get_validator_info, setup_logging_for_standalone
)

def main():
    print("🧪 GDX Config Validator - YAML Validation Test")
    print("=" * 60)
    
    # Path to our test YAML file
    test_yaml_path = Path(__file__).parent / "test.yaml"
    
    if not test_yaml_path.exists():
        print(f"❌ Test YAML file not found: {test_yaml_path}")
        return
    
    print(f"📄 Testing with: {test_yaml_path}")
    print()
    
    # Test 1: Quick validation (simplest approach)
    print("1. 🚀 Quick Validation (Boolean result)")
    print("-" * 40)
    is_valid = quick_validate(test_yaml_path)
    print(f"Result: {'✅ Valid' if is_valid else '❌ Invalid'}")
    print()
    
    # Test 2: High-level file validation with comprehensive validator
    print("2. 📋 Comprehensive File Validation")
    print("-" * 40)
    configure_for_development()  # Enable verbose logging
    result = validate_file(test_yaml_path, ValidatorType.COMPREHENSIVE)
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    if result.errors:
        print("Error details:")
        for error in result.errors[:3]:  # Show first 3 errors
            if hasattr(error, 'message'):
                print(f"  - {error.message}")
            else:
                print(f"  - {error}")
    if result.warnings:
        print("Warning details:")
        for warning in result.warnings[:3]:  # Show first 3 warnings
            if hasattr(warning, 'message'):
                print(f"  - {warning.message}")
            else:
                print(f"  - {warning}")
    print()
    
    # Test 3: Job-level validation
    print("3. 🏢 Job Configuration Validation")
    print("-" * 40)
    try:
        # Read and parse the YAML first
        from gdx_config_validator.parsers import parse_yaml_file
        config_data = parse_yaml_file(test_yaml_path)
        
        # Validate as job config
        is_valid, summary = validate_job_config(config_data, include_sql_validation=True)
        print(f"Job Valid: {'✅' if is_valid else '❌'}")
        print(f"Summary: {summary}")
    except Exception as e:
        print(f"❌ Job validation error: {e}")
    print()
    
    # Test 4: SQL-Enhanced validation
    print("4. 🔍 SQL-Enhanced Validation")
    print("-" * 40)
    result = validate_file(test_yaml_path, ValidatorType.SQL_ENHANCED)
    print(f"SQL-Enhanced Valid: {result.is_valid}")
    print(f"Total issues: {len(result.errors) + len(result.warnings)}")
    # Show detailed error information
    if result.errors:
        print("SQL validation errors:")
        for error in result.errors[:2]:  # Show first 2 errors
            if hasattr(error, 'message'):
                print(f"  - {error.message}")
            else:
                print(f"  - {error}")
    print()
    
    # Test 5: Individual mapping validation
    print("5. 🗺️ Individual Mapping Validation")
    print("-" * 40)
    try:
        config_data = parse_yaml_file(test_yaml_path)
        if 'mappings' in config_data and config_data['mappings']:
            first_mapping = config_data['mappings'][0]
            is_valid, summary = validate_mapping_config(
                first_mapping, 
                include_sql_validation=True
            )
            print(f"Mapping '{first_mapping.get('mapping_name', 'unnamed')}' Valid: {'✅' if is_valid else '❌'}")
            print(f"Summary: {summary}")
        else:
            print("❌ No mappings found in YAML")
    except Exception as e:
        print(f"❌ Mapping validation error: {e}")
    print()
    
    # Test 6: Direct validator class usage
    print("6. 🔧 Direct Validator Class Usage")
    print("-" * 40)
    configure_for_testing()  # Silent mode for cleaner output
    
    # Using ComprehensiveYamlValidator directly
    validator = ComprehensiveYamlValidator()
    try:
        config_data = parse_yaml_file(test_yaml_path)
        result = validator.validate_comprehensive(config_data)
        print(f"Direct validator result: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
        if hasattr(result, 'performance_metrics') and result.performance_metrics:
            print(f"Performance: {result.performance_metrics}")
        else:
            print(f"Validation completed with {len(result.errors)} errors and {len(result.warnings)} warnings")
    except Exception as e:
        print(f"❌ Direct validation error: {e}")
    print()
    
    # Test 7: Validator capabilities info
    print("7. ℹ️ Validator Information")
    print("-" * 40)
    for validator_type in [ValidatorType.BASIC, ValidatorType.COMPREHENSIVE, ValidatorType.SQL_ENHANCED]:
        info = get_validator_info(validator_type)
        if info:
            print(f"{validator_type}: {info['description']}")
            print(f"  Features: {', '.join(info['features'])}")
    print()
    
    # Test 8: Error handling demonstration
    print("8. 🛠️ Error Handling Test")
    print("-" * 40)
    # Test with non-existent file
    fake_result = validate_file("non_existent.yaml", ValidatorType.BASIC)
    print(f"Non-existent file result: {'✅ Valid' if fake_result.is_valid else '❌ Invalid'}")
    if fake_result.errors:
        error = fake_result.errors[0]
        if hasattr(error, 'message'):
            print(f"Expected error: {error.message}")
        else:
            print(f"Expected error: {error}")
    
    # Test with invalid YAML string
    invalid_yaml = "mappings: [invalid: yaml: structure"
    string_result = validate_string(invalid_yaml, ValidatorType.BASIC)
    print(f"Invalid YAML string result: {'✅ Valid' if string_result.is_valid else '❌ Invalid'}")
    print()
    
    print("✅ All validation tests completed!")
    print("=" * 60)
    
    # Final summary
    print("\n📊 Library Usage Summary:")
    print("• Quick validation for simple boolean checks")
    print("• File validation with detailed error reporting")
    print("• Job-level validation for complete configurations")
    print("• SQL-enhanced validation for complex transformations")
    print("• Individual mapping validation for granular checks")
    print("• Direct validator classes for advanced use cases")
    print("• Comprehensive error handling and reporting")

if __name__ == "__main__":
    main()