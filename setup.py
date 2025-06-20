"""
Setup script for GDX Config Validator Library

A comprehensive Python library for validating GDX (Glue DataXpress) configuration files
with advanced SQL security validation, performance optimization, and enterprise features.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding='utf-8')
except (UnicodeDecodeError, FileNotFoundError):
    # Fallback if README.md has encoding issues or doesn't exist
    long_description = "A comprehensive library for validating GDX (Glue DataXpress) configuration files with advanced SQL security validation, performance optimization, and enterprise features."

# Read the requirements
def read_requirements(filename):
    """Read requirements from file and return as list"""
    requirements_path = this_directory / filename
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Get version from __init__.py
def get_version():
    """Extract version from __init__.py"""
    init_path = this_directory / "src" / "gdx_config_validator" / "__init__.py"
    if init_path.exists():
        with open(init_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    # Extract version from line like: __version__ = "1.0.0"
                    return line.split('"')[1] if '"' in line else line.split("'")[1]
    return "1.0.0"

setup(
    # Basic package information
    name="gdx-config-validator",
    version=get_version(),
    description="A comprehensive library for validating GDX (Glue DataXpress) configuration files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Author information
    author="Mohan Reddy",
    author_email="mohan@example.com",
    
    # URLs
    url="https://github.com/timmapuramreddy/gdx-config-validator",
    project_urls={
        "Homepage": "https://github.com/timmapuramreddy/gdx-config-validator",
        "Repository": "https://github.com/timmapuramreddy/gdx-config-validator",
        "Issues": "https://github.com/timmapuramreddy/gdx-config-validator/issues",
        "Documentation": "https://github.com/timmapuramreddy/gdx-config-validator/blob/main/docs/README.md",
        "Changelog": "https://github.com/timmapuramreddy/gdx-config-validator/blob/main/CHANGELOG.md",
    },
    
    # License
    license="MIT",
    
    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=[
        "PyYAML>=6.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "pytest-benchmark>=4.0.0",
            "pytest-mock>=3.10.0",
            "coverage>=6.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
            "packaging>=21.0",
        ],
        "testing": [
            "pytest>=7.0.0",
            "pytest-benchmark>=4.0.0",
            "pytest-mock>=3.10.0",
            "coverage>=6.0.0",
        ],
        "lint": [
            "black>=22.0.0",
            "flake8>=5.0.0", 
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    
    # Keywords for PyPI discovery
    keywords=[
        "validation", "yaml", "configuration", "gdx", "glue", "dataxpress",
        "sql-security", "performance", "enterprise", "testing", "lru-cache"
    ],
    
    # PyPI classifiers
    classifiers=[
        # Development Status
        "Development Status :: 5 - Production/Stable",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        
        # Topics
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Markup :: YAML",
        "Topic :: Utilities",
        "Topic :: Database",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        
        # Operating System
        "Operating System :: OS Independent",
        
        # Environment
        "Environment :: Console",
        "Environment :: Web Environment",
        
        # Natural Language
        "Natural Language :: English",
    ],
    
    # Entry points (if you want to add CLI commands in the future)
    entry_points={
        "console_scripts": [
            # Future CLI tool could be added here
            # "gdx-validate=gdx_config_validator.cli:main",
        ],
    },
    
    # Data files to include
    package_data={
        "gdx_config_validator": [
            "*.md",
            "schemas/*.json",
        ],
    },
    
    # Additional metadata
    zip_safe=False,  # Don't zip the package
    
    # Test suite
    test_suite="src.tests",
    
    # Include package data
    include_package_data=True,
)

# Additional setup for development
if __name__ == "__main__":
    print("🚀 Setting up GDX Config Validator Library")
    print("=" * 50)
    print("📦 Package: gdx-config-validator")
    print(f"📋 Version: {get_version()}")
    print("🛡️ Features: SQL Security, Performance Optimization, Testing")
    print("⚡ Enhancements: LRU Caching, 22+ Tests, Enterprise-grade")
    print("📚 Documentation: Comprehensive guides and examples")
    print("=" * 50)