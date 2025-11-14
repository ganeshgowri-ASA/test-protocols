"""WET-001: Wet Leakage Current Test Protocol Implementation (IEC 61730 MST 02)."""

import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Template

from protocols.base import BaseProtocol, MeasurementPoint, TestResult
from protocols.wet_leakage_current.analysis import WETAnalyzer
from utils.config import get_config
from utils.logging import get_logger
from utils.validators import validate_parameters

logger = get_logger(__name__)


class WETLeakageCurrentProtocol(BaseProtocol):
    """WET-001: Wet Leakage Current Test per IEC 61730 MST 02.

    This protocol tests PV modules for wet leakage current to ensure
    electrical safety under humid conditions.
    """

    def __init__(self):
        """Initialize WET-001 protocol."""
        schema_path = os.path.join(
            Path(__file__).parent, 'schema.json'
        )

        super().__init__(
            protocol_id="WET-001",
            name="Wet Leakage Current Test",
            standard="IEC 61730 MST 02",
            version="1.0.0",
            schema_path=schema_path
        )

        # Load default acceptance criteria from config
        self.default_acceptance_criteria = {
            'max_leakage_current': get_config('wet_leakage_current.max_leakage_current', 0.25),
            'min_insulation_resistance': get_config('wet_leakage_current.min_insulation_resistance', 400),
            'max_voltage_variation': get_config('wet_leakage_current.environmental.max_voltage_variation', 5.0),
            'no_surface_tracking': True,
            'no_visible_damage': True,
        }

        self.analyzer: Optional[WETAnalyzer] = None

        logger.info("WET-001 protocol initialized")

    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate test parameters against protocol requirements.

        Args:
            params: Test parameters dictionary

        Returns:
            True if valid

        Raises:
            ValueError: If parameters are invalid
        """
        # Required top-level sections
        required_sections = [
            'sample_information',
            'test_conditions',
            'environmental_conditions'
        ]

        for section in required_sections:
            if section not in params:
                raise ValueError(f"Missing required section: {section}")

        # Validate sample information
        sample_info = params['sample_information']
        if 'sample_id' not in sample_info or not sample_info['sample_id']:
            raise ValueError("sample_id is required")
        if 'module_type' not in sample_info or not sample_info['module_type']:
            raise ValueError("module_type is required")

        # Validate test conditions
        test_cond = params['test_conditions']
        required_test_fields = ['test_voltage', 'electrode_configuration', 'test_duration']
        for field in required_test_fields:
            if field not in test_cond:
                raise ValueError(f"Missing required test condition: {field}")

        # Validate ranges
        if test_cond['test_voltage'] <= 0 or test_cond['test_voltage'] > 5000:
            raise ValueError("test_voltage must be between 0 and 5000 V")

        if test_cond['electrode_configuration'] not in ['A', 'B']:
            raise ValueError("electrode_configuration must be 'A' or 'B'")

        if test_cond['test_duration'] <= 0:
            raise ValueError("test_duration must be positive")

        # Validate environmental conditions
        env_cond = params['environmental_conditions']
        if 'temperature' not in env_cond or 'relative_humidity' not in env_cond:
            raise ValueError("temperature and relative_humidity are required")

        temp = env_cond['temperature']
        if temp < 15 or temp > 35:
            logger.warning(f"Temperature {temp}°C is outside recommended range (15-35°C)")

        humidity = env_cond['relative_humidity']
        if humidity < 45 or humidity > 100:
            logger.warning(f"Humidity {humidity}% is outside recommended range (45-100%)")

        logger.info("Parameters validated successfully")
        return True

    def run_test(
        self,
        params: Dict[str, Any],
        sample_id: str,
        operator: Optional[str] = None
    ) -> TestResult:
        """Execute the wet leakage current test.

        Args:
            params: Test parameters
            sample_id: Sample identifier
            operator: Operator name

        Returns:
            TestResult object

        Raises:
            ValueError: If parameters invalid
            RuntimeError: If test execution fails
        """
        # Validate parameters
        self.validate_parameters(params)

        # Store parameters
        self.parameters = params
        self.start_time = datetime.now()

        # Get acceptance criteria (use custom or defaults)
        acceptance_criteria = params.get('acceptance_criteria', self.default_acceptance_criteria)

        # Initialize analyzer
        self.analyzer = WETAnalyzer(acceptance_criteria)

        logger.info(f"Starting WET-001 test for sample {sample_id}")
        logger.info(f"Test voltage: {params['test_conditions']['test_voltage']} V")
        logger.info(f"Duration: {params['test_conditions']['test_duration']} hours")

        # NOTE: In a real implementation, this would interface with test equipment
        # For now, we provide the framework for data collection
        # Measurements should be added using add_measurement() method

        # Placeholder for actual test execution
        # In production, this would:
        # 1. Initialize test equipment
        # 2. Apply test voltage
        # 3. Collect measurements at specified intervals
        # 4. Monitor environmental conditions
        # 5. Stop test after duration or on failure

        logger.info("Test framework ready. Add measurements using add_measurement()")

        return self._create_test_result(sample_id, operator)

    def add_measurement(
        self,
        leakage_current: float,
        voltage: float,
        temperature: float,
        humidity: float,
        insulation_resistance: Optional[float] = None,
        notes: Optional[str] = None
    ) -> None:
        """Add a measurement point to the test.

        Args:
            leakage_current: Measured leakage current in mA
            voltage: Applied voltage in V
            temperature: Ambient temperature in °C
            humidity: Relative humidity in %
            insulation_resistance: Calculated insulation resistance in MΩ
            notes: Optional observation notes
        """
        # Calculate insulation resistance if not provided (R = V / I)
        if insulation_resistance is None and leakage_current > 0:
            # Convert: V / (mA * 1000) = MΩ / 1000 = MΩ
            insulation_resistance = (voltage / (leakage_current * 1000)) / 1000000

        measurement = MeasurementPoint(
            timestamp=datetime.now(),
            values={
                'leakage_current': leakage_current,
                'voltage': voltage,
                'temperature': temperature,
                'humidity': humidity,
                'insulation_resistance': insulation_resistance or 0,
            },
            notes=notes
        )

        super().add_measurement(measurement)
        logger.debug(
            f"Added measurement: {leakage_current:.4f} mA @ {voltage} V, "
            f"R={insulation_resistance:.2f} MΩ" if insulation_resistance else ""
        )

    def analyze_results(self) -> Dict[str, Any]:
        """Analyze measurements and determine pass/fail.

        Returns:
            Analysis results dictionary

        Raises:
            RuntimeError: If analyzer not initialized or no measurements
        """
        if self.analyzer is None:
            raise RuntimeError("Test not started. Call run_test() first.")

        if not self.measurements:
            raise RuntimeError("No measurements available for analysis")

        test_voltage = self.parameters['test_conditions']['test_voltage']
        results = self.analyzer.analyze_measurements(self.measurements, test_voltage)

        # Add trending analysis
        trending = self.analyzer.calculate_trending(self.measurements)
        results['trending'] = trending

        # Detect anomalies
        anomalies = self.analyzer.detect_anomalies(self.measurements)
        results['anomalies'] = [
            {'index': idx, 'reason': reason} for idx, reason in anomalies
        ]

        logger.info(f"Analysis complete: {results['summary']}")
        return results

    def _create_test_result(
        self,
        sample_id: str,
        operator: Optional[str]
    ) -> TestResult:
        """Create TestResult object from current state.

        Args:
            sample_id: Sample identifier
            operator: Operator name

        Returns:
            TestResult object
        """
        self.end_time = datetime.now()

        # Analyze if we have measurements
        if self.measurements and self.analyzer:
            analysis = self.analyze_results()
        else:
            analysis = {
                'passed': False,
                'summary': 'Test not completed - no measurements',
                'failure_reasons': ['No measurements recorded']
            }

        return TestResult(
            protocol_id=self.protocol_id,
            sample_id=sample_id,
            start_time=self.start_time or datetime.now(),
            end_time=self.end_time,
            passed=analysis['passed'],
            summary=analysis['summary'],
            details=analysis,
            acceptance_criteria=self.parameters.get(
                'acceptance_criteria',
                self.default_acceptance_criteria
            ),
            operator=operator
        )

    def generate_report(
        self,
        test_result: TestResult,
        format: str = 'html'
    ) -> str:
        """Generate test report.

        Args:
            test_result: TestResult object
            format: Report format ('html', 'json')

        Returns:
            Report content or file path

        Raises:
            ValueError: If format not supported
        """
        if format == 'json':
            import json
            report_data = {
                'test_result': test_result.to_dict(),
                'measurements': [m.to_dict() for m in self.measurements],
                'parameters': self.parameters,
            }
            return json.dumps(report_data, indent=2)

        elif format == 'html':
            return self._generate_html_report(test_result)

        else:
            raise ValueError(f"Unsupported report format: {format}")

    def _generate_html_report(self, test_result: TestResult) -> str:
        """Generate HTML report.

        Args:
            test_result: TestResult object

        Returns:
            HTML report content
        """
        template_path = os.path.join(Path(__file__).parent, 'report_template.html')

        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template = Template(f.read())
        else:
            # Use basic template if file doesn't exist
            template = Template(self._get_basic_html_template())

        # Prepare data for template
        report_data = {
            'protocol_id': self.protocol_id,
            'protocol_name': self.name,
            'standard': self.standard,
            'version': self.version,
            'test_result': test_result,
            'parameters': self.parameters,
            'measurements': self.measurements,
            'measurement_count': len(self.measurements),
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        html_content = template.render(**report_data)

        # Save to file
        report_id = str(uuid.uuid4())[:8]
        output_dir = get_config('reporting.output_path', 'reports')
        os.makedirs(output_dir, exist_ok=True)

        filename = f"WET-001_{test_result.sample_id}_{report_id}.html"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w') as f:
            f.write(html_content)

        logger.info(f"Generated HTML report: {filepath}")
        return filepath

    def _get_basic_html_template(self) -> str:
        """Get basic HTML template for reports.

        Returns:
            HTML template string
        """
        return """
<!DOCTYPE html>
<html>
<head>
    <title>{{ protocol_id }} Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        .header { background: #ecf0f1; padding: 20px; margin-bottom: 20px; }
        .section { margin: 20px 0; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #3498db; color: white; }
        .pass { color: green; font-weight: bold; }
        .fail { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ protocol_name }} Report</h1>
        <p><strong>Protocol:</strong> {{ protocol_id }} | <strong>Standard:</strong> {{ standard }}</p>
        <p><strong>Sample ID:</strong> {{ test_result.sample_id }}</p>
        <p><strong>Date:</strong> {{ generated_date }}</p>
    </div>

    <div class="section">
        <h2>Test Result</h2>
        <p class="{{ 'pass' if test_result.passed else 'fail' }}">
            {{ 'PASS' if test_result.passed else 'FAIL' }}
        </p>
        <p>{{ test_result.summary }}</p>
    </div>

    <div class="section">
        <h2>Test Parameters</h2>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            {% for key, value in parameters.items() %}
            <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
            {% endfor %}
        </table>
    </div>

    <div class="section">
        <h2>Measurements ({{ measurement_count }} total)</h2>
        <p>Detailed measurements available in data export.</p>
    </div>
</body>
</html>
        """
