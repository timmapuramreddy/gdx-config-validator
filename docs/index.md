# GDX Config Validator Library - Documentation

Complete documentation for the GDX Config Validator Library - a comprehensive Python library for validating GDX (Glue DataXpress) configuration files.

## 📚 Documentation Overview

This documentation provides everything you need to understand, use, maintain, and extend the GDX Config Validator Library.

### 🚀 For Users

- **[Quick Start & Overview](README.md)** - Library overview, features, and quick start guide
- **[Usage Examples](USAGE_EXAMPLES.md)** - Comprehensive examples for all use cases
- **[API Reference](API_REFERENCE.md)** - Complete API documentation

### 🔧 For Developers

- **[Developer Guide](DEVELOPER_GUIDE.md)** - Maintenance, enhancement, and extension guide
- **[Architecture Overview](#architecture-overview)** - Understanding the library structure
- **[Contributing Guidelines](#contributing-guidelines)** - How to contribute to the library

## 🎯 Quick Navigation

### Common Tasks

| I want to... | Go to... |
|--------------|----------|
| Get started quickly | [README.md - Quick Start](README.md#quick-start) |
| See basic examples | [USAGE_EXAMPLES.md - Basic Usage](USAGE_EXAMPLES.md#basic-usage-examples) |
| Integrate with GDX Framework | [USAGE_EXAMPLES.md - Framework Integration](USAGE_EXAMPLES.md#framework-integration-examples) |
| Handle errors properly | [USAGE_EXAMPLES.md - Error Handling](USAGE_EXAMPLES.md#error-handling-strategies) |
| Add new validation rules | [DEVELOPER_GUIDE.md - Adding Rules](DEVELOPER_GUIDE.md#adding-new-validation-rules) |
| Extend operation registry | [DEVELOPER_GUIDE.md - Extending Operations](DEVELOPER_GUIDE.md#extending-operation-registry) |
| Find specific API methods | [API_REFERENCE.md](API_REFERENCE.md) |
| Optimize performance | [USAGE_EXAMPLES.md - Performance](USAGE_EXAMPLES.md#performance-optimization-examples) |

### Validation Types

| Validation Type | Description | Documentation |
|-----------------|-------------|---------------|
| **File Validation** | Validate YAML configuration files | [API: validate_file](API_REFERENCE.md#validate_file) |
| **String Validation** | Validate YAML content as string | [API: validate_string](API_REFERENCE.md#validate_string) |
| **Job Validation** | Enterprise job configuration validation | [API: validate_job_config](API_REFERENCE.md#validate_job_config) |
| **Batch Validation** | Validate multiple files in directory | [API: validate_directory](API_REFERENCE.md#validate_directory) |
| **Quick Validation** | Fast boolean validation check | [API: quick_validate](API_REFERENCE.md#quick_validate) |

## 🏗️ Architecture Overview

The GDX Config Validator Library follows a modular, extensible architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Public API Layer                        │
│  Factory Functions │ High-Level APIs │ Configuration Mgmt  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Validator Layer                          │
│  Basic Validator │ Comprehensive │ Job Validator │ SQL     │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Core Infrastructure                      │
│  BaseValidator │ Rule Engine │ Metrics │ Logging Adapter   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Foundation Layer                         │
│  Results System │ Operations Registry │ Utilities │ Parsers│
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **🔄 Extensibility**: Easy to add new validators, rules, and operations
2. **🏭 Production Ready**: Optimized for enterprise use with proper logging
3. **🔧 Developer Friendly**: Clean APIs, factory patterns, and comprehensive docs
4. **⚡ Performance**: Efficient validation with caching and parallel processing
5. **🛡️ Robust**: Comprehensive error handling and validation

## 📖 Documentation Structure

### [README.md](README.md)
**Main library documentation covering:**
- Library overview and features
- Quick start guide
- Basic usage examples
- Architecture and structure
- API reference summary

### [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
**Comprehensive usage examples including:**
- Basic validation patterns
- Advanced validation scenarios
- Framework integration (GDX, Airflow, AWS Glue)
- Production usage patterns
- Error handling strategies
- Performance optimization
- Custom validation examples

### [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
**Developer and maintenance guide covering:**
- Architecture deep dive
- Adding new validation rules
- Extending operation registry
- Creating custom validators
- Enhancing logging system
- Testing guidelines
- Performance optimization
- Maintenance best practices

### [API_REFERENCE.md](API_REFERENCE.md)
**Complete API documentation including:**
- Core classes and methods
- Validator class APIs
- Factory functions
- Configuration management
- Result classes
- Utility functions
- Operation registry
- Logging system

## 🚀 Getting Started

### Installation

The library is structured as a Python package. To use it:

1. **Add to your project:**
   ```bash
   # Copy the src/gdx_config_validator directory to your project
   # or install as a package (when published)
   ```

2. **Install dependencies:**
   ```bash
   pip install PyYAML>=6.0
   ```

3. **Basic usage:**
   ```python
   from gdx_config_validator import validate_file
   
   result = validate_file("config.yaml")
   print(f"Valid: {result.is_valid}")
   ```

### First Steps

1. **Read the [Quick Start Guide](README.md#quick-start)** for immediate usage
2. **Explore [Basic Examples](USAGE_EXAMPLES.md#basic-usage-examples)** for common patterns
3. **Check [API Reference](API_REFERENCE.md)** for specific method documentation
4. **Review [Developer Guide](DEVELOPER_GUIDE.md)** if you need to extend the library

## 🎯 Use Case Guide

### I'm a GDX Developer
- Start with [Framework Integration Examples](USAGE_EXAMPLES.md#framework-integration-examples)
- Review [Production Usage Patterns](USAGE_EXAMPLES.md#production-usage-patterns)
- Check [Error Handling Strategies](USAGE_EXAMPLES.md#error-handling-strategies)

### I'm Validating Configuration Files
- Begin with [Basic Usage Examples](USAGE_EXAMPLES.md#basic-usage-examples)
- Look at [File Validation API](API_REFERENCE.md#validate_file)
- Explore [Batch Validation](USAGE_EXAMPLES.md#example-7-directory-batch-validation)

### I'm Building Custom Validators
- Study [Creating Custom Validators](DEVELOPER_GUIDE.md#creating-custom-validators)
- Learn about [Adding New Rules](DEVELOPER_GUIDE.md#adding-new-validation-rules)
- Review [Base Infrastructure](API_REFERENCE.md#core-classes)

### I'm Extending Operations
- Read [Extending Operation Registry](DEVELOPER_GUIDE.md#extending-operation-registry)
- Check [Operation Registry API](API_REFERENCE.md#operation-registry)
- See [Custom Validation Examples](USAGE_EXAMPLES.md#custom-validation-examples)

### I'm Optimizing Performance
- Review [Performance Examples](USAGE_EXAMPLES.md#performance-optimization-examples)
- Study [Caching Strategies](DEVELOPER_GUIDE.md#performance-optimization)
- Check [Configuration Management](API_REFERENCE.md#configuration-management)

## 🔧 Contributing Guidelines

### For Bug Reports
1. Check existing issues first
2. Provide minimal reproduction case
3. Include environment details
4. Follow the issue template

### For Feature Requests
1. Describe the use case clearly
2. Explain why it's needed
3. Provide examples if possible
4. Consider backward compatibility

### For Code Contributions
1. Read the [Developer Guide](DEVELOPER_GUIDE.md) first
2. Follow existing code patterns
3. Add comprehensive tests
4. Update documentation
5. Ensure backward compatibility

### Development Setup
```bash
# Clone or download the library
cd gdx_config_validator_lib

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest src/tests/

# Run examples
python src/tests/test_yaml_validation.py
```

## 📊 Library Statistics

- **Total Lines of Code**: ~6,000+ lines
- **Validator Classes**: 5 main validators
- **Operation Types**: 20+ predefined operations
- **Operation Categories**: 6 categories
- **Test Coverage**: Comprehensive test examples
- **Documentation Pages**: 4 comprehensive guides

## 🏷️ Version Information

- **Current Version**: 1.0.0
- **API Version**: 1.0
- **Python Compatibility**: 3.7+
- **Dependencies**: PyYAML>=6.0

## 📞 Support

### Documentation Issues
- Check the relevant documentation section first
- Look for similar examples in [Usage Examples](USAGE_EXAMPLES.md)
- Review the [API Reference](API_REFERENCE.md) for method details

### Code Issues
- Review the [Developer Guide](DEVELOPER_GUIDE.md) for architecture info
- Check existing test examples for patterns
- Refer to [Error Handling Examples](USAGE_EXAMPLES.md#error-handling-strategies)

### Feature Questions
- Check if the feature exists in [API Reference](API_REFERENCE.md)
- Look for extension patterns in [Developer Guide](DEVELOPER_GUIDE.md)
- Review [Custom Examples](USAGE_EXAMPLES.md#custom-validation-examples)

## 📄 License

This library is developed by Mohan Reddy for GDX (Glue DataXpress) configuration validation.

---

**Ready to get started?** Begin with the [Quick Start Guide](README.md#quick-start) or jump to [Usage Examples](USAGE_EXAMPLES.md) for immediate practical examples!