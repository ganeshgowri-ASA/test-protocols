"""
Setup configuration for PV Testing Protocol Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
with open(requirements_file) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="pv-testing-protocols",
    version="1.0.0",
    description="Modular PV Testing Protocol Framework with JSON-based dynamic templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PV Testing Team",
    author_email="testing@example.com",
    url="https://github.com/ganeshgowri-ASA/test-protocols",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "isort>=5.13.2",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.5.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "test-protocols=ui.streamlit.app:main",
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
    keywords="photovoltaic testing protocols IEC61215 delamination EL-imaging",
    project_urls={
        "Bug Reports": "https://github.com/ganeshgowri-ASA/test-protocols/issues",
        "Source": "https://github.com/ganeshgowri-ASA/test-protocols",
    },
)
