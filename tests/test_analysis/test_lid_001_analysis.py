"""Tests for LID-001 analysis module."""

import pytest
from analysis.lid_001_analysis import LID001Analyzer


class TestLID001Analyzer:
    """Test suite for LID-001 analyzer."""

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = LID001Analyzer()

        assert analyzer.protocol_id == "LID-001"
        assert analyzer.qc_checker is not None

    def test_analyze_test_run(self, sample_measurements):
        """Test complete test run analysis."""
        analyzer = LID001Analyzer()

        results = analyzer.analyze_test_run(sample_measurements, baseline_power=300.0)

        assert 'baseline_power' in results
        assert 'max_degradation_percent' in results
        assert 'final_degradation_percent' in results
        assert 'degradation_rate_percent_per_hour' in results
        assert 'is_stabilized' in results
        assert 'qc_results' in results

        # Check values are reasonable
        assert results['baseline_power'] == 300.0
        assert results['max_degradation_percent'] >= 0
        assert results['num_measurements'] == len(sample_measurements)

    def test_analyze_test_run_no_measurements(self):
        """Test analysis with no measurements."""
        analyzer = LID001Analyzer()

        results = analyzer.analyze_test_run([])

        assert 'error' in results

    def test_analyze_test_run_auto_baseline(self, sample_measurements):
        """Test analysis with automatic baseline calculation."""
        analyzer = LID001Analyzer()

        # Don't provide baseline_power
        results = analyzer.analyze_test_run(sample_measurements)

        assert 'baseline_power' in results
        assert results['baseline_power'] > 0

    def test_check_stabilization(self, sample_measurements):
        """Test stabilization checking."""
        analyzer = LID001Analyzer()

        # Create degradation data
        degradation_data = []
        for m in sample_measurements:
            if m.get('pmax'):
                degradation_data.append({
                    'elapsed_hours': m.get('elapsed_hours', 0),
                    'degradation_percent': 100 * (300.0 - m['pmax']) / 300.0,
                    'measurement_type': m.get('measurement_type')
                })

        result = analyzer._check_stabilization(degradation_data)

        assert 'is_stabilized' in result
        assert 'max_recent_change' in result
        assert isinstance(result['is_stabilized'], bool)

    def test_check_stabilization_insufficient_data(self):
        """Test stabilization check with insufficient data."""
        analyzer = LID001Analyzer()

        degradation_data = [
            {'elapsed_hours': 0, 'degradation_percent': 0.0}
        ]

        result = analyzer._check_stabilization(degradation_data)

        assert result['is_stabilized'] is False

    def test_calculate_recovery(self):
        """Test recovery calculation."""
        analyzer = LID001Analyzer()

        degradation_data = [
            {'measurement_type': 'initial', 'pmax': 300.0},
            {'measurement_type': 'during_exposure', 'pmax': 292.0},
            {'measurement_type': 'post_exposure', 'pmax': 296.0},
        ]

        result = analyzer._calculate_recovery(degradation_data)

        assert result['recovery_measured'] is True
        assert 'recovery_percent' in result
        assert result['recovery_percent'] > 0

    def test_calculate_recovery_no_data(self):
        """Test recovery calculation without post-exposure data."""
        analyzer = LID001Analyzer()

        degradation_data = [
            {'measurement_type': 'initial', 'pmax': 300.0},
            {'measurement_type': 'during_exposure', 'pmax': 292.0},
        ]

        result = analyzer._calculate_recovery(degradation_data)

        assert result['recovery_measured'] is False

    def test_perform_qc_checks(self, sample_measurements):
        """Test QC checks."""
        analyzer = LID001Analyzer()

        qc_results = analyzer._perform_qc_checks(
            sample_measurements,
            baseline_power=300.0,
            max_degradation=2.7
        )

        assert isinstance(qc_results, list)
        assert len(qc_results) > 0

        # All results should have required fields
        for qc in qc_results:
            assert 'check_name' in qc
            assert 'passed' in qc
            assert 'severity' in qc

    def test_generate_summary_report(self):
        """Test summary report generation."""
        analyzer = LID001Analyzer()

        analysis_results = {
            'baseline_power': 300.0,
            'max_degradation_percent': 2.7,
            'max_degradation_time_hours': 72.0,
            'final_degradation_percent': 2.6,
            'degradation_rate_percent_per_hour': 0.0375,
            'is_stabilized': True,
            'qc_passed': True,
            'num_measurements': 11,
            'num_outliers': 0,
            'qc_results': []
        }

        sample_info = {
            'sample_id': 'PV-2025-001',
            'manufacturer': 'SolarTech',
            'model': 'ST-300W',
            'technology': 'mono-Si'
        }

        report = analyzer.generate_summary_report(analysis_results, sample_info)

        assert isinstance(report, str)
        assert 'LID-001' in report
        assert 'PV-2025-001' in report
        assert '300.0' in report or '300.00' in report
        assert 'PASS' in report
