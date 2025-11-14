"""
Setup script for PV Testing Protocol Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pv-test-protocols",
    version="1.0.0",
    author="Test Protocols Team",
    author_email="support@example.com",
    description="Modular PV Testing Protocol Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ganeshgowri-ASA/test-protocols",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.17.0",
        "matplotlib>=3.7.0",
        "psycopg2-binary>=2.9.0",
        "sqlalchemy>=2.0.0",
        "jsonschema>=4.19.0",
        "python-dateutil>=2.8.0",
        "pytz>=2023.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "unittest-xml-reporting>=3.2.0",
        ],
        "advanced": [
            "pillow>=10.0.0",
            "opencv-python>=4.8.0",
            "reportlab>=4.0.0",
            "openpyxl>=3.1.0",
            "requests>=2.31.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pv-test-hail001=src.ui.hail_001_ui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.sql", "*.md"],
    },
)
