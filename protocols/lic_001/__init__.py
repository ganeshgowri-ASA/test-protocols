"""
LIC-001: Low Irradiance Conditions Test Protocol
IEC 61215-1:2021

This module implements the Low Irradiance Conditions test for photovoltaic modules.
Tests are performed at 200, 400, 600, and 800 W/m² at 25°C to evaluate module
performance under low light conditions.
"""

from .protocol import LIC001Protocol
from .analysis import LIC001Analyzer
from .validation import LIC001Validator

__all__ = ["LIC001Protocol", "LIC001Analyzer", "LIC001Validator"]

__version__ = "1.0.0"
