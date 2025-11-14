"""
PV Testing Protocol Framework
Setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pv-testing-framework",
    version="1.0.0",
    author="PV Testing Framework Team",
    author_email="contact@example.com",
    description="Modular PV Testing Protocol Framework with JSON-based dynamic templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ganeshgowri-ASA/test-protocols",
    project_urls={
        "Bug Tracker": "https://github.com/ganeshgowri-ASA/test-protocols/issues",
        "Documentation": "https://github.com/ganeshgowri-ASA/test-protocols/docs",
        "Source Code": "https://github.com/ganeshgowri-ASA/test-protocols",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "jsonschema>=4.17.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "psycopg2-binary>=2.9.5",
        "SQLAlchemy>=2.0.0",
        "streamlit>=1.28.0",
        "plotly>=5.14.0",
        "python-dateutil>=2.8.2",
        "pyyaml>=6.0.0",
        "python-dotenv>=1.0.0",
        "jinja2>=3.1.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "pylint>=2.17.0",
            "ipython>=8.14.0",
            "jupyter>=1.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "analysis": [
            "scipy>=1.11.0",
            "scikit-learn>=1.3.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
        ],
        "export": [
            "openpyxl>=3.1.0",
            "xlsxwriter>=3.1.0",
            "fpdf2>=2.7.0",
            "Pillow>=10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pv-test=src.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "protocols/templates/*.json",
            "protocols/schemas/*.json",
            "database/*.sql",
            "database/migrations/*.sql",
        ],
    },
    keywords=[
        "photovoltaic",
        "pv",
        "testing",
        "degradation",
        "quality-control",
        "solar",
        "reliability",
        "IEC61215",
        "IEC61730",
    ],
    zip_safe=False,
)
