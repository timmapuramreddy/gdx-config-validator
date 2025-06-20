#!/usr/bin/env python3
"""
Basic GDX Config Validator Example

This example demonstrates the basic usage of the GDX Config Validator Library
for validating YAML configuration files.
"""

import sys
from pathlib import Path

# Add the library to path (when using as standalone)
sys.path.insert(0, str(Path(__file__).parent.parent))

from gdx_config_validator import (
    validate_file, validate_string, quick_validate,
    ValidatorType, configure_for_development
)

def main():
    print("🧪 GDX Config Validator - Basic Example")
    print("=" * 50)
    
    # Configure for development (verbose logging)
    configure_for_development()
    
    # Example 1: Quick validation
    print("\n1. 📋 Quick Validation Example")
    print("-" * 30)
    
    sample_yaml = """
settings:
  env: development
  load: full

mappings:
  - mapping_name: example_mapping
    source_table: source_data
    target_table: processed_data
    source_columns_interested:
      - "id as record_id"
      - "name as customer_name"
      - "email as email_address"
    column_transformations:
      - source_alias: customer_name
        target_column: full_name
        data_type: VARCHAR(255)
        transformation_type: string_manipulation
        transformations:
          - type: trim
          - type: upper_case
"""
    
    # Quick boolean validation
    is_valid = quick_validate(sample_yaml)
    print(f"Quick validation result: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Example 2: Comprehensive validation with details
    print("\n2. 🔍 Comprehensive Validation Example")
    print("-" * 40)
    
    result = validate_string(sample_yaml, ValidatorType.COMPREHENSIVE)
    print(f"Comprehensive validation: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    
    if result.errors:
        print("\nErrors found:")
        for i, error in enumerate(result.errors, 1):
            print(f"  {i}. {error.get('message', 'Unknown error')}")
            if 'path' in error:
                print(f"     Location: {error['path']}")
            if 'suggestion' in error:
                print(f"     💡 Suggestion: {error['suggestion']}")
    
    # Example 3: SQL-Enhanced validation
    print("\n3. ⚡ SQL-Enhanced Validation Example")
    print("-" * 40)
    
    sql_enhanced_yaml = """
settings:
  env: development

mappings:
  - mapping_name: advanced_mapping
    source_table: transaction_data
    target_table: analytics_facts
    source_columns_interested:
      - "transaction_id"
      - "amount::decimal as transaction_amount"
      - "CASE WHEN status = 'completed' THEN 1 ELSE 0 END as is_completed"
    column_transformations:
      - source_alias: transaction_amount
        target_column: amount_usd
        data_type: DECIMAL(10,2)
        transformation_type: numeric_transformation
"""
    
    sql_result = validate_string(sql_enhanced_yaml, ValidatorType.SQL_ENHANCED)
    print(f"SQL-Enhanced validation: {'✅ Valid' if sql_result.is_valid else '❌ Invalid'}")
    
    # Example 4: File validation (if test file exists)
    print("\n4. 📄 File Validation Example")
    print("-" * 30)
    
    test_file = Path(__file__).parent.parent / "tests" / "test.yaml"
    if test_file.exists():
        file_result = validate_file(test_file, ValidatorType.COMPREHENSIVE)
        print(f"Test file validation: {'✅ Valid' if file_result.is_valid else '❌ Invalid'}")
        
        if not file_result.is_valid:
            print(f"Issues found in test file: {len(file_result.errors)} errors")
            if file_result.errors:
                print("First error:", file_result.errors[0].get('message', 'Unknown'))
    else:
        print("Test file not found, skipping file validation example")
    
    # Example 5: Different validator types
    print("\n5. 🔧 Different Validator Types")
    print("-" * 35)
    
    validator_types = [
        (ValidatorType.BASIC, "Basic YAML Parser"),
        (ValidatorType.COMPREHENSIVE, "Comprehensive Validator"),
        (ValidatorType.SQL_ENHANCED, "SQL-Enhanced Validator")
    ]
    
    simple_yaml = """
settings:
  env: test
mappings:
  - mapping_name: simple_test
    source_table: test_source
    target_table: test_target
"""
    
    for validator_type, description in validator_types:
        result = validate_string(simple_yaml, validator_type)
        status = "✅" if result.is_valid else "❌"
        print(f"{status} {description}: {len(result.errors)} errors")
    
    print("\n✅ Basic validation examples completed!")
    print("\n💡 For more advanced examples, see:")
    print("   - docs/USAGE_EXAMPLES.md")
    print("   - docs/API_REFERENCE.md")
    print("   - src/tests/test_yaml_validation.py")

if __name__ == "__main__":
    main()