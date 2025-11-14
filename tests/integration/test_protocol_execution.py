"""Integration tests for full protocol execution workflow."""

import pytest
from datetime import datetime
from pathlib import Path

from protocols.base import Protocol
from analysis.analyzer import TestAnalyzer
from analysis.qc_checker import QCChecker
from reports.generator import ReportGenerator


class TestProtocolExecutionWorkflow:
    """Integration tests for complete protocol execution workflow."""

    def test_complete_uvid_001_workflow_pass(
        self,
        uvid_001_protocol,
        sample_test_parameters,
        sample_initial_measurements,
        sample_final_measurements_pass,
        sample_test_execution,
        tmp_path
    ):
        """Test complete UVID-001 workflow with passing results."""

        # Step 1: Validate test parameters
        is_valid, errors = uvid_001_protocol.validate_parameters(sample_test_parameters)
        assert is_valid, f"Parameters should be valid: {errors}"

        # Step 2: Collect measurements
        measurements_by_point = {
            'initial': sample_initial_measurements,
            'final': sample_final_measurements_pass
        }

        # Step 3: Analyze results
        analyzer = TestAnalyzer(uvid_001_protocol)
        results = analyzer.evaluate_test_results(measurements_by_point)

        assert results['success'] is True
        assert results['pass_fail']['overall_pass'] is True

        # Step 4: Run QC checks
        qc_checker = QCChecker(uvid_001_protocol.definition)
        qc_data = {
            'measurements': {
                'pmax': [250.1, 250.3, 250.5],
                'voc': [38.1, 38.2, 38.2],
                'isc': [8.94, 8.95, 8.96]
            },
            'temperature_readings': [
                {'temperature': 60.0} for _ in range(10)
            ],
            'irradiance_readings': [
                {'irradiance': 1.0} for _ in range(10)
            ],
            'expected_measurements': 100,
            'actual_measurements': 100
        }

        qc_results = qc_checker.run_all_checks(qc_data)
        assert qc_results['overall_pass'] is True

        # Step 5: Generate report
        report_generator = ReportGenerator(uvid_001_protocol.definition)
        html_report = report_generator.generate_summary_report(
            sample_test_execution,
            results
        )

        assert html_report is not None
        assert 'UVID-001' in html_report
        assert 'PASS' in html_report

        # Step 6: Save report
        report_path = tmp_path / "test_report.html"
        report_generator.save_report(html_report, report_path, format='html')
        assert report_path.exists()

        # Step 7: Export data to JSON
        json_path = tmp_path / "test_data.json"
        report_generator.export_to_json(
            sample_test_execution,
            results,
            [],
            json_path
        )
        assert json_path.exists()

    def test_complete_uvid_001_workflow_fail(
        self,
        uvid_001_protocol,
        sample_test_parameters,
        sample_initial_measurements,
        sample_final_measurements_fail,
        sample_test_execution
    ):
        """Test complete UVID-001 workflow with failing results."""

        # Validate parameters
        is_valid, errors = uvid_001_protocol.validate_parameters(sample_test_parameters)
        assert is_valid

        # Collect measurements
        measurements_by_point = {
            'initial': sample_initial_measurements,
            'final': sample_final_measurements_fail
        }

        # Analyze results
        analyzer = TestAnalyzer(uvid_001_protocol)
        results = analyzer.evaluate_test_results(measurements_by_point)

        assert results['success'] is True
        assert results['pass_fail']['overall_pass'] is False

        # Generate report
        report_generator = ReportGenerator(uvid_001_protocol.definition)
        html_report = report_generator.generate_summary_report(
            sample_test_execution,
            results
        )

        assert 'FAIL' in html_report

    def test_degradation_trend_analysis(
        self,
        uvid_001_protocol,
        sample_measurement_series
    ):
        """Test degradation trend analysis over time."""

        analyzer = TestAnalyzer(uvid_001_protocol)

        # Generate trends
        trends = analyzer.generate_degradation_trends(sample_measurement_series)

        assert 'pmax' in trends
        assert len(trends['pmax']) == len(sample_measurement_series)

        # Verify retention is decreasing over time
        pmax_retentions = [point['retention_pct'] for point in trends['pmax']]
        assert pmax_retentions[0] == 100.0
        assert pmax_retentions[-1] < pmax_retentions[0]

        # Verify trend is generally decreasing
        for i in range(len(pmax_retentions) - 1):
            # Allow for some noise, but overall trend should be down
            assert pmax_retentions[i] - pmax_retentions[i + 1] >= -1.0

    def test_qc_integration_with_analysis(
        self,
        uvid_001_protocol,
        sample_initial_measurements,
        sample_final_measurements_pass,
        sample_temperature_readings,
        sample_irradiance_readings
    ):
        """Test QC checks integrated with analysis."""

        # Run analysis
        analyzer = TestAnalyzer(uvid_001_protocol)
        measurements_by_point = {
            'initial': sample_initial_measurements,
            'final': sample_final_measurements_pass
        }
        results = analyzer.evaluate_test_results(measurements_by_point)

        # Run QC checks
        qc_checker = QCChecker(uvid_001_protocol.definition)

        # Check environmental stability
        temp_result = qc_checker.check_temperature_stability(sample_temperature_readings)
        irr_result = qc_checker.check_irradiance_stability(sample_irradiance_readings)

        # Both should pass with provided sample data
        assert temp_result['pass'] is True
        assert irr_result['pass'] is True

        # Combined result should consider both analysis and QC
        overall_pass = (
            results['pass_fail']['overall_pass'] and
            temp_result['pass'] and
            irr_result['pass']
        )

        assert overall_pass is True

    def test_report_generation_with_all_data(
        self,
        uvid_001_protocol,
        sample_test_execution,
        sample_initial_measurements,
        sample_final_measurements_pass,
        sample_measurement_series
    ):
        """Test report generation with complete dataset."""

        # Analyze results
        analyzer = TestAnalyzer(uvid_001_protocol)
        measurements_by_point = {
            'initial': sample_initial_measurements,
            'final': sample_final_measurements_pass
        }
        results = analyzer.evaluate_test_results(measurements_by_point)

        # Generate detailed report with all measurements
        report_generator = ReportGenerator(uvid_001_protocol.definition)

        # Convert measurement series to proper format
        all_measurements = []
        for idx, meas in enumerate(sample_measurement_series):
            for param, value in meas.items():
                if param != 'timestamp':
                    all_measurements.append({
                        'measurement_point': f'point_{idx}',
                        'timestamp': meas['timestamp'],
                        'parameter': param,
                        'value': value,
                        'unit': 'W' if param == 'pmax' else 'V' if param == 'voc' else 'A'
                    })

        detailed_report = report_generator.generate_detailed_report(
            sample_test_execution,
            results,
            all_measurements
        )

        assert detailed_report is not None
        assert 'Detailed Measurements' in detailed_report
        assert len(all_measurements) > 0

    def test_parameter_validation_workflow(self, uvid_001_protocol):
        """Test parameter validation in workflow context."""

        # Test various parameter scenarios
        test_cases = [
            # (parameters, should_pass)
            ({
                'uv_irradiance': 1.0,
                'chamber_temperature': 60.0,
                'exposure_duration': 1000,
                'relative_humidity': 50.0
            }, True),
            ({
                'uv_irradiance': 2.0,  # Out of range
                'chamber_temperature': 60.0,
                'exposure_duration': 1000
            }, False),
            ({
                'uv_irradiance': 1.0,
                # Missing required parameter
                'exposure_duration': 1000
            }, False),
        ]

        for params, should_pass in test_cases:
            is_valid, errors = uvid_001_protocol.validate_parameters(params)
            assert is_valid == should_pass, f"Parameters {params} validation unexpected: {errors}"
