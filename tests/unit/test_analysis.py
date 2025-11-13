"""Unit tests for analysis calculations."""

import pytest
import numpy as np
from src.analysis.calculations import IVCurveAnalyzer, PerformanceAnalyzer, PERF002Analyzer


class TestIVCurveAnalyzer:
    """Tests for IVCurveAnalyzer class."""

    def test_find_mpp(self, sample_iv_curve):
        """Test finding maximum power point."""
        analyzer = IVCurveAnalyzer(
            sample_iv_curve['voltages'],
            sample_iv_curve['currents']
        )

        pmax, vmp, imp = analyzer.find_mpp()

        assert pmax > 0
        assert 0 < vmp < max(sample_iv_curve['voltages'])
        assert 0 < imp < max(sample_iv_curve['currents'])
        assert abs(pmax - (vmp * imp)) < 0.01  # Power should equal V * I

    def test_find_voc(self, sample_iv_curve):
        """Test finding open circuit voltage."""
        analyzer = IVCurveAnalyzer(
            sample_iv_curve['voltages'],
            sample_iv_curve['currents']
        )

        voc = analyzer.find_voc()

        assert voc > 0
        assert voc <= max(sample_iv_curve['voltages']) * 1.1  # Allow small extrapolation

    def test_find_isc(self, sample_iv_curve):
        """Test finding short circuit current."""
        analyzer = IVCurveAnalyzer(
            sample_iv_curve['voltages'],
            sample_iv_curve['currents']
        )

        isc = analyzer.find_isc()

        assert isc > 0
        assert isc <= max(sample_iv_curve['currents']) * 1.1

    def test_calculate_fill_factor(self, sample_iv_curve):
        """Test fill factor calculation."""
        analyzer = IVCurveAnalyzer(
            sample_iv_curve['voltages'],
            sample_iv_curve['currents']
        )

        ff = analyzer.calculate_fill_factor()

        assert 0 < ff <= 1  # Fill factor should be between 0 and 1
        assert ff > 0.65  # Typical PV module FF > 65%

    def test_validate_curve_valid(self, sample_iv_curve):
        """Test curve validation for valid curve."""
        analyzer = IVCurveAnalyzer(
            sample_iv_curve['voltages'],
            sample_iv_curve['currents']
        )

        is_valid, issues = analyzer.validate_curve()

        assert is_valid
        assert len(issues) == 0

    def test_validate_curve_insufficient_points(self):
        """Test curve validation with insufficient data points."""
        voltages = [0, 10, 20]
        currents = [9, 8, 7]

        analyzer = IVCurveAnalyzer(voltages, currents)
        is_valid, issues = analyzer.validate_curve()

        assert not is_valid
        assert any('Insufficient data points' in issue for issue in issues)

    def test_validate_curve_negative_values(self):
        """Test curve validation with negative values."""
        voltages = [0, 10, 20, 30]
        currents = [10, 8, -5, 2]  # Negative current

        analyzer = IVCurveAnalyzer(voltages, currents)
        is_valid, issues = analyzer.validate_curve()

        assert not is_valid
        assert any('Negative' in issue for issue in issues)


class TestPerformanceAnalyzer:
    """Tests for PerformanceAnalyzer class."""

    def test_calculate_efficiency(self):
        """Test efficiency calculation."""
        analyzer = PerformanceAnalyzer(module_area=2.0)

        pmax = 400  # 400W
        irradiance = 1000  # 1000 W/m²

        efficiency = analyzer.calculate_efficiency(pmax, irradiance)

        expected_efficiency = (400 / (1000 * 2.0)) * 100  # 20%
        assert abs(efficiency - expected_efficiency) < 0.01

    def test_normalize_power(self):
        """Test power normalization."""
        analyzer = PerformanceAnalyzer()

        pmax = 200  # 200W at 500 W/m²
        irradiance = 500
        target_irradiance = 1000

        normalized = analyzer.normalize_power(pmax, irradiance, target_irradiance)

        assert abs(normalized - 400) < 0.01  # Should be 400W at 1000 W/m²

    def test_analyze_linearity(self):
        """Test linearity analysis."""
        analyzer = PerformanceAnalyzer()

        # Perfect linear relationship
        irradiances = [100, 200, 400, 600, 800, 1000]
        powers = [40, 80, 160, 240, 320, 400]  # Linear: 0.4 * irradiance

        result = analyzer.analyze_linearity(irradiances, powers)

        assert result['r_squared'] > 0.99  # Should be very close to 1
        assert abs(result['slope'] - 0.4) < 0.01

    def test_calculate_uniformity(self):
        """Test uniformity calculation."""
        analyzer = PerformanceAnalyzer()

        # Perfect uniformity
        measurements = [1000] * 25
        result = analyzer.calculate_uniformity(measurements)

        assert result['mean'] == 1000
        assert result['std_dev'] == 0
        assert result['uniformity_percent'] == 100

        # Non-uniform measurements
        measurements = [1000, 1010, 990, 1005, 995]
        result = analyzer.calculate_uniformity(measurements)

        assert result['mean'] == 1000
        assert result['std_dev'] > 0
        assert result['uniformity_percent'] < 100


class TestPERF002Analyzer:
    """Tests for PERF002Analyzer class."""

    def test_analyze_test_run(self, sample_measurements):
        """Test complete test run analysis."""
        analyzer = PERF002Analyzer(module_area=2.0)

        result = analyzer.analyze_test_run(sample_measurements)

        assert 'per_irradiance' in result
        assert 'overall' in result

        # Should have results for each irradiance level
        per_irradiance = result['per_irradiance']
        assert len(per_irradiance) == 7  # 7 irradiance levels

        # Check first result has expected fields
        first_result = per_irradiance[0]
        assert 'irradiance_level' in first_result
        assert 'measurement_count' in first_result

    def test_group_by_irradiance(self, sample_measurements):
        """Test grouping measurements by irradiance."""
        analyzer = PERF002Analyzer()

        grouped = analyzer._group_by_irradiance(sample_measurements)

        assert len(grouped) == 7  # 7 irradiance levels
        assert 100 in grouped
        assert 1100 in grouped

        # Each group should have 5 measurements
        for level, measurements in grouped.items():
            assert len(measurements) == 5

    def test_analyze_irradiance_level(self, sample_measurements):
        """Test analyzing single irradiance level."""
        analyzer = PERF002Analyzer()

        # Get measurements for 1000 W/m²
        measurements_1000 = [m for m in sample_measurements
                            if m['target_irradiance'] == 1000]

        result = analyzer._analyze_irradiance_level(1000, measurements_1000)

        assert result['irradiance_level'] == 1000
        assert result['measurement_count'] == 5
        assert 'irradiance_mean' in result
        assert 'temperature_mean' in result

    def test_analyze_overall(self):
        """Test overall analysis."""
        analyzer = PERF002Analyzer()

        per_irradiance_results = [
            {'irradiance_level': 100, 'irradiance_mean': 100, 'pmax': 40, 'efficiency': 20.0},
            {'irradiance_level': 500, 'irradiance_mean': 500, 'pmax': 200, 'efficiency': 20.0},
            {'irradiance_level': 1000, 'irradiance_mean': 1000, 'pmax': 400, 'efficiency': 20.0},
        ]

        result = analyzer._analyze_overall(per_irradiance_results)

        assert 'r_squared' in result
        assert 'linearity_coefficient' in result
        assert 'completeness_percent' in result
