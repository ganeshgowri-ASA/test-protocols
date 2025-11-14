"""
Base protocol classes for test execution and management
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema
import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class Protocol:
    """
    Base class for loading and managing test protocol definitions
    """

    def __init__(self, protocol_path: str):
        """
        Initialize protocol from JSON file

        Args:
            protocol_path: Path to protocol JSON file
        """
        self.protocol_path = Path(protocol_path)
        self.protocol_data = self._load_protocol()
        self.protocol_id = self.protocol_data.get("protocol_id")
        self.protocol_name = self.protocol_data.get("protocol_name")
        self.version = self.protocol_data.get("version")
        self.standard = self.protocol_data.get("standard")

    def _load_protocol(self) -> Dict[str, Any]:
        """Load protocol from JSON file"""
        try:
            with open(self.protocol_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Protocol file not found: {self.protocol_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in protocol file: {e}")

    def get_parameter(self, param_name: str) -> Optional[Dict[str, Any]]:
        """Get parameter definition"""
        return self.protocol_data.get("test_parameters", {}).get(param_name)

    def get_equipment(self) -> List[Dict[str, Any]]:
        """Get list of required equipment"""
        return self.protocol_data.get("equipment_required", [])

    def get_procedure(self) -> List[Dict[str, Any]]:
        """Get test procedure steps"""
        return self.protocol_data.get("procedure", [])

    def get_qc_criteria(self) -> Dict[str, Any]:
        """Get quality control criteria"""
        return self.protocol_data.get("qc_criteria", {})

    def get_data_outputs(self) -> Dict[str, Any]:
        """Get expected data outputs"""
        return self.protocol_data.get("data_outputs", {})

    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate test parameters against protocol definition

        Args:
            params: Dictionary of parameter values

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        test_params = self.protocol_data.get("test_parameters", {})

        for param_name, param_def in test_params.items():
            if param_def.get("required", False) and param_name not in params:
                errors.append(f"Required parameter missing: {param_name}")
                continue

            if param_name in params:
                value = params[param_name]
                param_type = param_def.get("type")

                # Type validation
                if param_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Parameter {param_name} must be a number")
                elif param_type == "integer" and not isinstance(value, int):
                    errors.append(f"Parameter {param_name} must be an integer")

                # Range validation
                if "min" in param_def and value < param_def["min"]:
                    errors.append(
                        f"Parameter {param_name} ({value}) below minimum ({param_def['min']})"
                    )
                if "max" in param_def and value > param_def["max"]:
                    errors.append(
                        f"Parameter {param_name} ({value}) above maximum ({param_def['max']})"
                    )

        return len(errors) == 0, errors


class ProtocolValidator:
    """
    Validates protocol JSON files against schema
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize validator

        Args:
            schema_path: Path to JSON schema file
        """
        if schema_path is None:
            # Default schema path
            schema_path = Path(__file__).parent.parent.parent / "protocols" / "protocol_schema.json"

        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema"""
        try:
            with open(self.schema_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Schema file not found: {self.schema_path}")
            return {}

    def validate(self, protocol_path: str) -> tuple[bool, List[str]]:
        """
        Validate protocol file against schema

        Args:
            protocol_path: Path to protocol JSON file

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            with open(protocol_path, "r") as f:
                protocol_data = json.load(f)

            jsonschema.validate(instance=protocol_data, schema=self.schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]


class ProtocolExecutor(ABC):
    """
    Abstract base class for protocol execution
    """

    def __init__(self, protocol: Protocol, output_dir: Optional[str] = None):
        """
        Initialize executor

        Args:
            protocol: Protocol instance
            output_dir: Directory for output files
        """
        self.protocol = protocol
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.test_id = None
        self.start_time = None
        self.end_time = None
        self.status = "initialized"
        self.results = {}
        self.qc_results = {}

    def initialize(self, test_params: Dict[str, Any], sample_info: Dict[str, Any]) -> str:
        """
        Initialize test execution

        Args:
            test_params: Test parameters
            sample_info: Sample information

        Returns:
            Test ID
        """
        # Validate parameters
        is_valid, errors = self.protocol.validate_parameters(test_params)
        if not is_valid:
            raise ValueError(f"Invalid parameters: {errors}")

        # Generate test ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sample_id = sample_info.get("sample_id", "UNKNOWN")
        self.test_id = f"{self.protocol.protocol_id}_{sample_id}_{timestamp}"

        self.test_params = test_params
        self.sample_info = sample_info
        self.start_time = datetime.now()
        self.status = "initialized"

        logger.info(f"Initialized test: {self.test_id}")
        return self.test_id

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        Execute the test protocol
        Must be implemented by subclasses

        Returns:
            Dictionary containing test results
        """
        pass

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze test results
        Must be implemented by subclasses

        Returns:
            Dictionary containing analysis results
        """
        pass

    def run_qc(self) -> Dict[str, bool]:
        """
        Run quality control checks

        Returns:
            Dictionary of QC results
        """
        qc_criteria = self.protocol.get_qc_criteria()
        qc_results = {}

        for criterion_name, criterion_def in qc_criteria.items():
            # This is a simplified QC check - override in subclasses for specific logic
            qc_results[criterion_name] = {
                "passed": True,
                "value": None,
                "threshold": criterion_def.get("threshold"),
                "action": criterion_def.get("action_on_fail", "warning"),
            }

        self.qc_results = qc_results
        return qc_results

    def generate_report(self, output_format: str = "json") -> Path:
        """
        Generate test report

        Args:
            output_format: Report format (json, html, pdf)

        Returns:
            Path to generated report
        """
        report_data = {
            "test_id": self.test_id,
            "protocol_id": self.protocol.protocol_id,
            "protocol_name": self.protocol.protocol_name,
            "version": self.protocol.version,
            "standard": self.protocol.standard,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "sample_info": self.sample_info,
            "test_parameters": self.test_params,
            "results": self.results,
            "qc_results": self.qc_results,
        }

        if output_format == "json":
            report_path = self.output_dir / f"{self.test_id}_report.json"
            with open(report_path, "w") as f:
                json.dump(report_data, f, indent=2, default=str)
        else:
            raise NotImplementedError(f"Report format {output_format} not implemented")

        logger.info(f"Generated report: {report_path}")
        return report_path

    def save_data(self, data: pd.DataFrame, filename: Optional[str] = None) -> Path:
        """
        Save test data to file

        Args:
            data: DataFrame containing test data
            filename: Optional filename (default: test_id_data.csv)

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"{self.test_id}_data.csv"

        data_path = self.output_dir / filename
        data.to_csv(data_path, index=False)

        logger.info(f"Saved data: {data_path}")
        return data_path

    def complete(self):
        """Mark test as complete"""
        self.end_time = datetime.now()
        self.status = "completed"
        logger.info(f"Test completed: {self.test_id}")
