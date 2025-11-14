"""
Custom Exception Classes

Defines custom exceptions for the test protocols framework.
"""


class ProtocolError(Exception):
    """Base exception for protocol-related errors."""
    pass


class ProtocolValidationError(ProtocolError):
    """Raised when protocol validation fails."""
    pass


class MeasurementError(ProtocolError):
    """Raised when measurement collection fails."""
    pass


class QCError(ProtocolError):
    """Raised when quality control check fails."""
    pass


class AnalysisError(ProtocolError):
    """Raised when data analysis fails."""
    pass


class IntegrationError(ProtocolError):
    """Raised when external system integration fails."""
    pass
