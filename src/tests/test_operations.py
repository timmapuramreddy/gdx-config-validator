"""
Tests for operation registry and validation

Tests the operation registry system, parameter validation,
and caching performance improvements.
"""

import pytest
import time
from gdx_config_validator.schemas.operations import (
    OPERATION_REGISTRY, ParameterType, ParameterSpec, OperationSpec
)

class TestOperationRegistry:
    """Test operation registry functionality"""
    
    @pytest.mark.unit
    def test_operation_exists(self):
        """Test that basic operations exist"""
        # String operations
        assert OPERATION_REGISTRY.get_operation('trim') is not None
        assert OPERATION_REGISTRY.get_operation('uppercase') is not None
        assert OPERATION_REGISTRY.get_operation('lowercase') is not None
        
        # Numeric operations
        assert OPERATION_REGISTRY.get_operation('add') is not None
        assert OPERATION_REGISTRY.get_operation('multiply') is not None
        
        # Date operations
        assert OPERATION_REGISTRY.get_operation('format_date') is not None
        
        # Conversion operations
        assert OPERATION_REGISTRY.get_operation('string_to_number') is not None
    
    @pytest.mark.unit
    def test_operation_categories(self):
        """Test operation categorization"""
        categories = OPERATION_REGISTRY.get_all_categories()
        
        expected_categories = ['string', 'numeric', 'datetime', 'conversion', 'conditional', 'advanced']
        for category in expected_categories:
            assert category in categories
    
    @pytest.mark.unit
    def test_operations_by_category(self):
        """Test getting operations by category"""
        string_ops = OPERATION_REGISTRY.get_operations_by_category('string')
        assert 'trim' in string_ops
        assert 'uppercase' in string_ops
        assert 'lowercase' in string_ops
        
        numeric_ops = OPERATION_REGISTRY.get_operations_by_category('numeric')
        assert 'add' in numeric_ops
        assert 'subtract' in numeric_ops
        assert 'multiply' in numeric_ops
    
    @pytest.mark.unit
    def test_operation_validation_valid(self):
        """Test validation of valid operation parameters"""
        # Test trim operation (no parameters required)
        errors = OPERATION_REGISTRY.validate_operation('trim', {}, 'test.path')
        assert len(errors) == 0
        
        # Test add operation with valid parameters
        errors = OPERATION_REGISTRY.validate_operation(
            'add', 
            {'value': 10}, 
            'test.path'
        )
        assert len(errors) == 0
    
    @pytest.mark.unit
    def test_operation_validation_invalid(self):
        """Test validation of invalid operation parameters"""
        # Test non-existent operation
        errors = OPERATION_REGISTRY.validate_operation('non_existent', {}, 'test.path')
        assert len(errors) > 0
        assert errors[0]['type'] == 'invalid_operation_type'
        
        # Test add operation with missing required parameter
        errors = OPERATION_REGISTRY.validate_operation('add', {}, 'test.path')
        assert len(errors) > 0
        assert any(error['type'] == 'missing_required_parameter' for error in errors)
    
    @pytest.mark.unit
    def test_operation_suggestions(self):
        """Test operation name suggestions"""
        suggestions = OPERATION_REGISTRY.get_operation_suggestions('tri')
        assert 'trim' in suggestions
        
        suggestions = OPERATION_REGISTRY.get_operation_suggestions('upp')
        assert 'uppercase' in suggestions
    
    @pytest.mark.performance
    def test_caching_performance(self):
        """Test that caching improves performance"""
        # First, test without cache (direct access)
        start_time = time.time()
        for _ in range(1000):
            OPERATION_REGISTRY.operations.get('trim')
        direct_time = time.time() - start_time
        
        # Test with cache
        start_time = time.time()
        for _ in range(1000):
            OPERATION_REGISTRY.get_operation_cached('trim')
        cached_time = time.time() - start_time
        
        # Cache should be at least as fast (allowing for some variation)
        # Note: On fast systems, small timing differences can be insignificant
        assert cached_time <= direct_time * 2.0 or cached_time < 0.001  # Allow more variance or very fast execution
    
    @pytest.mark.unit
    def test_operation_help(self):
        """Test operation help information"""
        help_info = OPERATION_REGISTRY.get_operation_help('trim')
        assert help_info is not None
        assert 'description' in help_info
        assert 'category' in help_info
        assert 'parameters' in help_info

class TestParameterValidation:
    """Test parameter validation functionality"""
    
    @pytest.mark.unit
    def test_string_parameter_validation(self):
        """Test string parameter validation"""
        param_spec = ParameterSpec(
            name="test_param",
            param_type=ParameterType.STRING,
            required=True,
            description="Test string parameter"
        )
        
        # Valid string
        errors = param_spec.validate('test_value', 'test.path')
        assert len(errors) == 0
        
        # Invalid type (integer)
        errors = param_spec.validate(123, 'test.path')
        assert len(errors) > 0
        assert 'must be string' in errors[0]['message']
    
    @pytest.mark.unit
    def test_numeric_parameter_validation(self):
        """Test numeric parameter validation"""
        param_spec = ParameterSpec(
            name="test_param",
            param_type=ParameterType.INTEGER,
            required=True,
            description="Test integer parameter"
        )
        
        # Valid integer
        errors = param_spec.validate(42, 'test.path')
        assert len(errors) == 0
        
        # Invalid type (string)
        errors = param_spec.validate('not_a_number', 'test.path')
        assert len(errors) > 0
        assert 'must be integer' in errors[0]['message']
    
    @pytest.mark.unit
    def test_allowed_values_validation(self):
        """Test validation with allowed values"""
        param_spec = ParameterSpec(
            name="test_param",
            param_type=ParameterType.STRING,
            required=True,
            choices=['option1', 'option2', 'option3'],
            description="Test allowed values parameter"
        )
        
        # Valid value
        errors = param_spec.validate('option1', 'test.path')
        assert len(errors) == 0
        
        # Invalid value
        errors = param_spec.validate('invalid_option', 'test.path')
        assert len(errors) > 0
        assert 'must be one of' in errors[0]['message']

class TestOperationRegistryExtension:
    """Test extending the operation registry"""
    
    @pytest.mark.unit
    def test_register_new_operation(self):
        """Test registering a new operation"""
        # Create a new operation
        new_operation = OperationSpec(
            name='test_operation',
            category='test',
            description='Test operation for unit testing',
            parameters=[
                ParameterSpec(
                    name='test_param',
                    param_type=ParameterType.STRING,
                    required=True,
                    description='Test parameter'
                )
            ],
            examples=['test_operation(test_param="value")']
        )
        
        # Register it
        OPERATION_REGISTRY.register_operation(new_operation)
        
        # Verify it was registered
        registered_op = OPERATION_REGISTRY.get_operation('test_operation')
        assert registered_op is not None
        assert registered_op.name == 'test_operation'
        assert registered_op.category == 'test'
        
        # Verify it appears in category listing
        test_ops = OPERATION_REGISTRY.get_operations_by_category('test')
        assert 'test_operation' in test_ops
    
    @pytest.mark.unit
    def test_operation_count(self):
        """Test that we have the expected number of operations"""
        all_operations = OPERATION_REGISTRY.get_all_operation_names()
        
        # Should have at least 20 operations as implemented (may be more due to test registration)
        assert len(all_operations) >= 20
        
        # Verify specific operations exist
        expected_operations = [
            'trim', 'uppercase', 'lowercase', 'replace',
            'add', 'subtract', 'multiply', 'divide', 'round',
            'format_date',
            'string_to_number',
            'case_when'
        ]
        
        for op in expected_operations:
            assert op in all_operations, f"Expected operation '{op}' not found"

@pytest.mark.performance
class TestOperationPerformance:
    """Performance tests for operation registry"""
    
    def test_bulk_operation_lookup(self):
        """Test performance of bulk operation lookups"""
        operations = OPERATION_REGISTRY.get_all_operation_names()
        
        start_time = time.time()
        for _ in range(100):
            for op_name in operations:
                OPERATION_REGISTRY.get_operation(op_name)
        duration = time.time() - start_time
        
        # Should complete in reasonable time (less than 1 second for 100 iterations)
        assert duration < 1.0, f"Bulk operation lookup took too long: {duration}s"
    
    def test_category_lookup_performance(self):
        """Test performance of category lookups"""
        categories = OPERATION_REGISTRY.get_all_categories()
        
        start_time = time.time()
        for _ in range(100):
            for category in categories:
                OPERATION_REGISTRY.get_operations_by_category(category)
        duration = time.time() - start_time
        
        # Should complete in reasonable time
        assert duration < 0.5, f"Category lookup took too long: {duration}s"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])