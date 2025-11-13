"""
GenSpark PV Testing Protocol Framework

A modular framework for photovoltaic module testing protocols with:
- Interactive Streamlit UI
- Real-time data visualization
- Comprehensive data traceability
- LIMS integration
- Automated analysis and reporting
"""

__version__ = "1.0.0"
__author__ = "GenSpark Team"

from . import protocols
from . import utils
from . import ui

__all__ = ['protocols', 'utils', 'ui']
