"""Unit tests for QC checker."""

import pytest
from analysis.qc_checker import QCChecker


class TestQCChecker:
    """Tests for QCChecker class."""

    @pytest.fixture
    def qc_checker(self, uvid_001_protocol):
        """Fixture providing QC checker instance."""
        return QCChecker(uvid_001_protocol.definition)

    def test_check_measurement_repeatability_pass(self, qc_checker):
        """Test repeatability check with good data."""
        measurements = [250.1, 250.3, 250.2, 250.4, 250.0]
        result = qc_checker.check_measurement_repeatability(measurements, 'pmax')

        assert result['pass'] is True
        assert result['cv'] < 0.02

    def test_check_measurement_repeatability_fail(self, qc_checker):
        """Test repeatability check with poor repeatability."""
        measurements = [250.0, 255.0, 245.0, 260.0, 240.0]
        result = qc_checker.check_measurement_repeatability(measurements, 'pmax')

        assert result['pass'] is False
        assert result['cv'] > 0.02

    def test_check_measurement_repeatability_insufficient_data(self, qc_checker):
        """Test repeatability check with insufficient data."""
        measurements = [250.0]
        result = qc_checker.check_measurement_repeatability(measurements, 'pmax')

        assert result['pass'] is True
        assert result['cv'] is None

    def test_check_temperature_stability_pass(self, qc_checker):
        """Test temperature stability check with stable data."""
        readings = [
            {'temperature': 60.0 + i * 0.1} for i in range(10)
        ]
        result = qc_checker.check_temperature_stability(readings)

        assert result['pass'] is True
        assert result['max_deviation'] <= 2.0

    def test_check_temperature_stability_fail(self, qc_checker):
        """Test temperature stability check with unstable data."""
        readings = [
            {'temperature': 60.0 if i % 2 == 0 else 65.0} for i in range(10)
        ]
        result = qc_checker.check_temperature_stability(readings)

        assert result['pass'] is False
        assert result['max_deviation'] > 2.0

    def test_check_irradiance_stability_pass(self, qc_checker):
        """Test irradiance stability check with stable data."""
        readings = [
            {'irradiance': 1.0 + i * 0.01} for i in range(10)
        ]
        result = qc_checker.check_irradiance_stability(readings)

        assert result['pass'] is True
        assert result['max_deviation'] <= 0.1

    def test_check_irradiance_stability_fail(self, qc_checker):
        """Test irradiance stability check with unstable data."""
        readings = [
            {'irradiance': 1.0 if i % 2 == 0 else 1.3} for i in range(10)
        ]
        result = qc_checker.check_irradiance_stability(readings)

        assert result['pass'] is False
        assert result['max_deviation'] > 0.1

    def test_check_data_completeness_pass(self, qc_checker):
        """Test data completeness check with sufficient data."""
        result = qc_checker.check_data_completeness(
            expected_measurements=100,
            actual_measurements=98
        )

        assert result['pass'] is True
        assert result['completeness'] >= 0.95

    def test_check_data_completeness_fail(self, qc_checker):
        """Test data completeness check with insufficient data."""
        result = qc_checker.check_data_completeness(
            expected_measurements=100,
            actual_measurements=85
        )

        assert result['pass'] is False
        assert result['completeness'] < 0.95

    def test_check_data_completeness_zero_expected(self, qc_checker):
        """Test data completeness with zero expected measurements."""
        result = qc_checker.check_data_completeness(
            expected_measurements=0,
            actual_measurements=0
        )

        assert result['pass'] is True
        assert result['completeness'] == 1.0

    def test_check_outliers_iqr_method(self, qc_checker):
        """Test outlier detection using IQR method."""
        values = [10, 11, 10, 12, 11, 10, 11, 100]  # 100 is an outlier
        result = qc_checker.check_outliers(values, method='iqr')

        assert result['outliers_detected'] is True
        assert len(result['outlier_indices']) > 0
        assert 7 in result['outlier_indices']  # Index of 100

    def test_check_outliers_zscore_method(self, qc_checker):
        """Test outlier detection using z-score method."""
        values = [10, 11, 10, 12, 11, 10, 11, 100]  # 100 is an outlier
        result = qc_checker.check_outliers(values, method='zscore', threshold=3.0)

        assert result['outliers_detected'] is True
        assert len(result['outlier_indices']) > 0

    def test_check_outliers_no_outliers(self, qc_checker):
        """Test outlier detection with no outliers."""
        values = [10, 11, 10, 12, 11, 10, 11, 10]
        result = qc_checker.check_outliers(values, method='iqr')

        assert result['outliers_detected'] is False
        assert len(result['outlier_indices']) == 0

    def test_check_outliers_insufficient_data(self, qc_checker):
        """Test outlier detection with insufficient data."""
        values = [10, 11, 12]
        result = qc_checker.check_outliers(values)

        assert result['outliers_detected'] is False

    def test_run_all_checks(self, qc_checker):
        """Test running all QC checks."""
        test_data = {
            'measurements': {
                'pmax': [250.1, 250.3, 250.2],
                'voc': [38.1, 38.2, 38.15],
                'isc': [8.9, 8.95, 8.92]
            },
            'temperature_readings': [
                {'temperature': 60.0 + i * 0.1} for i in range(10)
            ],
            'irradiance_readings': [
                {'irradiance': 1.0 + i * 0.01} for i in range(10)
            ],
            'expected_measurements': 100,
            'actual_measurements': 98
        }

        results = qc_checker.run_all_checks(test_data)

        assert 'timestamp' in results
        assert 'checks' in results
        assert 'overall_pass' in results
        assert 'warnings' in results
        assert 'failures' in results

        # Should have checks for repeatability
        assert 'pmax_repeatability' in results['checks']
        assert 'voc_repeatability' in results['checks']
        assert 'isc_repeatability' in results['checks']

        # Should have environmental checks
        assert 'temperature_stability' in results['checks']
        assert 'irradiance_stability' in results['checks']

        # Should have data completeness check
        assert 'data_completeness' in results['checks']
