from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pv-test-protocols",
    version="0.1.0",
    author="PV Testing Team",
    description="Modular PV Testing Protocol Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "streamlit>=1.28.0",
        "plotly>=5.17.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "pydantic>=2.4.0",
        "sqlalchemy>=2.0.0",
        "python-dateutil>=2.8.2",
        "alembic>=1.12.0",
        "psycopg2-binary>=2.9.7",
        "python-dotenv>=1.0.0",
        "jsonschema>=4.19.0",
        "openpyxl>=3.1.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "black>=23.9.1",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
