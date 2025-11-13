"""
Base Protocol Class for all PV Testing Protocols

This module provides the foundation for implementing test protocols with:
- Standardized lifecycle management (setup, execute, analyze, validate, report)
- Data traceability and audit trail
- Equipment integration
- Real-time progress tracking
- Automated calculations and validations
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ProtocolStatus(Enum):
    """Protocol execution status"""
    PENDING = "pending"
    SETUP = "setup"
    RUNNING = "running"
    PAUSED = "paused"
    ANALYZING = "analyzing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProtocolStep(Enum):
    """Protocol execution steps"""
    INITIALIZATION = "initialization"
    EQUIPMENT_SETUP = "equipment_setup"
    SAMPLE_PREPARATION = "sample_preparation"
    PRE_TEST_MEASUREMENTS = "pre_test_measurements"
    MAIN_TEST = "main_test"
    POST_TEST_MEASUREMENTS = "post_test_measurements"
    DATA_ANALYSIS = "data_analysis"
    VALIDATION = "validation"
    REPORT_GENERATION = "report_generation"
    CLEANUP = "cleanup"


class BaseProtocol(ABC):
    """
    Abstract base class for all test protocols

    All protocol implementations must inherit from this class and implement:
    - setup(): Equipment configuration and preparation
    - execute(): Main test execution logic
    - analyze(): Data analysis and calculations
    - validate(): Results validation against acceptance criteria
    - generate_report(): Report generation
    """

    def __init__(self, protocol_id: str, template_path: Optional[Path] = None):
        """
        Initialize protocol

        Args:
            protocol_id: Unique protocol identifier (e.g., 'STC-001')
            template_path: Path to protocol JSON template
        """
        self.protocol_id = protocol_id
        self.template_path = template_path
        self.template_data = None

        # Execution state
        self.status = ProtocolStatus.PENDING
        self.current_step = None
        self.progress_percentage = 0
        self.start_time = None
        self.end_time = None

        # Data storage
        self.input_parameters = {}
        self.test_conditions = {}
        self.raw_data = []
        self.measurements = []
        self.analysis_results = {}
        self.validation_results = {}
        self.errors = []
        self.warnings = []

        # Equipment and resources
        self.equipment_list = []
        self.equipment_states = {}

        # Callbacks for progress updates
        self.progress_callbacks = []

        # Load template if provided
        if template_path and template_path.exists():
            self.load_template()

        logger.info(f"Initialized protocol: {protocol_id}")

    def load_template(self) -> Dict[str, Any]:
        """Load protocol template from JSON file"""
        try:
            with open(self.template_path, 'r') as f:
                self.template_data = json.load(f)
            logger.info(f"Loaded template for {self.protocol_id}")
            return self.template_data
        except Exception as e:
            logger.error(f"Failed to load template for {self.protocol_id}: {e}")
            self.errors.append(f"Template load error: {e}")
            return {}

    def set_input_parameters(self, parameters: Dict[str, Any]):
        """Set input parameters for the test"""
        self.input_parameters = parameters
        logger.info(f"Set input parameters for {self.protocol_id}: {parameters}")

    def set_test_conditions(self, conditions: Dict[str, Any]):
        """Set test conditions"""
        self.test_conditions = conditions
        logger.info(f"Set test conditions for {self.protocol_id}: {conditions}")

    def add_equipment(self, equipment_id: str, equipment_type: str):
        """Add equipment to the protocol"""
        self.equipment_list.append({
            'equipment_id': equipment_id,
            'equipment_type': equipment_type
        })
        self.equipment_states[equipment_id] = 'idle'

    def register_progress_callback(self, callback: Callable):
        """Register a callback function for progress updates"""
        self.progress_callbacks.append(callback)

    def update_progress(self, percentage: int, step: ProtocolStep, message: str = ""):
        """Update execution progress and notify callbacks"""
        self.progress_percentage = percentage
        self.current_step = step

        # Notify all registered callbacks
        for callback in self.progress_callbacks:
            try:
                callback(self.protocol_id, percentage, step.value, message)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

    def add_measurement(self, measurement_point: str, data: Dict[str, Any],
                       timestamp: Optional[datetime] = None):
        """Add measurement data"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        measurement = {
            'measurement_point': measurement_point,
            'timestamp': timestamp.isoformat(),
            'data': data
        }
        self.measurements.append(measurement)
        logger.debug(f"Added measurement: {measurement_point}")

    def add_analysis_result(self, result_type: str, value: float,
                          unit: str, pass_fail: str = "n/a"):
        """Add analysis result"""
        self.analysis_results[result_type] = {
            'value': value,
            'unit': unit,
            'pass_fail': pass_fail,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.info(f"Added analysis result: {result_type} = {value} {unit}")

    def add_error(self, error_message: str):
        """Add error message"""
        self.errors.append({
            'timestamp': datetime.utcnow().isoformat(),
            'message': error_message
        })
        logger.error(f"Protocol error: {error_message}")

    def add_warning(self, warning_message: str):
        """Add warning message"""
        self.warnings.append({
            'timestamp': datetime.utcnow().isoformat(),
            'message': warning_message
        })
        logger.warning(f"Protocol warning: {warning_message}")

    @abstractmethod
    def setup(self) -> bool:
        """
        Setup equipment and prepare for test execution

        Returns:
            bool: True if setup successful, False otherwise
        """
        pass

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the main test procedure

        Returns:
            bool: True if execution successful, False otherwise
        """
        pass

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze test data and calculate results

        Returns:
            Dict: Analysis results with calculated values
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate results against acceptance criteria

        Returns:
            bool: True if all validations pass, False otherwise
        """
        pass

    @abstractmethod
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate test report

        Returns:
            Dict: Report data structure
        """
        pass

    def run(self) -> bool:
        """
        Execute complete protocol workflow

        This is the main entry point for protocol execution.
        It orchestrates all steps in sequence.

        Returns:
            bool: True if protocol completes successfully
        """
        try:
            self.status = ProtocolStatus.SETUP
            self.start_time = datetime.utcnow()

            # Step 1: Setup
            self.update_progress(10, ProtocolStep.INITIALIZATION, "Initializing protocol...")
            if not self.setup():
                self.status = ProtocolStatus.FAILED
                self.add_error("Setup failed")
                return False

            # Step 2: Execute
            self.status = ProtocolStatus.RUNNING
            self.update_progress(30, ProtocolStep.MAIN_TEST, "Executing test...")
            if not self.execute():
                self.status = ProtocolStatus.FAILED
                self.add_error("Execution failed")
                return False

            # Step 3: Analyze
            self.status = ProtocolStatus.ANALYZING
            self.update_progress(60, ProtocolStep.DATA_ANALYSIS, "Analyzing data...")
            analysis_results = self.analyze()
            if not analysis_results:
                self.status = ProtocolStatus.FAILED
                self.add_error("Analysis failed")
                return False

            # Step 4: Validate
            self.status = ProtocolStatus.VALIDATING
            self.update_progress(80, ProtocolStep.VALIDATION, "Validating results...")
            if not self.validate():
                self.status = ProtocolStatus.FAILED
                self.add_error("Validation failed")
                return False

            # Step 5: Generate Report
            self.update_progress(90, ProtocolStep.REPORT_GENERATION, "Generating report...")
            report = self.generate_report()
            if not report:
                self.add_warning("Report generation failed")

            # Complete
            self.status = ProtocolStatus.COMPLETED
            self.end_time = datetime.utcnow()
            self.update_progress(100, ProtocolStep.CLEANUP, "Protocol completed")

            logger.info(f"Protocol {self.protocol_id} completed successfully")
            return True

        except Exception as e:
            self.status = ProtocolStatus.FAILED
            self.add_error(f"Protocol execution failed: {str(e)}")
            logger.exception(f"Protocol {self.protocol_id} failed with exception")
            return False

    def pause(self):
        """Pause protocol execution"""
        if self.status == ProtocolStatus.RUNNING:
            self.status = ProtocolStatus.PAUSED
            logger.info(f"Protocol {self.protocol_id} paused")

    def resume(self):
        """Resume protocol execution"""
        if self.status == ProtocolStatus.PAUSED:
            self.status = ProtocolStatus.RUNNING
            logger.info(f"Protocol {self.protocol_id} resumed")

    def cancel(self):
        """Cancel protocol execution"""
        self.status = ProtocolStatus.CANCELLED
        self.end_time = datetime.utcnow()
        logger.info(f"Protocol {self.protocol_id} cancelled")

    def get_state(self) -> Dict[str, Any]:
        """Get current protocol state"""
        return {
            'protocol_id': self.protocol_id,
            'status': self.status.value,
            'current_step': self.current_step.value if self.current_step else None,
            'progress_percentage': self.progress_percentage,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'input_parameters': self.input_parameters,
            'test_conditions': self.test_conditions,
            'measurements_count': len(self.measurements),
            'analysis_results': self.analysis_results,
            'validation_results': self.validation_results,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert protocol state to dictionary for serialization"""
        return {
            'protocol_id': self.protocol_id,
            'status': self.status.value,
            'progress': self.progress_percentage,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'input_parameters': self.input_parameters,
            'test_conditions': self.test_conditions,
            'measurements': self.measurements,
            'analysis_results': self.analysis_results,
            'validation_results': self.validation_results,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(protocol_id='{self.protocol_id}', status='{self.status.value}')>"
