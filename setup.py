"""
Setup configuration for PV Testing Protocol Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="pv-testing-protocols",
    version="1.0.0",
    description="Modular PV Testing Protocol Framework with automated analysis and reporting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Quality Assurance Team",
    author_email="qa@example.com",
    url="https://github.com/ganeshgowri-ASA/test-protocols",
    license="MIT",

    packages=find_packages(exclude=["tests", "tests.*", "docs"]),

    install_requires=requirements,

    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.12.0',
            'black>=23.12.0',
            'flake8>=7.0.0',
            'mypy>=1.8.0',
        ],
        'postgres': [
            'psycopg2-binary>=2.9.9',
        ],
    },

    python_requires='>=3.9',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Testing',
    ],

    keywords='photovoltaic pv solar testing quality-assurance protocols',

    entry_points={
        'console_scripts': [
            'pv-test=ui.streamlit_app:main',
        ],
    },

    include_package_data=True,
    zip_safe=False,
)
