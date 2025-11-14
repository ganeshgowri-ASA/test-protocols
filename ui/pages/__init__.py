"""
UI Pages Module

Import all page modules for easy access.
"""

from . import protocol_selector
from . import data_entry
from . import analysis_view
from . import reports

__all__ = [
    "protocol_selector",
    "data_entry",
    "analysis_view",
    "reports"
]
