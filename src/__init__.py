"""
Test Protocols Framework
========================

A modular PV testing protocol framework with JSON-based dynamic templates
for Streamlit/GenSpark UI with automated analysis, charting, QC, and report
generation integrated with LIMS, QMS, and Project Management systems.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Test Protocol Team"
__license__ = "MIT"

from src.core.protocol_loader import ProtocolLoader
from src.core.data_validator import DataValidator
from src.core.test_runner import TestRunner

__all__ = [
    "ProtocolLoader",
    "DataValidator",
    "TestRunner",
]
