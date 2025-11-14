"""Unit tests for protocol analyzer."""

import pytest
import numpy as np
from datetime import datetime

from src.core.analyzer import ProtocolAnalyzer


@pytest.fixture
def analyzer():
    """Create analyzer instance."""
    qc_criteria = {
        'data_completeness': 95,
        'validation_rules': [
            {
                'rule_id': 'R001',
                'parameter': 'test_metric',
                'condition': 'percentile_95',
                'threshold': 50.0,
                'unit': 'degrees',
                'description': 'Test rule'
            }
        ]
    }

    analysis_methods = {
        'statistical_analysis': {
            'methods': ['mean', 'median', 'std_dev', 'percentile_95'],
            'parameters': ['test_metric']
        },
        'performance_indices': []
    }

    return ProtocolAnalyzer(qc_criteria, analysis_methods)


def test_analyzer_initialization(analyzer):
    """Test analyzer initialization."""
    assert analyzer.qc_criteria is not None
    assert analyzer.analysis_methods is not None


def test_statistical_analysis(analyzer, sample_measurements):
    """Test statistical analysis."""
    results = analyzer._statistical_analysis(
        pd.DataFrame(sample_measurements)
    )

    assert len(results) > 0

    # Check that we have mean result
    mean_results = [r for r in results if r['calculation_method'] == 'mean']
    assert len(mean_results) > 0

    # Verify result structure
    result = mean_results[0]
    assert 'result_type' in result
    assert result['result_type'] == 'statistical'
    assert 'calculated_value' in result


def test_qc_checks(analyzer, sample_measurements):
    """Test QC checks."""
    import pandas as pd

    results = analyzer._qc_checks(pd.DataFrame(sample_measurements))

    assert len(results) > 0

    # Check for completeness result
    completeness_results = [r for r in results if r['metric_name'] == 'data_completeness']
    assert len(completeness_results) > 0


def test_data_completeness(analyzer, sample_measurements):
    """Test data completeness calculation."""
    import pandas as pd

    df = pd.DataFrame(sample_measurements)
    completeness = analyzer._check_data_completeness(df)

    assert 0 <= completeness <= 100
    assert completeness == 100.0  # All test data has 'good' quality flag


def test_validation_rule_percentile(analyzer):
    """Test validation rule with percentile condition."""
    import pandas as pd

    measurements = []
    base_time = datetime.now()

    # Create measurements with known distribution
    for i in range(100):
        measurements.append({
            'run_id': 'TEST',
            'timestamp': base_time,
            'metric_name': 'test_metric',
            'metric_value': float(i),  # Values 0-99
            'quality_flag': 'good'
        })

    df = pd.DataFrame(measurements)

    rule = {
        'rule_id': 'R001',
        'parameter': 'test_metric',
        'condition': 'percentile_95',
        'threshold': 95.0,
        'unit': 'degrees',
        'description': 'Test rule'
    }

    result = analyzer._apply_validation_rule(df, rule)

    assert result is not None
    assert result['calculated_value'] is not None
    assert result['pass_fail'] in ['pass', 'fail']


def test_analyze_empty_measurements(analyzer):
    """Test analysis with empty measurement list."""
    results = analyzer.analyze([])

    assert isinstance(results, list)
    # Should return empty list or handle gracefully


def test_analyze_complete(analyzer, sample_measurements):
    """Test complete analysis pipeline."""
    results = analyzer.analyze(sample_measurements)

    assert isinstance(results, list)
    assert len(results) > 0

    # Check result types
    result_types = {r['result_type'] for r in results}
    assert 'statistical' in result_types or 'qc' in result_types


# Import pandas for tests
import pandas as pd
