"""
Setup configuration for test-protocols package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="test-protocols",
    version="1.0.0",
    description="Modular PV Testing Protocol Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ASA Test Engineering",
    author_email="test-protocols@example.com",
    url="https://github.com/ganeshgowri-ASA/test-protocols",
    license="MIT",

    packages=find_packages(where="src"),
    package_dir={"": "src"},

    include_package_data=True,
    package_data={
        "": ["*.json", "*.sql"],
    },

    python_requires=">=3.8",

    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "sqlalchemy>=1.4.0",
        "alembic>=1.12.0",
        "streamlit>=1.28.0",
        "plotly>=5.17.0",
        "python-dateutil>=2.8.2",
        "jsonschema>=4.19.0",
    ],

    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },

    entry_points={
        "console_scripts": [
            "wind-001=protocols.wind_001:main",
        ],
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],

    keywords="pv solar testing protocols wind-load mechanical",
)
