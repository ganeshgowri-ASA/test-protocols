"""Core protocol engine for test execution."""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import dataclass, field

from src.utils.db import DatabaseManager
from src.utils.logging_config import get_logger
from src.core.validator import ProtocolValidator
from src.core.analyzer import ProtocolAnalyzer

logger = get_logger(__name__)


@dataclass
class ProtocolConfig:
    """Protocol configuration."""

    protocol_id: str
    name: str
    version: str
    category: str
    test_parameters: Dict[str, Any]
    qc_criteria: Dict[str, Any]
    analysis_methods: Dict[str, Any]
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProtocolEngine:
    """Base protocol execution engine."""

    def __init__(
        self,
        config: ProtocolConfig,
        db_manager: Optional[DatabaseManager] = None
    ) -> None:
        """Initialize protocol engine.

        Args:
            config: Protocol configuration
            db_manager: Optional database manager instance
        """
        self.config = config
        self.db_manager = db_manager or DatabaseManager()
        self.validator = ProtocolValidator()
        self.analyzer = ProtocolAnalyzer(config.qc_criteria, config.analysis_methods)
        self.run_id: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = "initialized"

    @classmethod
    def from_json(cls, json_file: str, db_manager: Optional[DatabaseManager] = None) -> 'ProtocolEngine':
        """Create protocol engine from JSON file.

        Args:
            json_file: Path to JSON protocol file
            db_manager: Optional database manager instance

        Returns:
            ProtocolEngine instance
        """
        with open(json_file, 'r') as f:
            data = json.load(f)

        config = ProtocolConfig(
            protocol_id=data['protocol_id'],
            name=data['name'],
            version=data['version'],
            category=data['category'],
            test_parameters=data['test_parameters'],
            qc_criteria=data.get('qc_criteria', {}),
            analysis_methods=data.get('analysis_methods', {}),
            description=data.get('description', ''),
            metadata=data.get('metadata', {})
        )

        return cls(config, db_manager)

    def validate_protocol(self) -> bool:
        """Validate protocol configuration.

        Returns:
            True if valid, False otherwise
        """
        protocol_dict = {
            'protocol_id': self.config.protocol_id,
            'name': self.config.name,
            'version': self.config.version,
            'category': self.config.category,
            'test_parameters': self.config.test_parameters,
            'qc_criteria': self.config.qc_criteria,
            'analysis_methods': self.config.analysis_methods,
            'description': self.config.description,
            'metadata': self.config.metadata
        }

        is_valid = self.validator.validate_protocol(protocol_dict)

        if is_valid:
            logger.info(f"Protocol {self.config.protocol_id} validation successful")
        else:
            logger.error(f"Protocol {self.config.protocol_id} validation failed: {self.validator.errors}")

        return is_valid

    def start_test_run(
        self,
        operator: Optional[str] = None,
        sample_id: Optional[str] = None,
        device_id: Optional[str] = None,
        location: Optional[str] = None,
        environmental_conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new test run.

        Args:
            operator: Operator name
            sample_id: Sample identifier
            device_id: Device identifier
            location: Test location
            environmental_conditions: Environmental conditions

        Returns:
            Run ID
        """
        self.run_id = f"{self.config.protocol_id}-{uuid.uuid4().hex[:8]}"
        self.start_time = datetime.now()
        self.status = "running"

        run_data = {
            'run_id': self.run_id,
            'protocol_id': self.config.protocol_id,
            'protocol_version': self.config.version,
            'status': self.status,
            'start_time': self.start_time,
            'operator': operator,
            'sample_id': sample_id,
            'device_id': device_id,
            'location': location,
            'environmental_conditions': environmental_conditions or {}
        }

        self.db_manager.create_test_run(run_data)
        logger.info(f"Started test run {self.run_id}")

        return self.run_id

    def record_measurement(
        self,
        metric_name: str,
        value: float,
        unit: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        quality_flag: str = "good",
        sensor_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Record a measurement.

        Args:
            metric_name: Name of the metric
            value: Measurement value
            unit: Unit of measurement
            timestamp: Timestamp (defaults to now)
            quality_flag: Quality flag (good/questionable/bad)
            sensor_id: Sensor identifier
            metadata: Additional metadata

        Returns:
            Measurement ID
        """
        if not self.run_id:
            raise ValueError("No active test run. Call start_test_run() first.")

        measurement = {
            'run_id': self.run_id,
            'timestamp': timestamp or datetime.now(),
            'metric_name': metric_name,
            'metric_value': value,
            'metric_unit': unit,
            'quality_flag': quality_flag,
            'sensor_id': sensor_id,
            'metadata': metadata or {}
        }

        measurement_id = self.db_manager.insert_measurement(measurement)
        return measurement_id

    def complete_test_run(self) -> None:
        """Complete the current test run."""
        if not self.run_id:
            raise ValueError("No active test run.")

        self.end_time = datetime.now()
        self.status = "completed"

        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0

        with self.db_manager.get_session() as session:
            from sqlalchemy import text
            session.execute(
                text("""
                    UPDATE test_runs
                    SET status = :status, end_time = :end_time, duration_seconds = :duration
                    WHERE run_id = :run_id
                """),
                {
                    'status': self.status,
                    'end_time': self.end_time,
                    'duration': int(duration),
                    'run_id': self.run_id
                }
            )

        logger.info(f"Completed test run {self.run_id} in {duration:.1f} seconds")

    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results.

        Returns:
            Analysis results dictionary
        """
        if not self.run_id:
            raise ValueError("No active test run.")

        # Get all measurements
        measurements = self.db_manager.get_measurements(self.run_id)

        # Perform analysis
        analysis_results = self.analyzer.analyze(measurements)

        # Store results in database
        for result in analysis_results:
            result['run_id'] = self.run_id
            self.db_manager.insert_result(result)

        logger.info(f"Analysis completed for run {self.run_id}")

        return analysis_results

    def get_test_summary(self) -> Dict[str, Any]:
        """Get test run summary.

        Returns:
            Test summary dictionary
        """
        if not self.run_id:
            raise ValueError("No active test run.")

        summary = self.db_manager.get_test_run(self.run_id)
        return summary or {}
