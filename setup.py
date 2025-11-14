"""
Setup configuration for Test Protocols Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="test-protocols",
    version="1.0.0",
    description="Modular PV Testing Protocol Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Test Protocols Framework Team",
    author_email="protocols@example.com",
    url="https://github.com/ganeshgowri-ASA/test-protocols",

    packages=find_packages(where="src"),
    package_dir={"": "src"},

    python_requires=">=3.8",

    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pandas>=2.0.0",
        "streamlit>=1.28.0",
        "matplotlib>=3.7.0",
        "plotly>=5.17.0",
        "seaborn>=0.12.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "jsonschema>=4.19.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "reportlab>=4.0.0",
        "openpyxl>=3.1.0",
        "jinja2>=3.1.2",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
    ],

    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "integration": [
            "requests>=2.31.0",
            "boto3>=1.28.0",
        ],
    },

    entry_points={
        "console_scripts": [
            "test-protocols=main:main",
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

    keywords="pv photovoltaic testing protocols eva yellowing degradation",

    include_package_data=True,

    package_data={
        "": ["protocols/**/*.json", "docs/**/*.md"],
    },
)
