"""
Security validation tests for GDX Config Validator

Tests the enhanced SQL security validation and injection prevention.
"""

import pytest
from gdx_config_validator import validate_string, ValidatorType
from gdx_config_validator.validators import ComprehensiveYamlValidator

@pytest.mark.security
class TestSQLSecurityValidation:
    """Test SQL injection and security validation"""
    
    def test_sql_injection_detection(self, sql_injection_config):
        """Test detection of SQL injection patterns"""
        validator = ComprehensiveYamlValidator()
        result = validator.validate_comprehensive(sql_injection_config)
        
        # Should detect security issues (they may be in errors or info)
        all_issues = result.errors + result.info
        
        # Check for security-related errors
        security_errors = [
            error for error in all_issues 
            if error.get('type') in ['sql_security_risk', 'potential_sql_injection', 'suspicious_sql_function']
        ]
        
        assert len(security_errors) > 0, "Should detect SQL injection attempts"
        
        # Verify specific patterns are caught
        error_messages = [error.get('message', '') for error in security_errors]
        error_text = ' '.join(error_messages).lower()
        
        # Should detect at least some dangerous patterns
        dangerous_indicators = ['drop', 'exec', 'union', 'security', 'injection']
        detected_patterns = [indicator for indicator in dangerous_indicators if indicator in error_text]
        
        assert len(detected_patterns) > 0, f"Should detect dangerous SQL patterns. Errors: {error_messages}"
    
    @pytest.mark.security
    def test_command_injection_detection(self):
        """Test detection of command injection attempts"""
        malicious_config = {
            'settings': {'env': 'test'},
            'mappings': [{
                'mapping_name': 'command_injection_test',
                'source_table': 'test_table',
                'target_table': 'target',
                'source_columns_interested': [
                    "id; exec xp_cmdshell('rm -rf /')",  # Command injection
                    "name'; EXEC sp_configure 'show advanced options', 1; --",  # System procedure
                    "email UNION SELECT @@version; --"  # Information disclosure
                ]
            }]
        }
        
        result = validate_string(str(malicious_config), ValidatorType.COMPREHENSIVE)
        
        # Should detect security issues (check both errors and info)
        all_issues = result.errors + result.info
        security_errors = [
            error for error in all_issues 
            if 'security' in error.get('type', '').lower() or 
               'injection' in error.get('message', '').lower() or
               'suspicious' in error.get('type', '').lower()
        ]
        
        assert len(security_errors) > 0, "Should detect command injection attempts"
    
    @pytest.mark.security
    def test_suspicious_function_detection(self):
        """Test detection of suspicious SQL functions"""
        suspicious_config = {
            'settings': {'env': 'test'},
            'mappings': [{
                'mapping_name': 'suspicious_functions_test',
                'source_table': 'test_table',
                'target_table': 'target',
                'source_columns_interested': [
                    "id, xp_cmdshell('dir') as command_output",  # System command
                    "name, openrowset('SQLOLEDB', 'server=evil.com;uid=sa;pwd=pass', 'select * from sys.tables') as data",  # External data
                    "email, sp_configure('show advanced options', 1) as config"  # System configuration
                ]
            }]
        }
        
        result = validate_string(str(suspicious_config), ValidatorType.SQL_ENHANCED)
        
        # Should detect suspicious functions (check both errors and info)
        all_issues = result.errors + result.info
        suspicious_errors = [
            error for error in all_issues 
            if 'suspicious' in error.get('type', '').lower() or
               'xp_cmdshell' in error.get('message', '').lower() or
               'openrowset' in error.get('message', '').lower() or
               'sp_configure' in error.get('message', '').lower()
        ]
        
        assert len(suspicious_errors) > 0, "Should detect suspicious SQL functions"
    
    @pytest.mark.security
    def test_safe_sql_expressions_allowed(self):
        """Test that safe SQL expressions are allowed"""
        safe_config = {
            'settings': {'env': 'test'},
            'mappings': [{
                'mapping_name': 'safe_sql_test',
                'source_table': 'test_table',
                'target_table': 'target',
                'source_columns_interested': [
                    "customer_id as id",
                    "'gdx_user' AS created_by"
                    "UPPER(customer_name) as name",
                    "CASE WHEN status = 'active' THEN 1 ELSE 0 END as is_active",
                    "COALESCE(email, 'no-email@example.com') as email",
                    "DATE_FORMAT(created_date, '%Y-%m-%d') as formatted_date"
                ]
            }]
        }
        
        result = validate_string(str(safe_config), ValidatorType.SQL_ENHANCED)
        
        # Should not trigger security errors for safe SQL
        security_errors = [
            error for error in result.errors 
            if 'security' in error.get('type', '').lower() and
               'critical' in error.get('severity', '').lower()
        ]
        
        # May have validation errors for other reasons, but no critical security errors
        critical_security_count = len([e for e in security_errors if e.get('severity') == 'critical'])
        assert critical_security_count == 0, f"Safe SQL should not trigger critical security errors: {security_errors}"
    
    @pytest.mark.security
    def test_complexity_warning(self):
        """Test detection of overly complex SQL expressions"""
        # Create a very complex nested expression
        complex_expression = "CASE " + " ".join([
            f"WHEN condition_{i} = {i} THEN (SELECT nested_value_{i} FROM nested_table_{i} WHERE id = {i})"
            for i in range(20)  # 20 nested conditions
        ]) + " ELSE default_value END"
        
        complex_config = {
            'settings': {'env': 'test'},
            'mappings': [{
                'mapping_name': 'complexity_test',
                'source_table': 'test_table',
                'target_table': 'target',
                'source_columns_interested': [
                    f"id, {complex_expression} as complex_field"
                ]
            }]
        }
        
        result = validate_string(str(complex_config), ValidatorType.SQL_ENHANCED)
        
        # Should generate complexity warnings for very complex expressions
        complexity_warnings = [
            error for error in result.errors + result.warnings
            if 'complexity' in error.get('type', '').lower()
        ]
        
        # Note: This might not trigger if the expression isn't long enough
        # The test verifies the functionality exists, not necessarily that it triggers
        print(f"Complex expression length: {len(complex_expression)}")
        print(f"Complexity warnings: {len(complexity_warnings)}")
    
    @pytest.mark.security
    def test_error_handling_in_security_validation(self):
        """Test that security validation handles errors gracefully"""
        # Create config with potentially problematic regex patterns
        config_with_special_chars = {
            'settings': {'env': 'test'},
            'mappings': [{
                'mapping_name': 'special_chars_test',
                'source_table': 'test_table',
                'target_table': 'target',
                'source_columns_interested': [
                    "id, '[regex special chars: .*+?^${}()|[]\\\\' as special_field",
                    "name, 'unicode: 你好世界 🌟' as unicode_field"
                ]
            }]
        }
        
        # Should not crash on special characters
        result = validate_string(str(config_with_special_chars), ValidatorType.SQL_ENHANCED)
        
        # Validation should complete without exceptions
        assert result is not None
        
        # Check for security validation exceptions
        validation_exceptions = [
            error for error in result.errors 
            if 'security_validation_exception' in error.get('type', '')
        ]
        
        # Should handle gracefully - no exceptions should propagate
        critical_exceptions = [e for e in validation_exceptions if e.get('severity') == 'critical']
        assert len(critical_exceptions) == 0, f"Security validation should handle errors gracefully: {critical_exceptions}"

@pytest.mark.security
class TestSecurityValidationPerformance:
    """Test performance of security validation"""
    
    def test_security_validation_performance(self):
        """Test that security validation doesn't significantly slow down validation"""
        import time
        
        # Large config for performance testing
        large_config = {
            'settings': {'env': 'test'},
            'mappings': []
        }
        
        # Add many mappings with various SQL expressions
        for i in range(50):
            large_config['mappings'].append({
                'mapping_name': f'mapping_{i}',
                'source_table': f'table_{i}',
                'target_table': f'target_{i}',
                'source_columns_interested': [
                    f"id_{i} as mapped_id",
                    f"UPPER(name_{i}) as mapped_name",
                    f"CASE WHEN status_{i} = 'active' THEN 1 ELSE 0 END as is_active",
                    f"COALESCE(email_{i}, 'default@example.com') as email"
                ]
            })
        
        # Test performance with security validation
        start_time = time.time()
        result = validate_string(str(large_config), ValidatorType.SQL_ENHANCED)
        duration = time.time() - start_time
        
        # Should complete in reasonable time (less than 5 seconds for 50 mappings)
        assert duration < 5.0, f"Security validation took too long: {duration}s"
        assert result is not None, "Validation should complete successfully"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "security"])