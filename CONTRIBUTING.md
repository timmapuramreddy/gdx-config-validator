# Contributing to GDX Config Validator

Thank you for your interest in contributing to the GDX Config Validator Library! 

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/YOUR_USERNAME/gdx-config-validator.git`
3. **Set up development environment**:
   ```bash
   cd gdx-config-validator
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements-dev.txt
   ```

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific test categories
python -m pytest src/tests/ -v -k "security"
python -m pytest src/tests/ -v -k "performance"

# Run comprehensive validation test
python src/tests/test_yaml_validation.py
```

## 🔍 Code Quality

```bash
# Format code
python -m black src/gdx_config_validator/ --line-length=100

# Run linting
python -m flake8 src/gdx_config_validator/ --max-line-length=100

# Type checking (optional)
python -m mypy src/gdx_config_validator/ --ignore-missing-imports
```

## 📝 Development Guidelines

### Adding New Validators
1. Inherit from `BaseValidator`
2. Implement required methods
3. Add comprehensive tests
4. Update documentation

### Adding New Operations
1. Add to `schemas/operations.py`
2. Include parameter specifications
3. Add validation tests
4. Document with examples

### Security Considerations
- Test all SQL validation patterns
- Ensure no false positives for legitimate SQL
- Add security test cases

## 🎯 Areas for Contribution

- **New Validation Rules**: Additional validation patterns
- **Performance Optimizations**: Caching and speed improvements
- **Documentation**: Examples and guides
- **Testing**: Additional test coverage
- **Operations**: New transformation operations

## 📋 Pull Request Process

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes** with proper tests
3. **Run the test suite** to ensure everything passes
4. **Update documentation** if needed
5. **Submit a pull request** with clear description

## 🐛 Bug Reports

Use the GitHub issue template and include:
- YAML configuration (sanitized)
- Code example
- Expected vs actual behavior
- Environment details

## 💡 Feature Requests

Use the GitHub issue template and describe:
- Use case and problem
- Proposed solution
- Code examples
- Alternatives considered

## 📚 Documentation

- Keep `README.md` up to date
- Update `docs/` for new features
- Include examples in `docs/USAGE_EXAMPLES.md`
- Update `CHANGELOG.md` for releases

## 🏆 Recognition

Contributors will be acknowledged in:
- `CHANGELOG.md` for their contributions
- Documentation credits
- Release notes

Thank you for helping make GDX Config Validator better! 🎉