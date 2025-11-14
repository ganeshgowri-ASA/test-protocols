"""Unit tests for test analyzer."""

import pytest
from analysis.analyzer import TestAnalyzer


class TestTestAnalyzer:
    """Tests for TestAnalyzer class."""

    @pytest.fixture
    def analyzer(self, uvid_001_protocol):
        """Fixture providing analyzer instance."""
        return TestAnalyzer(uvid_001_protocol)

    def test_calculate_retention(self, analyzer):
        """Test retention calculation."""
        retention = analyzer.calculate_retention(250.5, 241.2)
        assert pytest.approx(retention, 0.1) == 96.3

    def test_calculate_retention_zero_initial(self, analyzer):
        """Test retention calculation with zero initial value."""
        retention = analyzer.calculate_retention(0, 100)
        assert retention == 0.0

    def test_calculate_degradation_rate(self, analyzer, sample_measurement_series):
        """Test degradation rate calculation."""
        rate = analyzer.calculate_degradation_rate(sample_measurement_series, 'pmax')

        # Should have negative degradation rate (decreasing power)
        assert rate is not None
        assert rate < 0

    def test_calculate_degradation_rate_insufficient_data(self, analyzer):
        """Test degradation rate with insufficient data."""
        measurements = [
            {'timestamp': 0, 'pmax': 250}
        ]
        rate = analyzer.calculate_degradation_rate(measurements, 'pmax')
        assert rate is None

    def test_analyze_measurement_series(self, analyzer):
        """Test measurement series analysis."""
        measurements = [
            {'pmax': 250.5},
            {'pmax': 250.3},
            {'pmax': 250.7},
            {'pmax': 250.4}
        ]

        analysis = analyzer.analyze_measurement_series(measurements, 'pmax')

        assert analysis['count'] == 4
        assert analysis['mean'] is not None
        assert analysis['std'] is not None
        assert analysis['cv'] is not None
        assert pytest.approx(analysis['mean'], 0.1) == 250.475

    def test_analyze_measurement_series_empty(self, analyzer):
        """Test measurement series analysis with empty data."""
        analysis = analyzer.analyze_measurement_series([], 'pmax')

        assert analysis['count'] == 0
        assert analysis['mean'] is None

    def test_evaluate_test_results_pass(
        self,
        analyzer,
        sample_initial_measurements,
        sample_final_measurements_pass
    ):
        """Test full test evaluation with passing results."""
        measurements_by_point = {
            'initial': sample_initial_measurements,
            'final': sample_final_measurements_pass
        }

        results = analyzer.evaluate_test_results(measurements_by_point)

        assert results['success'] is True
        assert results['pass_fail']['overall_pass'] is True
        assert 'summary_stats' in results

        # Check summary stats calculated
        assert 'pmax' in results['summary_stats']
        pmax_stats = results['summary_stats']['pmax']
        assert pmax_stats['initial'] == 250.5
        assert pmax_stats['final'] == 241.2
        assert pmax_stats['retention_pct'] >= 95.0

    def test_evaluate_test_results_fail(
        self,
        analyzer,
        sample_initial_measurements,
        sample_final_measurements_fail
    ):
        """Test full test evaluation with failing results."""
        measurements_by_point = {
            'initial': sample_initial_measurements,
            'final': sample_final_measurements_fail
        }

        results = analyzer.evaluate_test_results(measurements_by_point)

        assert results['success'] is True
        assert results['pass_fail']['overall_pass'] is False

    def test_evaluate_test_results_missing_measurements(self, analyzer):
        """Test evaluation with missing measurement data."""
        measurements_by_point = {
            'initial': {'pmax': 250.5}
            # Missing 'final'
        }

        results = analyzer.evaluate_test_results(measurements_by_point)

        assert results['success'] is False
        assert 'error' in results

    def test_generate_degradation_trends(self, analyzer, sample_measurement_series):
        """Test degradation trend generation."""
        trends = analyzer.generate_degradation_trends(sample_measurement_series)

        assert 'pmax' in trends
        assert 'voc' in trends
        assert 'isc' in trends

        # Check pmax trend
        pmax_trend = trends['pmax']
        assert len(pmax_trend) == len(sample_measurement_series)

        # First point should be 100% retention
        assert pmax_trend[0]['retention_pct'] == 100.0

        # Last point should show degradation
        assert pmax_trend[-1]['retention_pct'] < 100.0
