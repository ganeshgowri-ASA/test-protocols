"""
DELAM-001 Protocol Definition
Defines the structure, metadata, and configuration for delamination testing
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
from pydantic import BaseModel, Field, validator


class TemperatureConfig(BaseModel):
    """Temperature configuration"""
    value: float = Field(..., ge=-40, le=90, description="Temperature value")
    unit: str = Field(..., description="Temperature unit")
    tolerance: float = Field(..., ge=0, le=10, description="Tolerance")

    @validator('unit')
    def validate_unit(cls, v):
        if v not in ['celsius', 'fahrenheit', 'kelvin']:
            raise ValueError(f"Invalid temperature unit: {v}")
        return v


class HumidityConfig(BaseModel):
    """Humidity configuration"""
    value: float = Field(..., ge=0, le=100, description="Humidity value")
    unit: str = Field(default="percent_rh", description="Humidity unit")
    tolerance: float = Field(..., ge=0, le=10, description="Tolerance")


class EnvironmentalConditions(BaseModel):
    """Environmental conditions for the test"""
    temperature: TemperatureConfig
    humidity: HumidityConfig
    pressure: Optional[Dict[str, Any]] = None


class TestDuration(BaseModel):
    """Test duration configuration"""
    value: float = Field(..., gt=0, description="Duration value")
    unit: str = Field(..., description="Duration unit")

    @validator('unit')
    def validate_unit(cls, v):
        if v not in ['hours', 'days', 'cycles']:
            raise ValueError(f"Invalid duration unit: {v}")
        return v


class InspectionInterval(BaseModel):
    """Inspection interval configuration"""
    interval: float = Field(..., ge=0, description="Interval value")
    unit: str = Field(..., description="Interval unit")
    inspection_type: List[str] = Field(..., description="Types of inspection")

    @validator('inspection_type')
    def validate_inspection_types(cls, v):
        valid_types = ['visual', 'el_imaging', 'electrical', 'dimensional']
        for inspection_type in v:
            if inspection_type not in valid_types:
                raise ValueError(f"Invalid inspection type: {inspection_type}")
        return v


class CameraSettings(BaseModel):
    """EL camera settings"""
    resolution: Dict[str, Any]
    exposure_time: Dict[str, Any]
    gain: Optional[float] = None
    bit_depth: Optional[int] = Field(None, ge=8, le=16)


class AnalysisParameters(BaseModel):
    """EL analysis parameters"""
    defect_detection_threshold: float = Field(..., ge=0, le=1)
    minimum_defect_area: Dict[str, Any]
    delamination_severity_levels: Optional[List[Dict[str, Any]]] = None


class ELImagingConfig(BaseModel):
    """EL imaging configuration"""
    camera_settings: CameraSettings
    lighting: Dict[str, Any]
    analysis_parameters: AnalysisParameters


class AcceptanceCriteria(BaseModel):
    """Test acceptance criteria"""
    maximum_delamination_area: Dict[str, Any]
    visual_inspection_criteria: Dict[str, bool]
    electrical_performance: Dict[str, Any]


class DELAM001Protocol:
    """
    DELAM-001 Delamination Test Protocol

    This class defines the protocol structure and provides methods
    for loading, validating, and managing DELAM-001 test configurations.
    """

    PROTOCOL_ID = "DELAM-001"
    PROTOCOL_NAME = "Delamination Test with EL Imaging"
    VERSION = "1.0.0"
    STANDARD = "IEC 61215"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize DELAM-001 protocol

        Args:
            config: Protocol configuration dictionary. If None, loads default template.
        """
        self.config = config or self._load_default_template()
        self._validate_protocol_id()

    def _load_default_template(self) -> Dict[str, Any]:
        """Load default template from JSON file"""
        template_path = Path(__file__).parent / "templates" / "test_plan.json"
        with open(template_path, 'r') as f:
            return json.load(f)

    def _validate_protocol_id(self):
        """Validate that the protocol ID matches"""
        if self.config.get('protocol_id') != self.PROTOCOL_ID:
            raise ValueError(
                f"Protocol ID mismatch. Expected {self.PROTOCOL_ID}, "
                f"got {self.config.get('protocol_id')}"
            )

    @property
    def protocol_id(self) -> str:
        """Get protocol ID"""
        return self.config['protocol_id']

    @property
    def protocol_name(self) -> str:
        """Get protocol name"""
        return self.config['protocol_name']

    @property
    def version(self) -> str:
        """Get protocol version"""
        return self.config['version']

    @property
    def environmental_conditions(self) -> EnvironmentalConditions:
        """Get environmental conditions"""
        return EnvironmentalConditions(
            **self.config['test_parameters']['environmental_conditions']
        )

    @property
    def test_duration(self) -> TestDuration:
        """Get test duration"""
        return TestDuration(**self.config['test_parameters']['test_duration'])

    @property
    def inspection_intervals(self) -> List[InspectionInterval]:
        """Get inspection intervals"""
        return [
            InspectionInterval(**interval)
            for interval in self.config['test_parameters']['inspection_intervals']
        ]

    @property
    def el_imaging_config(self) -> ELImagingConfig:
        """Get EL imaging configuration"""
        return ELImagingConfig(**self.config['test_parameters']['el_imaging'])

    @property
    def acceptance_criteria(self) -> AcceptanceCriteria:
        """Get acceptance criteria"""
        return AcceptanceCriteria(**self.config['acceptance_criteria'])

    def get_required_equipment(self) -> List[Dict[str, Any]]:
        """Get list of required equipment"""
        return self.config.get('required_equipment', [])

    def get_data_collection_requirements(self) -> Dict[str, Any]:
        """Get data collection requirements"""
        return self.config.get('data_collection', {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert protocol to dictionary"""
        return self.config

    def to_json(self, indent: int = 2) -> str:
        """Convert protocol to JSON string"""
        return json.dumps(self.config, indent=indent)

    def save(self, filepath: Path):
        """Save protocol configuration to file"""
        with open(filepath, 'w') as f:
            json.dump(self.config, f, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> 'DELAM001Protocol':
        """Load protocol configuration from file"""
        with open(filepath, 'r') as f:
            config = json.load(f)
        return cls(config)

    def get_test_parameters(self) -> Dict[str, Any]:
        """Get all test parameters"""
        return self.config.get('test_parameters', {})

    def get_metadata(self) -> Dict[str, Any]:
        """Get protocol metadata"""
        return self.config.get('metadata', {})

    def update_parameter(self, parameter_path: str, value: Any):
        """
        Update a specific parameter in the protocol

        Args:
            parameter_path: Dot-separated path to parameter (e.g., 'test_parameters.temperature.value')
            value: New value for the parameter
        """
        keys = parameter_path.split('.')
        config = self.config

        # Navigate to the parent of the target parameter
        for key in keys[:-1]:
            config = config[key]

        # Set the value
        config[keys[-1]] = value

    def validate_test_data(self, test_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate test data against protocol requirements

        Args:
            test_data: Test data to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        required_fields = [
            'module_id',
            'test_start_time',
            'environmental_data',
            'measurements'
        ]

        for field in required_fields:
            if field not in test_data:
                errors.append(f"Missing required field: {field}")

        # Validate environmental data if present
        if 'environmental_data' in test_data:
            env_data = test_data['environmental_data']
            env_config = self.environmental_conditions

            # Check temperature
            if 'temperature' in env_data:
                temp_value = env_data['temperature']
                expected_temp = env_config.temperature.value
                tolerance = env_config.temperature.tolerance

                if abs(temp_value - expected_temp) > tolerance:
                    errors.append(
                        f"Temperature {temp_value} out of range "
                        f"({expected_temp} ± {tolerance})"
                    )

            # Check humidity
            if 'humidity' in env_data:
                humidity_value = env_data['humidity']
                expected_humidity = env_config.humidity.value
                tolerance = env_config.humidity.tolerance

                if abs(humidity_value - expected_humidity) > tolerance:
                    errors.append(
                        f"Humidity {humidity_value} out of range "
                        f"({expected_humidity} ± {tolerance})"
                    )

        return len(errors) == 0, errors

    def check_acceptance_criteria(self, results: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """
        Check if test results meet acceptance criteria

        Args:
            results: Test results to check

        Returns:
            Tuple of (passed, details)
        """
        criteria = self.acceptance_criteria
        details = {
            'passed': True,
            'delamination_check': None,
            'visual_check': None,
            'electrical_check': None,
            'failures': []
        }

        # Check delamination area
        if 'delamination_area_percent' in results:
            max_allowed = criteria.maximum_delamination_area['value']
            actual = results['delamination_area_percent']

            passed = actual <= max_allowed
            details['delamination_check'] = {
                'passed': passed,
                'actual': actual,
                'maximum_allowed': max_allowed
            }

            if not passed:
                details['passed'] = False
                details['failures'].append(
                    f"Delamination area {actual}% exceeds maximum {max_allowed}%"
                )

        # Check electrical performance
        if 'power_degradation_percent' in results:
            max_allowed = criteria.electrical_performance['maximum_power_degradation']['value']
            actual = results['power_degradation_percent']

            passed = actual <= max_allowed
            details['electrical_check'] = {
                'passed': passed,
                'actual': actual,
                'maximum_allowed': max_allowed
            }

            if not passed:
                details['passed'] = False
                details['failures'].append(
                    f"Power degradation {actual}% exceeds maximum {max_allowed}%"
                )

        # Check visual criteria
        if 'visual_inspection' in results:
            visual_results = results['visual_inspection']
            visual_criteria = criteria.visual_inspection_criteria

            visual_passed = True
            visual_failures = []

            for criterion, required in visual_criteria.items():
                if required and not visual_results.get(criterion, True):
                    visual_passed = False
                    visual_failures.append(f"Failed: {criterion}")

            details['visual_check'] = {
                'passed': visual_passed,
                'failures': visual_failures
            }

            if not visual_passed:
                details['passed'] = False
                details['failures'].extend(visual_failures)

        return details['passed'], details


# Register the protocol
from protocols import register_protocol
register_protocol(DELAM001Protocol.PROTOCOL_ID, DELAM001Protocol)
