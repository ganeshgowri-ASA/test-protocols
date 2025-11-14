"""
Unit Tests for YELLOW-001 Analyzer

Tests for the yellowing analysis module.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from protocols.yellow.analyzer import YellowingAnalyzer


class TestYellowingAnalyzer:
    """Test suite for YellowingAnalyzer class."""

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = YellowingAnalyzer()
        assert analyzer is not None

    def test_analyze_degradation_kinetics(self, mock_time_points):
        """Test degradation kinetics analysis."""
        analyzer = YellowingAnalyzer()

        result = analyzer.analyze_degradation_kinetics(mock_time_points, 'yellow_index')

        assert result is not None
        assert 'model' in result
        assert 'parameters' in result
        assert 'fit_quality' in result

    def test_compare_samples(self):
        """Test sample comparison."""
        analyzer = YellowingAnalyzer()

        samples_data = [
            {
                'sample_id': 'EVA_001',
                'time_points': [
                    {'time_point_hours': 0, 'yellow_index': 0.5},
                    {'time_point_hours': 1000, 'yellow_index': 12.0}
                ]
            },
            {
                'sample_id': 'EVA_002',
                'time_points': [
                    {'time_point_hours': 0, 'yellow_index': 0.6},
                    {'time_point_hours': 1000, 'yellow_index': 14.0}
                ]
            }
        ]

        comparison = analyzer.compare_samples(samples_data, 'yellow_index')

        assert 'statistics' in comparison
        assert 'rankings' in comparison
        assert len(comparison['rankings']) == 2

    def test_calculate_stability_index(self, mock_time_points):
        """Test stability index calculation."""
        analyzer = YellowingAnalyzer()

        stability = analyzer.calculate_stability_index(mock_time_points, 'yellow_index')

        assert stability >= 0
        assert stability <= 100

    def test_generate_color_trajectory(self, mock_time_points):
        """Test color trajectory generation."""
        analyzer = YellowingAnalyzer()

        trajectory = analyzer.generate_color_trajectory(mock_time_points)

        assert 'path_length' in trajectory
        assert 'direction' in trajectory
        assert 'velocity' in trajectory
        assert trajectory['path_length'] > 0
