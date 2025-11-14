"""
Unit tests for ML-002 analyzer

Tests data analysis, statistics, and quality control evaluation

Author: ganeshgowri-ASA
Date: 2025-11-14
"""

import pytest
import numpy as np
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer import (
    ML002Analyzer,
    StatisticalSummary,
    RegressionResults
)
from implementation import TestResults, TestSample, CycleData, SensorReading, TestStatus


class TestStatisticalSummary:
    """Test StatisticalSummary dataclass"""

    def test_statistical_summary_creation(self):
        """Test creating statistical summary"""
        summary = StatisticalSummary(
            mean=5.0,
            std_dev=1.0,
            min=3.0,
            max=7.0,
            range=4.0,
            median=5.0,
            q25=4.0,
            q75=6.0,
            iqr=2.0,
            coefficient_of_variation=20.0,
            count=100
        )

        assert summary.mean == 5.0
        assert summary.count == 100

    def test_statistical_summary_to_dict(self):
        """Test converting to dictionary"""
        summary = StatisticalSummary(
            mean=5.0, std_dev=1.0, min=3.0, max=7.0, range=4.0,
            median=5.0, q25=4.0, q75=6.0, iqr=2.0,
            coefficient_of_variation=20.0, count=100
        )

        summary_dict = summary.to_dict()
        assert isinstance(summary_dict, dict)
        assert summary_dict['mean'] == 5.0


class TestML002AnalyzerHelpers:
    """Test ML002Analyzer helper methods"""

    @pytest.fixture
    def mock_test_results(self):
        """Create mock test results"""
        sample = TestSample(
            sample_id="TEST-001",
            module_type="Crystalline Silicon",
            serial_number="SN123"
        )

        test_results = TestResults(
            test_id="TEST-001-20251114",
            sample=sample,
            start_time=datetime.now(),
            total_cycles=10,
            status=TestStatus.COMPLETED
        )

        # Add cycle data
        for i in range(1, 11):
            cycle = CycleData(
                cycle_number=i,
                start_time=float(i),
                end_time=float(i + 1),
                max_load_pa=1000.0,
                min_load_pa=0.0,
                max_deflection_mm=5.0 + np.random.normal(0, 0.1),
                min_deflection_mm=0.1,
                peak_to_peak_deflection_mm=4.9
            )
            test_results.cycle_data.append(cycle)

        return test_results

    @pytest.fixture
    def protocol_data(self):
        """Load protocol data"""
        import json
        protocol_file = Path(__file__).parent.parent / "protocol.json"
        with open(protocol_file) as f:
            return json.load(f)

    @pytest.fixture
    def analyzer(self, mock_test_results, protocol_data):
        """Create analyzer instance"""
        return ML002Analyzer(mock_test_results, protocol_data)

    def test_calculate_statistics(self, analyzer):
        """Test calculating statistics"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        stats = analyzer._calculate_statistics(data)

        assert isinstance(stats, StatisticalSummary)
        assert stats.mean == 5.5
        assert stats.min == 1.0
        assert stats.max == 10.0
        assert stats.count == 10

    def test_calculate_statistics_empty_data(self, analyzer):
        """Test calculating statistics with empty data"""
        stats = analyzer._calculate_statistics([])

        assert stats.mean == 0
        assert stats.count == 0

    def test_linear_regression(self, analyzer):
        """Test linear regression"""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]  # Perfect linear relationship: y = 2x

        regression = analyzer._linear_regression(x, y)

        assert isinstance(regression, RegressionResults)
        assert abs(regression.slope - 2.0) < 0.01
        assert abs(regression.intercept - 0.0) < 0.01
        assert regression.r_squared > 0.99

    def test_linear_regression_noisy_data(self, analyzer):
        """Test linear regression with noisy data"""
        x = np.linspace(0, 1000, 100)
        y = 0.005 * x + np.random.normal(0, 0.1, 100)  # y = 0.005x + noise

        regression = analyzer._linear_regression(x.tolist(), y.tolist())

        assert abs(regression.slope - 0.005) < 0.01
        assert regression.r_squared > 0.8

    def test_detect_outliers_iqr(self, analyzer):
        """Test outlier detection using IQR method"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]  # 100 is an outlier
        outliers = analyzer._detect_outliers(data, method='iqr', threshold=3.0)

        assert len(outliers) == len(data)
        assert outliers[-1] is True  # Last value (100) should be detected as outlier

    def test_detect_outliers_zscore(self, analyzer):
        """Test outlier detection using z-score method"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 50]  # 50 is an outlier
        outliers = analyzer._detect_outliers(data, method='zscore', threshold=3.0)

        assert len(outliers) == len(data)
        assert outliers[-1] is True  # Last value should be detected


class TestML002AnalyzerAnalyses:
    """Test ML002Analyzer analysis methods"""

    @pytest.fixture
    def mock_test_results(self):
        """Create mock test results with sensor data"""
        sample = TestSample(
            sample_id="TEST-ANALYSIS-001",
            module_type="Crystalline Silicon",
            serial_number="SN456"
        )

        test_results = TestResults(
            test_id="TEST-ANALYSIS-001-20251114",
            sample=sample,
            start_time=datetime.now(),
            total_cycles=50,
            status=TestStatus.COMPLETED
        )

        # Add cycle data with sensors
        for i in range(1, 51):
            cycle = CycleData(
                cycle_number=i,
                start_time=float(i * 10),
                end_time=float(i * 10 + 10),
                max_load_pa=1000.0 + np.random.normal(0, 10),
                min_load_pa=0.0,
                max_deflection_mm=5.0 + i * 0.01,  # Slight increasing trend
                min_deflection_mm=0.1,
                peak_to_peak_deflection_mm=4.9 + i * 0.01
            )

            # Add sensor readings
            cycle.sensor_readings.append(
                SensorReading(
                    sensor_id='load_cell_1',
                    timestamp=float(i * 10 + 5),
                    value=1000.0,
                    unit='Pa',
                    cycle_number=i
                )
            )
            cycle.sensor_readings.append(
                SensorReading(
                    sensor_id='displacement_center',
                    timestamp=float(i * 10 + 5),
                    value=5.0 + i * 0.01,
                    unit='mm',
                    cycle_number=i
                )
            )

            test_results.cycle_data.append(cycle)

        return test_results

    @pytest.fixture
    def protocol_data(self):
        """Load protocol data"""
        import json
        protocol_file = Path(__file__).parent.parent / "protocol.json"
        with open(protocol_file) as f:
            return json.load(f)

    @pytest.fixture
    def analyzer(self, mock_test_results, protocol_data):
        """Create analyzer instance"""
        return ML002Analyzer(mock_test_results, protocol_data)

    def test_analyze_deflection_statistics(self, analyzer):
        """Test deflection statistics analysis"""
        results = analyzer.analyze_deflection_statistics()

        assert 'max_deflection_stats' in results
        assert 'min_deflection_stats' in results
        assert 'overall_deflection_range' in results

        max_stats = results['max_deflection_stats']
        assert max_stats.count == 50

    def test_analyze_load_deflection_linearity(self, analyzer):
        """Test load-deflection linearity analysis"""
        results = analyzer.analyze_load_deflection_linearity()

        assert 'regression' in results
        assert 'data_points' in results

        regression = results['regression']
        assert 'r_squared' in regression
        assert 'slope' in regression

    def test_analyze_cyclic_behavior(self, analyzer):
        """Test cyclic behavior analysis"""
        results = analyzer.analyze_cyclic_behavior()

        assert 'peak_to_peak_variation' in results
        assert 'cycle_to_cycle_variation' in results
        assert 'trend_slope' in results
        assert 'fatigue_indicator' in results

    def test_analyze_permanent_deformation(self, analyzer):
        """Test permanent deformation analysis"""
        results = analyzer.analyze_permanent_deformation()

        assert 'permanent_deflection_mm' in results
        assert 'permanent_change_mm' in results
        assert 'within_tolerance' in results

    def test_analyze_load_control_quality(self, analyzer):
        """Test load control quality analysis"""
        results = analyzer.analyze_load_control_quality()

        assert 'target_load_pa' in results
        assert 'actual_load_stats' in results
        assert 'percent_error_stats' in results
        assert 'within_tolerance' in results

    def test_perform_full_analysis(self, analyzer):
        """Test performing full analysis"""
        results = analyzer.perform_full_analysis()

        expected_keys = [
            'deflection_statistics',
            'load_deflection_linearity',
            'cyclic_behavior',
            'permanent_deformation',
            'load_control_quality',
            'acceptance_criteria'
        ]

        for key in expected_keys:
            assert key in results

    def test_evaluate_acceptance_criteria(self, analyzer):
        """Test acceptance criteria evaluation"""
        # First perform analysis to populate results
        analyzer.perform_full_analysis()

        # Then evaluate criteria
        results = analyzer.evaluate_acceptance_criteria()

        assert 'overall_pass' in results
        assert 'total_criteria' in results
        assert 'passed_criteria' in results

        assert isinstance(results['overall_pass'], bool)
        assert results['total_criteria'] > 0

    def test_generate_summary_report(self, analyzer):
        """Test summary report generation"""
        analyzer.perform_full_analysis()

        report = analyzer.generate_summary_report()

        assert isinstance(report, str)
        assert len(report) > 0
        assert 'ML-002' in report
        assert 'TEST-ANALYSIS-001' in report


class TestML002AnalyzerEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def empty_test_results(self):
        """Create empty test results"""
        sample = TestSample(
            sample_id="EMPTY-TEST",
            module_type="Test",
            serial_number="SN000"
        )

        return TestResults(
            test_id="EMPTY-TEST-001",
            sample=sample,
            start_time=datetime.now(),
            total_cycles=0,
            status=TestStatus.COMPLETED
        )

    @pytest.fixture
    def protocol_data(self):
        """Load protocol data"""
        import json
        protocol_file = Path(__file__).parent.parent / "protocol.json"
        with open(protocol_file) as f:
            return json.load(f)

    def test_analyzer_with_no_cycle_data(self, empty_test_results, protocol_data):
        """Test analyzer with no cycle data"""
        analyzer = ML002Analyzer(empty_test_results, protocol_data)

        # Should handle gracefully
        results = analyzer.analyze_deflection_statistics()
        assert results is not None

    def test_analyzer_with_insufficient_data(self, empty_test_results, protocol_data):
        """Test analyzer with insufficient data for linearity"""
        analyzer = ML002Analyzer(empty_test_results, protocol_data)

        results = analyzer.analyze_load_deflection_linearity()
        assert 'error' in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
