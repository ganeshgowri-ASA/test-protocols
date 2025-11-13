"""
Base Protocol Class
Defines the interface and common functionality for all testing protocols.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json
import hashlib
from pathlib import Path


class BaseProtocol(ABC):
    """
    Abstract base class for all testing protocols.

    All protocol implementations must inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self, protocol_id: str, protocol_name: str, version: str):
        """
        Initialize base protocol.

        Args:
            protocol_id: Unique protocol identifier (e.g., 'STC-001')
            protocol_name: Human-readable protocol name
            version: Protocol version (e.g., '2.0')
        """
        self.protocol_id = protocol_id
        self.protocol_name = protocol_name
        self.version = version
        self.audit_trail: List[Dict[str, Any]] = []
        self.test_data: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}
        self.validation_errors: List[str] = []
        self.warnings: List[str] = []

        # Load protocol template
        self.template = self._load_template()

    def _load_template(self) -> Dict[str, Any]:
        """Load protocol JSON template."""
        template_path = Path(__file__).parent.parent.parent.parent / 'templates' / 'protocols' / f'{self.protocol_id.lower().replace("-", "_")}.json'

        if template_path.exists():
            with open(template_path, 'r') as f:
                return json.load(f)
        else:
            return {}

    def log_action(self, action: str, data: Any, user_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None):
        """
        Log an action to the audit trail for complete traceability.

        Args:
            action: Description of the action performed
            data: Data associated with the action
            user_id: User who performed the action
            metadata: Additional metadata (IP address, session ID, etc.)
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'data': data,
            'user_id': user_id,
            'metadata': metadata or {}
        }

        # Add data hash for integrity verification
        data_str = json.dumps(data, sort_keys=True, default=str)
        entry['data_hash'] = hashlib.sha256(data_str.encode()).hexdigest()

        self.audit_trail.append(entry)

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Return complete audit trail."""
        return self.audit_trail

    def add_validation_error(self, error: str):
        """Add a validation error."""
        self.validation_errors.append(error)

    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)

    def clear_validation_errors(self):
        """Clear all validation errors."""
        self.validation_errors = []

    def clear_warnings(self):
        """Clear all warnings."""
        self.warnings = []

    @abstractmethod
    def render_ui(self) -> Dict[str, Any]:
        """
        Render the interactive user interface.

        Returns:
            Dict containing UI configuration with tabs, fields, and components
        """
        pass

    @abstractmethod
    def validate_setup(self, setup_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate test setup parameters.

        Args:
            setup_data: Dictionary containing setup parameters

        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass

    @abstractmethod
    def execute_test(self, test_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the test protocol.

        Args:
            test_params: Dictionary containing test parameters

        Returns:
            Dictionary containing test results
        """
        pass

    @abstractmethod
    def analyze_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze raw test data and extract key parameters.

        Args:
            raw_data: Raw test data

        Returns:
            Dictionary containing analyzed results
        """
        pass

    @abstractmethod
    def generate_graphs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate interactive graphs and visualizations.

        Args:
            data: Data to visualize

        Returns:
            Dictionary containing graph configurations (Plotly JSON)
        """
        pass

    @abstractmethod
    def validate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate test results against acceptance criteria.

        Args:
            results: Test results to validate

        Returns:
            Dictionary containing validation status and details
        """
        pass

    @abstractmethod
    def calculate_uncertainty(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate measurement uncertainty.

        Args:
            results: Test results

        Returns:
            Dictionary containing uncertainty analysis
        """
        pass

    @abstractmethod
    def generate_report(self, format: str = 'pdf') -> bytes:
        """
        Generate test report.

        Args:
            format: Report format ('pdf', 'excel', 'json')

        Returns:
            Report as bytes
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Return protocol metadata."""
        return {
            'protocol_id': self.protocol_id,
            'protocol_name': self.protocol_name,
            'version': self.version,
            'template': self.template.get('metadata', {})
        }

    def save_state(self) -> Dict[str, Any]:
        """Save current protocol state."""
        return {
            'protocol_id': self.protocol_id,
            'version': self.version,
            'test_data': self.test_data,
            'results': self.results,
            'audit_trail': self.audit_trail,
            'validation_errors': self.validation_errors,
            'warnings': self.warnings,
            'timestamp': datetime.now().isoformat()
        }

    def load_state(self, state: Dict[str, Any]):
        """Load protocol state."""
        self.test_data = state.get('test_data', {})
        self.results = state.get('results', {})
        self.audit_trail = state.get('audit_trail', [])
        self.validation_errors = state.get('validation_errors', [])
        self.warnings = state.get('warnings', [])
