"""
DELAM-001 Validation Module
Validates protocol configurations, test data, and analysis results
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import re
from pathlib import Path


class DELAM001Validator:
    """
    Validator for DELAM-001 protocol data

    Provides comprehensive validation for:
    - Protocol configurations
    - Test setup parameters
    - Measurement data
    - EL image data
    - Analysis results
    """

    # Module ID pattern: alphanumeric with optional hyphens/underscores
    MODULE_ID_PATTERN = re.compile(r'^[A-Z0-9_-]{5,20}$')

    # Valid image formats for EL analysis
    VALID_EL_IMAGE_FORMATS = {'.tiff', '.tif', '.png', '.raw'}
    VALID_VISUAL_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png'}

    def __init__(self, protocol_config: Optional[Dict[str, Any]] = None):
        """
        Initialize validator

        Args:
            protocol_config: Protocol configuration to validate against
        """
        self.protocol_config = protocol_config or {}

    def validate_module_id(self, module_id: str) -> Tuple[bool, List[str]]:
        """
        Validate module ID format

        Args:
            module_id: Module identifier string

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not module_id:
            errors.append("Module ID cannot be empty")
            return False, errors

        if not self.MODULE_ID_PATTERN.match(module_id):
            errors.append(
                "Module ID must be 5-20 characters, uppercase alphanumeric "
                "with optional hyphens/underscores"
            )

        return len(errors) == 0, errors

    def validate_environmental_data(
        self,
        environmental_data: Dict[str, Any],
        expected_conditions: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate environmental test data

        Args:
            environmental_data: Environmental measurements
            expected_conditions: Expected environmental conditions from protocol

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        required_fields = ['temperature', 'humidity']
        for field in required_fields:
            if field not in environmental_data:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, errors

        # Validate temperature
        temp = environmental_data.get('temperature')
        if temp is not None:
            if not isinstance(temp, (int, float)):
                errors.append("Temperature must be a number")
            elif temp < -40 or temp > 150:
                errors.append(f"Temperature {temp}°C is out of valid range (-40 to 150)")

            # Check against expected conditions if provided
            if expected_conditions and 'temperature' in expected_conditions:
                expected_temp = expected_conditions['temperature']['value']
                tolerance = expected_conditions['temperature']['tolerance']

                if abs(temp - expected_temp) > tolerance:
                    errors.append(
                        f"Temperature {temp}°C is outside tolerance "
                        f"({expected_temp} ± {tolerance}°C)"
                    )

        # Validate humidity
        humidity = environmental_data.get('humidity')
        if humidity is not None:
            if not isinstance(humidity, (int, float)):
                errors.append("Humidity must be a number")
            elif humidity < 0 or humidity > 100:
                errors.append(f"Humidity {humidity}% is out of valid range (0-100)")

            # Check against expected conditions if provided
            if expected_conditions and 'humidity' in expected_conditions:
                expected_humidity = expected_conditions['humidity']['value']
                tolerance = expected_conditions['humidity']['tolerance']

                if abs(humidity - expected_humidity) > tolerance:
                    errors.append(
                        f"Humidity {humidity}% is outside tolerance "
                        f"({expected_humidity} ± {tolerance}%)"
                    )

        return len(errors) == 0, errors

    def validate_el_image_metadata(
        self,
        image_metadata: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate EL image metadata

        Args:
            image_metadata: Image metadata dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Required metadata fields
        required_fields = [
            'filename',
            'timestamp',
            'resolution',
            'bit_depth'
        ]

        for field in required_fields:
            if field not in image_metadata:
                errors.append(f"Missing required metadata field: {field}")

        if errors:
            return False, errors

        # Validate filename and format
        filename = image_metadata.get('filename')
        if filename:
            file_path = Path(filename)
            if file_path.suffix.lower() not in self.VALID_EL_IMAGE_FORMATS:
                errors.append(
                    f"Invalid EL image format: {file_path.suffix}. "
                    f"Valid formats: {', '.join(self.VALID_EL_IMAGE_FORMATS)}"
                )

        # Validate resolution
        resolution = image_metadata.get('resolution')
        if resolution:
            if not isinstance(resolution, dict):
                errors.append("Resolution must be a dictionary with 'width' and 'height'")
            else:
                width = resolution.get('width')
                height = resolution.get('height')

                if not width or not height:
                    errors.append("Resolution must include both 'width' and 'height'")
                elif width < 640 or height < 480:
                    errors.append(
                        f"Resolution {width}x{height} is below minimum (640x480)"
                    )

        # Validate bit depth
        bit_depth = image_metadata.get('bit_depth')
        if bit_depth:
            valid_bit_depths = {8, 10, 12, 14, 16}
            if bit_depth not in valid_bit_depths:
                errors.append(
                    f"Invalid bit depth: {bit_depth}. "
                    f"Valid values: {', '.join(map(str, valid_bit_depths))}"
                )

        # Validate timestamp
        timestamp = image_metadata.get('timestamp')
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append(f"Invalid timestamp format: {timestamp}")

        return len(errors) == 0, errors

    def validate_measurement_data(
        self,
        measurement_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate electrical measurement data

        Args:
            measurement_data: Measurement data dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check for at least one measurement type
        measurement_types = ['voltage', 'current', 'power', 'resistance']
        has_measurement = any(mt in measurement_data for mt in measurement_types)

        if not has_measurement:
            errors.append(
                f"Must include at least one measurement type: {', '.join(measurement_types)}"
            )

        # Validate voltage
        if 'voltage' in measurement_data:
            voltage = measurement_data['voltage']
            if not isinstance(voltage, (int, float)):
                errors.append("Voltage must be a number")
            elif voltage < 0:
                errors.append(f"Voltage cannot be negative: {voltage}")
            elif voltage > 1000:
                errors.append(f"Voltage {voltage}V seems unusually high")

        # Validate current
        if 'current' in measurement_data:
            current = measurement_data['current']
            if not isinstance(current, (int, float)):
                errors.append("Current must be a number")
            elif current < 0:
                errors.append(f"Current cannot be negative: {current}")
            elif current > 100:
                errors.append(f"Current {current}A seems unusually high")

        # Validate power
        if 'power' in measurement_data:
            power = measurement_data['power']
            if not isinstance(power, (int, float)):
                errors.append("Power must be a number")
            elif power < 0:
                errors.append(f"Power cannot be negative: {power}")

            # Cross-validate with voltage and current if available
            if 'voltage' in measurement_data and 'current' in measurement_data:
                calculated_power = measurement_data['voltage'] * measurement_data['current']
                # Allow 10% tolerance for measurement differences
                if abs(power - calculated_power) / max(power, 0.001) > 0.1:
                    errors.append(
                        f"Power {power}W doesn't match V×I calculation "
                        f"({calculated_power:.2f}W)"
                    )

        return len(errors) == 0, errors

    def validate_analysis_results(
        self,
        analysis_results: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate EL analysis results

        Args:
            analysis_results: Analysis results dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Required analysis result fields
        required_fields = [
            'delamination_detected',
            'delamination_area_percent',
            'defect_count'
        ]

        for field in required_fields:
            if field not in analysis_results:
                errors.append(f"Missing required analysis result: {field}")

        if errors:
            return False, errors

        # Validate delamination_detected
        if not isinstance(analysis_results['delamination_detected'], bool):
            errors.append("delamination_detected must be a boolean")

        # Validate delamination_area_percent
        area_percent = analysis_results.get('delamination_area_percent')
        if area_percent is not None:
            if not isinstance(area_percent, (int, float)):
                errors.append("delamination_area_percent must be a number")
            elif area_percent < 0 or area_percent > 100:
                errors.append(
                    f"delamination_area_percent {area_percent} is out of range (0-100)"
                )

        # Validate defect_count
        defect_count = analysis_results.get('defect_count')
        if defect_count is not None:
            if not isinstance(defect_count, int):
                errors.append("defect_count must be an integer")
            elif defect_count < 0:
                errors.append("defect_count cannot be negative")

        # Validate severity level if present
        if 'severity_level' in analysis_results:
            valid_levels = {'none', 'minor', 'moderate', 'severe', 'critical'}
            severity = analysis_results['severity_level']
            if severity not in valid_levels:
                errors.append(
                    f"Invalid severity level: {severity}. "
                    f"Valid values: {', '.join(valid_levels)}"
                )

        # Validate defect locations if present
        if 'defect_locations' in analysis_results:
            defects = analysis_results['defect_locations']
            if not isinstance(defects, list):
                errors.append("defect_locations must be a list")
            else:
                for i, defect in enumerate(defects):
                    if not isinstance(defect, dict):
                        errors.append(f"Defect {i} must be a dictionary")
                        continue

                    # Check for required defect fields
                    if 'x' not in defect or 'y' not in defect:
                        errors.append(f"Defect {i} missing x or y coordinates")

                    if 'area' in defect and defect['area'] < 0:
                        errors.append(f"Defect {i} has negative area")

        return len(errors) == 0, errors

    def validate_test_execution(
        self,
        test_execution_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate complete test execution data

        Args:
            test_execution_data: Complete test execution data

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Required top-level fields
        required_fields = [
            'test_id',
            'module_id',
            'start_time',
            'protocol_version'
        ]

        for field in required_fields:
            if field not in test_execution_data:
                errors.append(f"Missing required field: {field}")

        # Validate module_id
        if 'module_id' in test_execution_data:
            is_valid, module_errors = self.validate_module_id(
                test_execution_data['module_id']
            )
            errors.extend(module_errors)

        # Validate timestamps
        if 'start_time' in test_execution_data:
            try:
                start_time = test_execution_data['start_time']
                if isinstance(start_time, str):
                    datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append(f"Invalid start_time format: {start_time}")

        if 'end_time' in test_execution_data:
            try:
                end_time = test_execution_data['end_time']
                if isinstance(end_time, str):
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

                    if 'start_time' in test_execution_data:
                        start_dt = datetime.fromisoformat(
                            test_execution_data['start_time'].replace('Z', '+00:00')
                        )
                        if end_dt < start_dt:
                            errors.append("end_time cannot be before start_time")
            except (ValueError, AttributeError):
                errors.append(f"Invalid end_time format: {end_time}")

        # Validate environmental data if present
        if 'environmental_data' in test_execution_data:
            expected_conditions = None
            if self.protocol_config:
                expected_conditions = self.protocol_config.get(
                    'test_parameters', {}
                ).get('environmental_conditions')

            is_valid, env_errors = self.validate_environmental_data(
                test_execution_data['environmental_data'],
                expected_conditions
            )
            errors.extend(env_errors)

        # Validate measurements if present
        if 'measurements' in test_execution_data:
            measurements = test_execution_data['measurements']
            if isinstance(measurements, list):
                for i, measurement in enumerate(measurements):
                    is_valid, meas_errors = self.validate_measurement_data(measurement)
                    errors.extend([f"Measurement {i}: {err}" for err in meas_errors])
            elif isinstance(measurements, dict):
                is_valid, meas_errors = self.validate_measurement_data(measurements)
                errors.extend(meas_errors)

        # Validate analysis results if present
        if 'analysis_results' in test_execution_data:
            is_valid, analysis_errors = self.validate_analysis_results(
                test_execution_data['analysis_results']
            )
            errors.extend(analysis_errors)

        return len(errors) == 0, errors

    def validate_batch_test_data(
        self,
        batch_data: List[Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate batch test data

        Args:
            batch_data: List of test execution data

        Returns:
            Tuple of (all_valid, error_map)
        """
        error_map = {}
        all_valid = True

        for i, test_data in enumerate(batch_data):
            test_id = test_data.get('test_id', f'Test_{i}')
            is_valid, errors = self.validate_test_execution(test_data)

            if not is_valid:
                all_valid = False
                error_map[test_id] = errors

        return all_valid, error_map
