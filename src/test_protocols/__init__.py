"""
PV Test Protocol Framework

A modular framework for managing and executing photovoltaic module test protocols
following international standards (IEC 61215, UL 1703, etc.).
"""

__version__ = "1.0.0"
__author__ = "Test Protocol Development Team"

from .core.protocol import Protocol, TestStep
from .core.protocol_loader import ProtocolLoader
from .core.test_executor import TestExecutor
from .core.result_analyzer import ResultAnalyzer

__all__ = [
    "Protocol",
    "TestStep",
    "ProtocolLoader",
    "TestExecutor",
    "ResultAnalyzer",
]
