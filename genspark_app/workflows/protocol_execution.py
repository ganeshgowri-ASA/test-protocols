"""
Protocol Execution Workflow

Manages the execution of test protocols from start to completion
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from uuid import uuid4
import importlib

logger = logging.getLogger(__name__)


class ProtocolExecutionWorkflow:
    """Workflow for protocol execution management"""

    def __init__(self, db_session=None):
        """Initialize protocol execution workflow"""
        self.db_session = db_session
        self.current_execution = None
        self.protocol_instance = None

    def create_execution(
        self,
        service_request_id: str,
        sample_id: str,
        protocol_id: str,
        technician_id: str,
        input_parameters: Dict[str, Any],
        scheduled_start: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create a new test execution

        Args:
            service_request_id: Associated service request
            sample_id: Sample to be tested
            protocol_id: Protocol to execute
            technician_id: Technician performing the test
            input_parameters: Test input parameters
            scheduled_start: Scheduled start time (optional)

        Returns:
            Test execution object
        """
        try:
            execution_number = self._generate_execution_number()

            execution = {
                'id': str(uuid4()),
                'execution_number': execution_number,
                'service_request_id': service_request_id,
                'sample_id': sample_id,
                'protocol_id': protocol_id,
                'status': 'pending',
                'scheduled_start': scheduled_start,
                'technician_id': technician_id,
                'input_parameters': input_parameters,
                'progress_percentage': 0,
                'current_step': 'initialization',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'measurements': [],
                'analysis_results': {},
                'validation_results': {}
            }

            self.current_execution = execution
            logger.info(f"Created test execution: {execution_number}")

            # Load protocol class
            self.protocol_instance = self._load_protocol(protocol_id)
            if self.protocol_instance:
                self.protocol_instance.set_input_parameters(input_parameters)

            # In production: save to database
            if self.db_session:
                self._persist_execution(execution)

            return execution

        except Exception as e:
            logger.error(f"Failed to create execution: {e}")
            return {}

    def start_execution(self) -> bool:
        """Start protocol execution"""
        try:
            if not self.current_execution:
                logger.error("No active execution")
                return False

            if not self.protocol_instance:
                logger.error("Protocol instance not loaded")
                return False

            self.current_execution['status'] = 'setup'
            self.current_execution['actual_start'] = datetime.utcnow()
            self.current_execution['updated_at'] = datetime.utcnow()

            logger.info(f"Starting execution: {self.current_execution['execution_number']}")

            # Register progress callback
            self.protocol_instance.register_progress_callback(self._update_progress)

            # Run protocol setup
            setup_success = self.protocol_instance.setup()

            if not setup_success:
                self.current_execution['status'] = 'failed'
                logger.error("Protocol setup failed")
                return False

            self.current_execution['status'] = 'running'

            # In production: update database
            if self.db_session:
                self._persist_execution(self.current_execution)

            return True

        except Exception as e:
            logger.error(f"Failed to start execution: {e}")
            self.current_execution['status'] = 'failed'
            return False

    def execute_protocol(self) -> bool:
        """Execute the protocol"""
        try:
            if not self.protocol_instance:
                return False

            # Execute protocol
            execution_success = self.protocol_instance.execute()

            if not execution_success:
                self.current_execution['status'] = 'failed'
                logger.error("Protocol execution failed")
                return False

            logger.info("Protocol execution completed")
            return True

        except Exception as e:
            logger.error(f"Protocol execution error: {e}")
            self.current_execution['status'] = 'failed'
            return False

    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results"""
        try:
            if not self.protocol_instance:
                return {}

            self.current_execution['status'] = 'analyzing'

            analysis_results = self.protocol_instance.analyze()

            self.current_execution['analysis_results'] = analysis_results
            self.current_execution['updated_at'] = datetime.utcnow()

            logger.info("Analysis completed")

            # In production: save analysis results to database
            if self.db_session:
                self._save_analysis_results(analysis_results)

            return analysis_results

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {}

    def validate_results(self) -> bool:
        """Validate test results against acceptance criteria"""
        try:
            if not self.protocol_instance:
                return False

            self.current_execution['status'] = 'validating'

            validation_success = self.protocol_instance.validate()

            self.current_execution['validation_results'] = self.protocol_instance.validation_results
            self.current_execution['updated_at'] = datetime.utcnow()

            logger.info(f"Validation completed: {'PASS' if validation_success else 'FAIL'}")

            return validation_success

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    def complete_execution(self) -> bool:
        """Complete test execution"""
        try:
            if not self.current_execution:
                return False

            self.current_execution['status'] = 'completed'
            self.current_execution['actual_end'] = datetime.utcnow()
            self.current_execution['progress_percentage'] = 100
            self.current_execution['updated_at'] = datetime.utcnow()

            logger.info(f"Execution completed: {self.current_execution['execution_number']}")

            # In production: update database
            if self.db_session:
                self._persist_execution(self.current_execution)

            return True

        except Exception as e:
            logger.error(f"Failed to complete execution: {e}")
            return False

    def run_full_protocol(self) -> bool:
        """
        Run complete protocol workflow (setup -> execute -> analyze -> validate)

        Returns:
            Success status
        """
        try:
            if not self.protocol_instance:
                logger.error("Protocol instance not loaded")
                return False

            logger.info("Running full protocol workflow...")

            # Start execution
            if not self.start_execution():
                return False

            # Execute protocol
            if not self.execute_protocol():
                return False

            # Analyze results
            analysis_results = self.analyze_results()
            if not analysis_results:
                logger.warning("Analysis returned no results")

            # Validate results
            validation_success = self.validate_results()

            # Complete execution
            self.complete_execution()

            logger.info(f"Full protocol workflow completed. Validation: {'PASS' if validation_success else 'FAIL'}")

            return validation_success

        except Exception as e:
            logger.error(f"Full protocol run failed: {e}")
            self.current_execution['status'] = 'failed'
            return False

    def pause_execution(self) -> bool:
        """Pause protocol execution"""
        try:
            if not self.current_execution:
                return False

            if self.protocol_instance:
                self.protocol_instance.pause()

            self.current_execution['status'] = 'paused'
            self.current_execution['updated_at'] = datetime.utcnow()

            logger.info(f"Execution paused: {self.current_execution['execution_number']}")

            # In production: update database
            if self.db_session:
                self._persist_execution(self.current_execution)

            return True

        except Exception as e:
            logger.error(f"Failed to pause execution: {e}")
            return False

    def resume_execution(self) -> bool:
        """Resume paused execution"""
        try:
            if not self.current_execution:
                return False

            if self.protocol_instance:
                self.protocol_instance.resume()

            self.current_execution['status'] = 'running'
            self.current_execution['updated_at'] = datetime.utcnow()

            logger.info(f"Execution resumed: {self.current_execution['execution_number']}")

            # In production: update database
            if self.db_session:
                self._persist_execution(self.current_execution)

            return True

        except Exception as e:
            logger.error(f"Failed to resume execution: {e}")
            return False

    def cancel_execution(self, reason: str) -> bool:
        """Cancel protocol execution"""
        try:
            if not self.current_execution:
                return False

            if self.protocol_instance:
                self.protocol_instance.cancel()

            self.current_execution['status'] = 'cancelled'
            self.current_execution['cancellation_reason'] = reason
            self.current_execution['updated_at'] = datetime.utcnow()

            logger.info(f"Execution cancelled: {self.current_execution['execution_number']}")

            # In production: update database
            if self.db_session:
                self._persist_execution(self.current_execution)

            return True

        except Exception as e:
            logger.error(f"Failed to cancel execution: {e}")
            return False

    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        if not self.current_execution:
            return {}

        status = {
            'execution_number': self.current_execution.get('execution_number'),
            'status': self.current_execution.get('status'),
            'progress_percentage': self.current_execution.get('progress_percentage', 0),
            'current_step': self.current_execution.get('current_step'),
            'actual_start': self.current_execution.get('actual_start'),
            'actual_end': self.current_execution.get('actual_end')
        }

        if self.protocol_instance:
            status['protocol_state'] = self.protocol_instance.get_state()

        return status

    def add_measurement(self, measurement_point: str, data: Dict[str, Any]) -> bool:
        """Add measurement data to execution"""
        try:
            if not self.current_execution:
                return False

            measurement = {
                'measurement_point': measurement_point,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }

            self.current_execution['measurements'].append(measurement)

            logger.info(f"Added measurement: {measurement_point}")

            return True

        except Exception as e:
            logger.error(f"Failed to add measurement: {e}")
            return False

    def _update_progress(self, protocol_id: str, percentage: int, step: str, message: str):
        """Callback for protocol progress updates"""
        if self.current_execution:
            self.current_execution['progress_percentage'] = percentage
            self.current_execution['current_step'] = step
            self.current_execution['updated_at'] = datetime.utcnow()

            logger.debug(f"Progress: {percentage}% - {step} - {message}")

            # In production: update database in real-time
            if self.db_session:
                self._persist_execution(self.current_execution)

    def _generate_execution_number(self) -> str:
        """Generate unique execution number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"EXE-{timestamp}"

    def _load_protocol(self, protocol_id: str):
        """
        Dynamically load protocol class

        Args:
            protocol_id: Protocol identifier (e.g., 'STC-001')

        Returns:
            Protocol instance
        """
        try:
            # Convert protocol ID to module and class name
            # E.g., 'STC-001' -> 'protocols.performance.stc_001'
            protocol_id_lower = protocol_id.lower().replace('-', '_')
            class_name = protocol_id.replace('-', '')

            # Determine category based on protocol ID prefix
            category_map = {
                'STC': 'performance', 'NOCT': 'performance', 'LIC': 'performance',
                'PERF': 'performance', 'IAM': 'performance', 'SPEC': 'performance',
                'TEMP': 'performance', 'ENER': 'performance', 'BIFI': 'performance',
                'TRACK': 'performance', 'CONC': 'performance',
                'LID': 'degradation', 'LETID': 'degradation', 'PID': 'degradation',
                'UVID': 'degradation', 'SPONGE': 'degradation', 'SNAIL': 'degradation',
                'DELAM': 'degradation', 'CORR': 'degradation', 'CHALK': 'degradation',
                'YELLOW': 'degradation', 'CRACK': 'degradation', 'SOLDER': 'degradation',
                'JBOX': 'degradation', 'SEAL': 'degradation',
                'TC': 'environmental', 'DH': 'environmental', 'HF': 'environmental',
                'UV': 'environmental', 'SALT': 'environmental', 'SAND': 'environmental',
                'AMMON': 'environmental', 'SO2': 'environmental', 'H2S': 'environmental',
                'TROP': 'environmental', 'DESERT': 'environmental',
                'ML': 'mechanical', 'HAIL': 'mechanical', 'WIND': 'mechanical',
                'SNOW': 'mechanical', 'VIBR': 'mechanical', 'TWIST': 'mechanical',
                'TERM': 'mechanical',
                'INSU': 'safety', 'WET': 'safety', 'DIEL': 'safety',
                'GROUND': 'safety', 'HOT': 'safety', 'BYPASS': 'safety',
                'FIRE': 'safety'
            }

            prefix = protocol_id.split('-')[0]
            category = category_map.get(prefix, 'performance')

            module_path = f"genspark_app.protocols.{category}.{protocol_id_lower}"
            protocol_module = importlib.import_module(module_path)

            protocol_class = getattr(protocol_module, f"{class_name}Protocol")
            protocol_instance = protocol_class()

            logger.info(f"Loaded protocol: {protocol_id}")
            return protocol_instance

        except Exception as e:
            logger.error(f"Failed to load protocol {protocol_id}: {e}")
            return None

    def _persist_execution(self, execution: Dict[str, Any]):
        """Persist execution to database"""
        # In production: save using SQLAlchemy
        pass

    def _save_analysis_results(self, analysis_results: Dict[str, Any]):
        """Save analysis results to database"""
        # In production: save to analysis_results table
        pass
