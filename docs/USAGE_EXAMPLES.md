# Usage Examples - GDX Config Validator Library

Comprehensive examples demonstrating various use cases and patterns for the GDX Config Validator Library.

## 📋 Table of Contents

1. [Basic Usage Examples](#basic-usage-examples)
2. [Advanced Validation Scenarios](#advanced-validation-scenarios)
3. [Framework Integration Examples](#framework-integration-examples)
4. [Production Usage Patterns](#production-usage-patterns)
5. [Error Handling Strategies](#error-handling-strategies)
6. [Performance Optimization Examples](#performance-optimization-examples)
7. [Custom Validation Examples](#custom-validation-examples)

## 🚀 Basic Usage Examples

### Example 1: Simple File Validation

```python
from gdx_config_validator import validate_file, ValidatorType

# Basic file validation
result = validate_file("job_config.yaml")

print(f"Is Valid: {result.is_valid}")
print(f"Errors: {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")

# Show errors if any
if not result.is_valid:
    print("\nValidation Errors:")
    for i, error in enumerate(result.errors, 1):
        print(f"{i}. {error['message']}")
        if 'path' in error:
            print(f"   Location: {error['path']}")
        if 'suggestion' in error:
            print(f"   💡 Suggestion: {error['suggestion']}")
```

### Example 2: Quick Boolean Validation

```python
from gdx_config_validator import quick_validate

# Quick validation for simple yes/no checks
config_files = [
    "job1.yaml",
    "job2.yaml", 
    "job3.yaml"
]

for config_file in config_files:
    is_valid = quick_validate(config_file)
    status = "✅ Valid" if is_valid else "❌ Invalid"
    print(f"{config_file}: {status}")
```

### Example 3: String Validation

```python
from gdx_config_validator import validate_string, ValidatorType

yaml_content = """
settings:
  env: dev
  load: incremental

mappings:
  - mapping_name: customer_data
    source_table: raw_customers
    target_table: processed_customers
    source_columns_interested:
      - "customer_id"
      - "customer_name as name"
      - "email_address as email"
    column_transformations:
      - source_alias: name
        target_column: customer_name
        data_type: VARCHAR(255)
        transformation_type: string_manipulation
        transformations:
          - type: trim
          - type: upper_case
"""

result = validate_string(yaml_content, ValidatorType.COMPREHENSIVE)
print(f"String validation result: {result.is_valid}")
```

### Example 4: Factory Pattern Usage

```python
from gdx_config_validator import create_validator, ValidatorType

# Create different types of validators
basic_validator = create_validator(ValidatorType.BASIC)
comprehensive_validator = create_validator(ValidatorType.COMPREHENSIVE)
sql_validator = create_validator(ValidatorType.SQL_ENHANCED)

# Use them for different validation needs
config_data = {...}  # Your parsed YAML

basic_result = basic_validator.validate(config_data)
comprehensive_result = comprehensive_validator.validate_comprehensive(config_data)

print(f"Basic validation: {basic_result.is_valid}")
print(f"Comprehensive validation: {comprehensive_result.is_valid}")
```

## 🔧 Advanced Validation Scenarios

### Example 5: Job-Level Validation with SQL Support

```python
from gdx_config_validator import validate_job_config
from gdx_config_validator.parsers import parse_yaml_file

# Load and validate job configuration
config_data = parse_yaml_file("complex_job.yaml")

# Standard job validation
is_valid, summary = validate_job_config(config_data)
print(f"Standard validation: {is_valid}")
print(f"Summary: {summary}")

# Enhanced validation with SQL expression analysis
is_valid_sql, summary_sql = validate_job_config(
    config_data, 
    include_sql_validation=True
)
print(f"SQL-enhanced validation: {is_valid_sql}")
print(f"Enhanced summary: {summary_sql}")
```

### Example 6: Individual Mapping Validation

```python
from gdx_config_validator import validate_mapping_config

# Extract and validate individual mappings
config_data = parse_yaml_file("multi_mapping_job.yaml")

for i, mapping in enumerate(config_data.get('mappings', [])):
    mapping_name = mapping.get('mapping_name', f'unnamed_{i}')
    
    # Validate each mapping individually
    is_valid, summary = validate_mapping_config(
        mapping,
        include_sql_validation=True
    )
    
    status = "✅" if is_valid else "❌"
    print(f"{status} Mapping '{mapping_name}': {summary}")
    
    if not is_valid:
        print(f"   Details: {summary}")
```

### Example 7: Directory Batch Validation

```python
from gdx_config_validator import validate_directory, get_validation_summary

# Validate all YAML files in a directory
results = validate_directory(
    "config_files/",
    pattern="*.yaml",
    validator_type=ValidatorType.COMPREHENSIVE
)

# Generate summary report
summary = get_validation_summary(results)

print("📊 Batch Validation Summary")
print("=" * 40)
print(f"Total files: {summary['total_count']}")
print(f"Valid files: {summary['valid_count']}")
print(f"Invalid files: {summary['invalid_count']}")
print(f"Success rate: {summary['success_rate']:.1%}")
print(f"Total errors: {summary['total_errors']}")
print(f"Total warnings: {summary['total_warnings']}")

# Show problematic files
if summary['invalid_files']:
    print("\n❌ Files with errors:")
    for file_path in summary['invalid_files']:
        result = results[file_path]
        print(f"  - {file_path}: {len(result.errors)} errors")

if summary['files_with_warnings']:
    print("\n⚠️ Files with warnings:")
    for file_path in summary['files_with_warnings']:
        result = results[file_path]
        print(f"  - {file_path}: {len(result.warnings)} warnings")
```

### Example 8: Validator Information and Capabilities

```python
from gdx_config_validator import get_validator_info, ValidatorType

# Get information about available validators
print("📋 Available Validators:")
print("=" * 50)

validator_types = [
    ValidatorType.BASIC,
    ValidatorType.COMPREHENSIVE,
    ValidatorType.JOB,
    ValidatorType.SQL_ENHANCED
]

for validator_type in validator_types:
    info = get_validator_info(validator_type)
    if info:
        print(f"\n🔧 {validator_type.upper()}")
        print(f"   Class: {info['class']}")
        print(f"   Description: {info['description']}")
        print(f"   Features: {', '.join(info['features'])}")

# Get all validator information
all_info = get_validator_info()
print(f"\nTotal validators available: {len(all_info)}")
```

## 🏭 Framework Integration Examples

### Example 9: GDX Framework Integration

```python
from gdx_config_validator import GDXJobValidator, configure_for_production

# Configure for production environment
configure_for_production()

# Mock GDX Framework Logger (replace with actual GDX logger)
class GDXFrameworkLogger:
    """Example GDX Framework Logger"""
    
    def __init__(self, job_id):
        self.job_id = job_id
    
    def info(self, message):
        print(f"[GDX-{self.job_id}] INFO: {message}")
    
    def warning(self, message):
        print(f"[GDX-{self.job_id}] WARNING: {message}")
    
    def error(self, message):
        print(f"[GDX-{self.job_id}] ERROR: {message}")
    
    def debug(self, message):
        print(f"[GDX-{self.job_id}] DEBUG: {message}")

# Initialize with GDX logger
gdx_logger = GDXFrameworkLogger("JOB-12345")
validator = GDXJobValidator(
    logger=gdx_logger,
    validation_mode="sql_enhanced"
)

# Validate within GDX job context
job_config = parse_yaml_file("gdx_job.yaml")
is_valid, summary = validator.validate_job_configuration(job_config)

if not is_valid:
    # Log error through GDX framework
    gdx_logger.error(f"Job configuration validation failed: {summary}")
    
    # Get detailed validation history for debugging
    history = validator.get_validation_history()
    for entry in history[-3:]:  # Last 3 validations
        gdx_logger.info(f"Validation history: {entry}")
```

### Example 10: AWS Glue Integration

```python
from gdx_config_validator import ExtendedGDXJobValidator
import sys
from awsglue.utils import getResolvedOptions

# Get Glue job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'config_s3_path'])

# Glue logger integration
from awsglue.context import GlueContext
from pyspark.context import SparkContext

sc = SparkContext()
glueContext = GlueContext(sc)
logger = glueContext.get_logger()

# Initialize validator with Glue logger
validator = ExtendedGDXJobValidator(
    logger=logger,
    validation_mode="comprehensive"
)

# Download config from S3 (pseudo-code)
config_content = download_from_s3(args['config_s3_path'])

# Validate configuration
from gdx_config_validator import validate_string
result = validate_string(config_content, ValidatorType.SQL_ENHANCED)

if not result.is_valid:
    error_msg = f"Configuration validation failed with {len(result.errors)} errors"
    logger.error(error_msg)
    
    # Log each error
    for error in result.errors:
        logger.error(f"  - {error['message']}")
    
    # Fail the Glue job
    raise Exception("Configuration validation failed")

logger.info("Configuration validation passed successfully")
```

### Example 11: Airflow Integration

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from gdx_config_validator import validate_file, ValidatorType, configure_for_production

def validate_gdx_config(**context):
    """Airflow task to validate GDX configuration"""
    
    # Configure for production (minimal logging)
    configure_for_production()
    
    # Get config file path from Airflow variables
    config_path = context['dag_run'].conf.get('config_path', 'default_config.yaml')
    
    # Validate configuration
    result = validate_file(config_path, ValidatorType.SQL_ENHANCED)
    
    if not result.is_valid:
        error_summary = f"Validation failed with {len(result.errors)} errors"
        
        # Log errors to Airflow logs
        print(f"❌ {error_summary}")
        for error in result.errors:
            print(f"  - {error['message']}")
            if 'suggestion' in error:
                print(f"    💡 {error['suggestion']}")
        
        # Fail the task
        raise ValueError(error_summary)
    
    print(f"✅ Configuration validation passed")
    return {"validation_status": "passed", "config_path": config_path}

# Define Airflow DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'gdx_config_validation',
    default_args=default_args,
    description='Validate GDX configuration files',
    schedule_interval='@daily',
    catchup=False
)

# Validation task
validate_task = PythonOperator(
    task_id='validate_gdx_config',
    python_callable=validate_gdx_config,
    dag=dag
)
```

## 🎯 Production Usage Patterns

### Example 12: Configuration Management in Production

```python
from gdx_config_validator import (
    configure_for_production, configure_for_development,
    LoggingContext, validate_file
)
import os

def setup_validation_environment():
    """Setup validation based on environment"""
    
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        configure_for_production()
        print("🏭 Production mode: Errors only, optimized performance")
    elif env == 'development':
        configure_for_development()
        print("🔧 Development mode: Verbose logging enabled")
    else:
        # Default to testing/staging
        from gdx_config_validator import configure_for_testing
        configure_for_testing()
        print("🧪 Testing mode: Silent operation")

def validate_with_environment_context(config_path):
    """Validate with environment-appropriate configuration"""
    
    setup_validation_environment()
    
    # Production validation with error handling
    try:
        result = validate_file(config_path, ValidatorType.SQL_ENHANCED)
        
        if result.is_valid:
            print(f"✅ Configuration {config_path} is valid")
            return True
        else:
            print(f"❌ Configuration {config_path} has {len(result.errors)} errors")
            
            # In production, log errors but don't print details
            if os.getenv('ENVIRONMENT') == 'production':
                # Log to monitoring system (pseudo-code)
                log_to_monitoring_system({
                    'event': 'config_validation_failed',
                    'config_path': config_path,
                    'error_count': len(result.errors),
                    'errors': [error['type'] for error in result.errors]
                })
            else:
                # In development, show detailed errors
                for error in result.errors:
                    print(f"  - {error['message']}")
            
            return False
            
    except Exception as e:
        print(f"💥 Validation failed with exception: {e}")
        return False

# Usage
if __name__ == "__main__":
    config_files = ["job1.yaml", "job2.yaml", "job3.yaml"]
    
    for config_file in config_files:
        validate_with_environment_context(config_file)
```

### Example 13: Automated Validation Pipeline

```python
from gdx_config_validator import validate_directory, get_validation_summary
from pathlib import Path
import json
import datetime

class ValidationPipeline:
    """Automated validation pipeline for configuration files"""
    
    def __init__(self, config_dir: str, report_dir: str = "validation_reports"):
        self.config_dir = Path(config_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
    
    def run_validation_pipeline(self):
        """Run complete validation pipeline"""
        
        print("🚀 Starting GDX Configuration Validation Pipeline")
        print("=" * 60)
        
        # 1. Discover configuration files
        yaml_files = list(self.config_dir.glob("**/*.yaml"))
        yml_files = list(self.config_dir.glob("**/*.yml"))
        all_files = yaml_files + yml_files
        
        print(f"📁 Found {len(all_files)} configuration files")
        
        # 2. Validate all files
        print("🔍 Running validations...")
        results = validate_directory(
            self.config_dir,
            pattern="*.yaml",
            validator_type=ValidatorType.SQL_ENHANCED
        )
        
        # Also validate .yml files
        yml_results = validate_directory(
            self.config_dir,
            pattern="*.yml", 
            validator_type=ValidatorType.SQL_ENHANCED
        )
        results.update(yml_results)
        
        # 3. Generate summary
        summary = get_validation_summary(results)
        
        # 4. Create detailed report
        report = self._create_detailed_report(results, summary)
        
        # 5. Save report
        report_file = self._save_report(report)
        
        # 6. Print summary
        self._print_summary(summary, report_file)
        
        return summary, report_file
    
    def _create_detailed_report(self, results, summary):
        """Create detailed validation report"""
        
        report = {
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "total_files": summary['total_count'],
                "validation_summary": summary
            },
            "file_results": {}
        }
        
        for file_path, result in results.items():
            file_report = {
                "is_valid": result.is_valid,
                "error_count": len(result.errors),
                "warning_count": len(result.warnings),
                "errors": [],
                "warnings": []
            }
            
            # Add error details
            for error in result.errors:
                file_report["errors"].append({
                    "type": error.get('type', 'unknown'),
                    "message": error.get('message', ''),
                    "path": error.get('path', ''),
                    "severity": error.get('severity', 'error')
                })
            
            # Add warning details
            for warning in result.warnings:
                file_report["warnings"].append({
                    "type": warning.get('type', 'unknown'),
                    "message": warning.get('message', ''),
                    "path": warning.get('path', ''),
                    "severity": warning.get('severity', 'warning')
                })
            
            report["file_results"][file_path] = file_report
        
        return report
    
    def _save_report(self, report):
        """Save validation report to file"""
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"validation_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file
    
    def _print_summary(self, summary, report_file):
        """Print validation summary"""
        
        print("\n📊 Validation Pipeline Results")
        print("=" * 40)
        print(f"✅ Valid files: {summary['valid_count']}")
        print(f"❌ Invalid files: {summary['invalid_count']}")
        print(f"📈 Success rate: {summary['success_rate']:.1%}")
        print(f"🐛 Total errors: {summary['total_errors']}")
        print(f"⚠️  Total warnings: {summary['total_warnings']}")
        print(f"📄 Detailed report: {report_file}")
        
        if summary['invalid_files']:
            print(f"\n❌ Files requiring attention:")
            for file_path in summary['invalid_files'][:5]:  # Show first 5
                print(f"  - {file_path}")
            
            if len(summary['invalid_files']) > 5:
                print(f"  ... and {len(summary['invalid_files']) - 5} more")

# Usage
if __name__ == "__main__":
    pipeline = ValidationPipeline("config_files/")
    summary, report_file = pipeline.run_validation_pipeline()
    
    # Exit with error code if validation failed
    import sys
    if summary['invalid_count'] > 0:
        sys.exit(1)
```

## 🛡️ Error Handling Strategies

### Example 14: Comprehensive Error Handling

```python
from gdx_config_validator import validate_file, ValidationSeverity
from gdx_config_validator.results import ValidationResult
import logging

def robust_validation_with_error_handling(config_path: str) -> dict:
    """
    Robust validation with comprehensive error handling
    """
    
    validation_report = {
        "status": "unknown",
        "config_path": config_path,
        "validation_result": None,
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "metadata": {}
    }
    
    try:
        # Attempt validation
        result = validate_file(config_path, ValidatorType.SQL_ENHANCED)
        validation_report["validation_result"] = result
        
        if result.is_valid:
            validation_report["status"] = "valid"
            validation_report["metadata"]["message"] = "Configuration is valid"
        else:
            validation_report["status"] = "invalid"
            
            # Categorize errors by severity
            critical_errors = []
            standard_errors = []
            
            for error in result.errors:
                error_info = {
                    "type": error.get('type', 'unknown'),
                    "message": error.get('message', ''),
                    "path": error.get('path', ''),
                    "severity": error.get('severity', 'error')
                }
                
                if error.get('severity') == 'critical':
                    critical_errors.append(error_info)
                else:
                    standard_errors.append(error_info)
                
                # Collect suggestions
                if 'suggestion' in error:
                    validation_report["suggestions"].append({
                        "for_error": error.get('type', 'unknown'),
                        "suggestion": error['suggestion']
                    })
            
            validation_report["errors"] = {
                "critical": critical_errors,
                "standard": standard_errors,
                "total_count": len(result.errors)
            }
            
            # Process warnings
            for warning in result.warnings:
                validation_report["warnings"].append({
                    "type": warning.get('type', 'unknown'),
                    "message": warning.get('message', ''),
                    "path": warning.get('path', '')
                })
            
            validation_report["metadata"]["message"] = f"Configuration has {len(result.errors)} errors and {len(result.warnings)} warnings"
    
    except FileNotFoundError:
        validation_report["status"] = "file_not_found"
        validation_report["metadata"]["message"] = f"Configuration file not found: {config_path}"
        validation_report["errors"] = [{
            "type": "file_not_found",
            "message": f"File {config_path} does not exist",
            "severity": "critical"
        }]
    
    except PermissionError:
        validation_report["status"] = "permission_denied"
        validation_report["metadata"]["message"] = f"Permission denied accessing: {config_path}"
        validation_report["errors"] = [{
            "type": "permission_denied",
            "message": f"Cannot read file {config_path} due to insufficient permissions",
            "severity": "critical"
        }]
    
    except Exception as e:
        validation_report["status"] = "validation_error"
        validation_report["metadata"]["message"] = f"Validation failed with error: {str(e)}"
        validation_report["errors"] = [{
            "type": "validation_exception",
            "message": str(e),
            "severity": "critical"
        }]
        
        # Log the full exception for debugging
        logging.exception(f"Validation failed for {config_path}")
    
    return validation_report

def print_validation_report(report: dict):
    """Print formatted validation report"""
    
    config_path = report["config_path"]
    status = report["status"]
    
    print(f"\n📋 Validation Report for: {config_path}")
    print("=" * 60)
    
    # Status indicator
    status_indicators = {
        "valid": "✅ VALID",
        "invalid": "❌ INVALID", 
        "file_not_found": "📁 FILE NOT FOUND",
        "permission_denied": "🔒 PERMISSION DENIED",
        "validation_error": "💥 VALIDATION ERROR",
        "unknown": "❓ UNKNOWN"
    }
    
    print(f"Status: {status_indicators.get(status, status.upper())}")
    print(f"Message: {report['metadata'].get('message', 'No message')}")
    
    # Show errors
    if report["errors"]:
        if isinstance(report["errors"], dict):
            # Structured errors
            if report["errors"].get("critical"):
                print(f"\n🚨 Critical Errors ({len(report['errors']['critical'])}):")
                for error in report["errors"]["critical"]:
                    print(f"  - {error['message']}")
                    if error.get('path'):
                        print(f"    Location: {error['path']}")
            
            if report["errors"].get("standard"):
                print(f"\n❌ Standard Errors ({len(report['errors']['standard'])}):")
                for error in report["errors"]["standard"]:
                    print(f"  - {error['message']}")
                    if error.get('path'):
                        print(f"    Location: {error['path']}")
        else:
            # Simple error list
            print(f"\n❌ Errors ({len(report['errors'])}):")
            for error in report["errors"]:
                print(f"  - {error['message']}")
    
    # Show warnings
    if report["warnings"]:
        print(f"\n⚠️ Warnings ({len(report['warnings'])}):")
        for warning in report["warnings"]:
            print(f"  - {warning['message']}")
            if warning.get('path'):
                print(f"    Location: {warning['path']}")
    
    # Show suggestions
    if report["suggestions"]:
        print(f"\n💡 Suggestions:")
        for suggestion in report["suggestions"]:
            print(f"  - {suggestion['suggestion']}")

# Usage example
if __name__ == "__main__":
    test_files = [
        "valid_config.yaml",
        "invalid_config.yaml", 
        "nonexistent_config.yaml"
    ]
    
    for config_file in test_files:
        report = robust_validation_with_error_handling(config_file)
        print_validation_report(report)
```

### Example 15: Validation with Retry Logic

```python
import time
from typing import Optional

def validate_with_retry(config_path: str, max_retries: int = 3, 
                       retry_delay: float = 1.0) -> Optional[ValidationResult]:
    """
    Validate configuration with retry logic for transient failures
    """
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Validation attempt {attempt + 1}/{max_retries} for {config_path}")
            
            result = validate_file(config_path, ValidatorType.COMPREHENSIVE)
            
            print(f"✅ Validation successful on attempt {attempt + 1}")
            return result
            
        except FileNotFoundError:
            # Don't retry for file not found
            print(f"❌ File not found: {config_path}")
            break
            
        except PermissionError:
            # Don't retry for permission errors
            print(f"❌ Permission denied: {config_path}")
            break
            
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"💥 All {max_retries} attempts failed")
                raise
    
    return None

# Usage
try:
    result = validate_with_retry("unstable_config.yaml", max_retries=3)
    if result and result.is_valid:
        print("Configuration is valid!")
    elif result:
        print(f"Configuration has {len(result.errors)} errors")
except Exception as e:
    print(f"Validation completely failed: {e}")
```

## ⚡ Performance Optimization Examples

### Example 16: Parallel Validation for Large Datasets

```python
import concurrent.futures
from pathlib import Path
import time

def validate_large_dataset_parallel(config_directory: str, max_workers: int = 4):
    """
    Validate large number of configuration files in parallel
    """
    
    config_dir = Path(config_directory)
    yaml_files = list(config_dir.glob("**/*.yaml"))
    
    print(f"🚀 Starting parallel validation of {len(yaml_files)} files")
    print(f"👥 Using {max_workers} worker threads")
    
    start_time = time.time()
    results = {}
    
    def validate_single_file(file_path):
        """Validate a single file (worker function)"""
        try:
            result = validate_file(file_path, ValidatorType.COMPREHENSIVE)
            return str(file_path), result, None
        except Exception as e:
            return str(file_path), None, str(e)
    
    # Use ThreadPoolExecutor for I/O bound validation
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all validation tasks
        future_to_file = {
            executor.submit(validate_single_file, file_path): file_path 
            for file_path in yaml_files
        }
        
        # Collect results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(future_to_file):
            file_path_str, result, error = future.result()
            
            if error:
                print(f"❌ {file_path_str}: {error}")
                results[file_path_str] = {"error": error}
            else:
                status = "✅" if result.is_valid else "❌"
                error_count = len(result.errors) if result.errors else 0
                print(f"{status} {file_path_str}: {error_count} errors")
                results[file_path_str] = {"result": result}
            
            completed += 1
            if completed % 10 == 0:  # Progress update every 10 files
                print(f"📊 Progress: {completed}/{len(yaml_files)} files completed")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Summary
    valid_count = sum(1 for r in results.values() 
                     if "result" in r and r["result"].is_valid)
    error_count = len(yaml_files) - valid_count
    
    print(f"\n📈 Parallel Validation Summary")
    print(f"   Total files: {len(yaml_files)}")
    print(f"   Valid files: {valid_count}")
    print(f"   Invalid files: {error_count}")
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Files/second: {len(yaml_files)/duration:.2f}")
    
    return results

# Usage
if __name__ == "__main__":
    results = validate_large_dataset_parallel("large_config_dataset/", max_workers=8)
```

### Example 17: Cached Validation for Repeated Use

```python
import hashlib
import json
from typing import Dict, Any
import time

class CachedValidationManager:
    """
    Validation manager with intelligent caching
    """
    
    def __init__(self, cache_size: int = 100):
        self.cache = {}
        self.cache_size = cache_size
        self.cache_stats = {"hits": 0, "misses": 0}
    
    def validate_with_cache(self, config_path: str) -> ValidationResult:
        """
        Validate with caching based on file content hash
        """
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(config_path)
        
        # Check cache
        if file_hash in self.cache:
            self.cache_stats["hits"] += 1
            print(f"💾 Cache hit for {config_path}")
            return self.cache[file_hash]["result"]
        
        # Cache miss - perform validation
        self.cache_stats["misses"] += 1
        print(f"🔍 Cache miss for {config_path} - validating...")
        
        start_time = time.time()
        result = validate_file(config_path, ValidatorType.COMPREHENSIVE)
        validation_time = time.time() - start_time
        
        # Store in cache
        self._store_in_cache(file_hash, result, config_path, validation_time)
        
        return result
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            # Use file path + timestamp as fallback
            return hashlib.sha256(f"{file_path}_{time.time()}".encode()).hexdigest()
    
    def _store_in_cache(self, file_hash: str, result: ValidationResult, 
                       file_path: str, validation_time: float):
        """Store validation result in cache"""
        
        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry
            oldest_hash = min(self.cache.keys(), 
                            key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_hash]
            print(f"🗑️ Evicted old cache entry")
        
        self.cache[file_hash] = {
            "result": result,
            "file_path": file_path,
            "timestamp": time.time(),
            "validation_time": validation_time
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests 
                   if total_requests > 0 else 0)
        
        return {
            "cache_hits": self.cache_stats["hits"],
            "cache_misses": self.cache_stats["misses"],
            "hit_rate": hit_rate,
            "cache_size": len(self.cache),
            "total_requests": total_requests
        }
    
    def clear_cache(self):
        """Clear all cached results"""
        self.cache.clear()
        print("🧹 Cache cleared")

# Usage example
def demonstration_with_caching():
    """Demonstrate caching benefits"""
    
    cache_manager = CachedValidationManager(cache_size=50)
    
    # Test files (some duplicates to show cache benefits)
    test_files = [
        "config1.yaml",
        "config2.yaml", 
        "config1.yaml",  # Duplicate - should hit cache
        "config3.yaml",
        "config2.yaml",  # Duplicate - should hit cache
        "config1.yaml",  # Duplicate - should hit cache
    ]
    
    print("🧪 Testing cached validation...")
    
    for config_file in test_files:
        try:
            result = cache_manager.validate_with_cache(config_file)
            status = "✅" if result.is_valid else "❌"
            print(f"{status} {config_file}: validation completed")
        except Exception as e:
            print(f"❌ {config_file}: {e}")
    
    # Show cache statistics
    stats = cache_manager.get_cache_stats()
    print(f"\n📊 Cache Performance:")
    print(f"   Cache hits: {stats['cache_hits']}")
    print(f"   Cache misses: {stats['cache_misses']}")
    print(f"   Hit rate: {stats['hit_rate']:.1%}")
    print(f"   Total requests: {stats['total_requests']}")

if __name__ == "__main__":
    demonstration_with_caching()
```

## 🔧 Custom Validation Examples

### Example 18: Custom Business Rules Validator

```python
from gdx_config_validator import BaseValidator, ValidationResultBuilder

class BusinessRulesValidator(BaseValidator):
    """
    Custom validator for business-specific validation rules
    """
    
    def __init__(self, business_config: Dict[str, Any], logger=None):
        super().__init__(logger, "BusinessRulesValidator")
        self.business_config = business_config
        
        # Business rule configurations
        self.allowed_tables = business_config.get('allowed_tables', [])
        self.forbidden_patterns = business_config.get('forbidden_patterns', [])
        self.required_fields = business_config.get('required_fields', [])
        self.data_retention_days = business_config.get('data_retention_days', 2555)
    
    def validate(self, config_data: Dict[str, Any]) -> ValidationResult:
        """
        Apply business-specific validation rules
        """
        builder = ValidationResultBuilder()
        
        self.log_info("Starting business rules validation")
        
        # Apply various business rules
        self._validate_table_access_rules(config_data, builder)
        self._validate_naming_conventions(config_data, builder)
        self._validate_data_retention_compliance(config_data, builder)
        self._validate_required_business_fields(config_data, builder)
        self._validate_transformation_complexity(config_data, builder)
        
        result = builder.build()
        
        self.log_info(f"Business validation completed: {result.is_valid}")
        return result
    
    def _validate_table_access_rules(self, config_data: Dict[str, Any], 
                                   builder: ValidationResultBuilder):
        """Validate that only allowed tables are accessed"""
        
        if not self.allowed_tables:
            return  # No restrictions defined
        
        for i, mapping in enumerate(config_data.get('mappings', [])):
            source_table = mapping.get('source_table', '').lower()
            target_table = mapping.get('target_table', '').lower()
            
            # Check source table
            if source_table and source_table not in self.allowed_tables:
                builder.add_error(
                    'unauthorized_source_table',
                    f'Source table "{source_table}" is not in allowed tables list',
                    path=f'mappings[{i}].source_table',
                    severity='critical'
                )
            
            # Check target table
            if target_table and target_table not in self.allowed_tables:
                builder.add_error(
                    'unauthorized_target_table',
                    f'Target table "{target_table}" is not in allowed tables list',
                    path=f'mappings[{i}].target_table',
                    severity='critical'
                )
    
    def _validate_naming_conventions(self, config_data: Dict[str, Any],
                                   builder: ValidationResultBuilder):
        """Validate business naming conventions"""
        
        for i, mapping in enumerate(config_data.get('mappings', [])):
            mapping_name = mapping.get('mapping_name', '')
            
            # Check mapping name format
            if not self._follows_naming_convention(mapping_name):
                builder.add_warning(
                    'naming_convention_violation',
                    f'Mapping name "{mapping_name}" does not follow business naming conventions',
                    path=f'mappings[{i}].mapping_name',
                    suggestion='Use format: {department}_{datatype}_{version} (e.g., sales_customer_v1)'
                )
            
            # Check for forbidden patterns
            for pattern in self.forbidden_patterns:
                if pattern.lower() in mapping_name.lower():
                    builder.add_error(
                        'forbidden_naming_pattern',
                        f'Mapping name contains forbidden pattern "{pattern}"',
                        path=f'mappings[{i}].mapping_name',
                        severity='error'
                    )
    
    def _validate_data_retention_compliance(self, config_data: Dict[str, Any],
                                          builder: ValidationResultBuilder):
        """Validate data retention policy compliance"""
        
        for i, mapping in enumerate(config_data.get('mappings', [])):
            # Check partition bounds for retention compliance
            if 'partition_upperbound' in mapping:
                upperbound = mapping['partition_upperbound']
                
                # Simple date check (in real implementation, parse actual dates)
                if '2030' in str(upperbound) or '2029' in str(upperbound):
                    builder.add_warning(
                        'potential_retention_violation',
                        f'Partition upper bound may exceed {self.data_retention_days} day retention policy',
                        path=f'mappings[{i}].partition_upperbound',
                        suggestion=f'Ensure partition bounds comply with {self.data_retention_days} day retention policy'
                    )
    
    def _validate_required_business_fields(self, config_data: Dict[str, Any],
                                         builder: ValidationResultBuilder):
        """Validate that required business fields are present"""
        
        for required_field in self.required_fields:
            if required_field not in config_data:
                builder.add_error(
                    'missing_required_business_field',
                    f'Required business field "{required_field}" is missing',
                    path=f'root.{required_field}',
                    severity='error'
                )
    
    def _validate_transformation_complexity(self, config_data: Dict[str, Any],
                                          builder: ValidationResultBuilder):
        """Validate transformation complexity doesn't exceed business limits"""
        
        max_transformations_per_mapping = self.business_config.get('max_transformations_per_mapping', 50)
        
        for i, mapping in enumerate(config_data.get('mappings', [])):
            transformations = mapping.get('column_transformations', [])
            
            if len(transformations) > max_transformations_per_mapping:
                builder.add_warning(
                    'excessive_transformation_complexity',
                    f'Mapping has {len(transformations)} transformations, exceeding recommended limit of {max_transformations_per_mapping}',
                    path=f'mappings[{i}].column_transformations',
                    suggestion='Consider breaking this mapping into smaller, more manageable pieces'
                )
    
    def _follows_naming_convention(self, name: str) -> bool:
        """Check if name follows business naming conventions"""
        
        # Example: department_datatype_version pattern
        import re
        pattern = r'^[a-z]+_[a-z]+_v\d+$'
        return bool(re.match(pattern, name.lower()))

# Usage example
def use_business_validator():
    """Demonstrate business rules validator"""
    
    # Define business rules configuration
    business_config = {
        'allowed_tables': [
            'sales_raw', 'sales_processed', 'customer_data',
            'product_catalog', 'inventory_snapshot'
        ],
        'forbidden_patterns': ['temp', 'test', 'debug'],
        'required_fields': ['settings', 'mappings'],
        'data_retention_days': 2555,
        'max_transformations_per_mapping': 25
    }
    
    # Create business validator
    validator = BusinessRulesValidator(business_config)
    
    # Test configuration
    test_config = {
        'settings': {
            'env': 'production'
        },
        'mappings': [{
            'mapping_name': 'sales_customer_v1',  # Good naming
            'source_table': 'sales_raw',          # Allowed table
            'target_table': 'customer_processed', # Not in allowed list
            'column_transformations': [
                # ... many transformations ...
            ] * 30  # Exceeds recommended limit
        }, {
            'mapping_name': 'temp_test_mapping',  # Contains forbidden patterns
            'source_table': 'unauthorized_table', # Not allowed
            'target_table': 'sales_processed'     # Allowed
        }]
    }
    
    # Validate with business rules
    result = validator.validate(test_config)
    
    print("🏢 Business Rules Validation Results:")
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    
    if result.errors:
        print("\n❌ Business Rule Violations:")
        for error in result.errors:
            print(f"  - {error['message']}")
            if 'suggestion' in error:
                print(f"    💡 {error['suggestion']}")
    
    if result.warnings:
        print("\n⚠️ Business Rule Warnings:")
        for warning in result.warnings:
            print(f"  - {warning['message']}")

if __name__ == "__main__":
    use_business_validator()
```

This comprehensive usage examples guide provides practical patterns for integrating and using the GDX Config Validator Library in various scenarios, from simple validations to complex enterprise workflows.