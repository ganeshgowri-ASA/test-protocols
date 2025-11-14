"""Setup script for PV Testing Protocol Framework."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="pv-testing-protocols",
    version="1.0.0",
    description="Modular PV Testing Protocol Framework with JSON-based templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PV Testing Team",
    author_email="testing@example.com",
    url="https://github.com/your-org/test-protocols",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "sqlalchemy>=2.0.0,<3.0.0",
        "jsonschema>=4.17.0,<5.0.0",
        "streamlit>=1.28.0,<2.0.0",
        "plotly>=5.17.0,<6.0.0",
        "pandas>=2.0.0,<3.0.0",
        "alembic>=1.12.0,<2.0.0",
        "python-dateutil>=2.8.0,<3.0.0",
        "pillow>=10.0.0,<11.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0,<8.0.0",
            "pytest-cov>=4.1.0,<5.0.0",
            "pytest-mock>=3.11.0,<4.0.0",
            "ruff>=0.1.0,<0.2.0",
            "mypy>=1.5.0,<2.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0,<2.0.0",
            "mkdocs-material>=9.4.0,<10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pv-test=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Testing",
    ],
    keywords="photovoltaic pv testing quality-assurance protocols",
    project_urls={
        "Documentation": "https://your-docs-url.com",
        "Source": "https://github.com/your-org/test-protocols",
        "Tracker": "https://github.com/your-org/test-protocols/issues",
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md"],
    },
)
