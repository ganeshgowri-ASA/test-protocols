"""
LETID-001 Protocol Python Module

Light and Elevated Temperature Induced Degradation Test
IEC 61215-2:2021
"""

__version__ = '1.0.0'
__protocol_id__ = 'LETID-001'
__standard__ = 'IEC 61215-2:2021'

from .validation import LETID001Validator, validate_module_id, validate_serial_number
from .processor import LETID001Processor

__all__ = [
    'LETID001Validator',
    'LETID001Processor',
    'validate_module_id',
    'validate_serial_number'
]
