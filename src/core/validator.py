"""Protocol validation using JSON schemas."""

from typing import Any, Dict, List, Optional
import json
from pathlib import Path

import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ProtocolValidator:
    """Validates protocol configurations against JSON schemas."""

    def __init__(self, schema_dir: str = "schemas") -> None:
        """Initialize validator.

        Args:
            schema_dir: Directory containing JSON schemas
        """
        self.schema_dir = Path(schema_dir)
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.errors: List[str] = []
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load all JSON schemas from schema directory."""
        schema_files = {
            'protocol': 'protocol-schema.json',
            'tracker': 'tracker-schema.json',
            'track_001': 'track_001_schema.json'
        }

        for name, filename in schema_files.items():
            schema_path = self.schema_dir / filename
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    self.schemas[name] = json.load(f)
                logger.debug(f"Loaded schema: {name}")

    def validate_protocol(
        self,
        protocol_data: Dict[str, Any],
        schema_name: str = 'protocol'
    ) -> bool:
        """Validate protocol data against schema.

        Args:
            protocol_data: Protocol configuration dictionary
            schema_name: Name of schema to use for validation

        Returns:
            True if valid, False otherwise
        """
        self.errors = []

        if schema_name not in self.schemas:
            self.errors.append(f"Schema '{schema_name}' not found")
            return False

        schema = self.schemas[schema_name]

        try:
            validate(instance=protocol_data, schema=schema)
            logger.info(f"Protocol validation successful for {protocol_data.get('protocol_id', 'unknown')}")
            return True
        except ValidationError as e:
            error_msg = f"Validation error: {e.message} at {'.'.join(str(p) for p in e.path)}"
            self.errors.append(error_msg)
            logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Unexpected validation error: {str(e)}"
            self.errors.append(error_msg)
            logger.error(error_msg)
            return False

    def validate_test_data(
        self,
        test_data: Dict[str, Any],
        protocol_config: Dict[str, Any]
    ) -> bool:
        """Validate test data against protocol configuration.

        Args:
            test_data: Test measurement data
            protocol_config: Protocol configuration

        Returns:
            True if valid, False otherwise
        """
        self.errors = []

        # Check required metrics are present
        required_metrics = {
            metric['name']
            for metric in protocol_config.get('test_parameters', {}).get('metrics', [])
        }

        provided_metrics = set(test_data.keys())

        missing_metrics = required_metrics - provided_metrics
        if missing_metrics:
            self.errors.append(f"Missing required metrics: {missing_metrics}")
            return False

        # Validate metric types and units
        metric_configs = {
            metric['name']: metric
            for metric in protocol_config.get('test_parameters', {}).get('metrics', [])
        }

        for metric_name, metric_value in test_data.items():
            if metric_name in metric_configs:
                config = metric_configs[metric_name]

                # Type validation
                expected_type = config.get('type')
                if expected_type == 'angle' and not isinstance(metric_value, (int, float)):
                    self.errors.append(f"Metric '{metric_name}' should be numeric")

        return len(self.errors) == 0

    def get_errors(self) -> List[str]:
        """Get validation errors.

        Returns:
            List of error messages
        """
        return self.errors
