"""
Setup script for gdx-config-validator library
"""
from setuptools import setup, find_packages

setup(
    name="gdx-config-validator",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)