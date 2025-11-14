"""Unit tests for DataProcessor."""

import pytest
import pandas as pd
from src.core.data_processor import DataProcessor


class TestDataProcessor:
    """Test cases for DataProcessor class."""

    def test_initialization(self, data_processor):
        """Test DataProcessor initialization."""
        assert data_processor is not None
        assert data_processor.protocol_manager is not None

    def test_process_raw_data(self, data_processor, sample_conc001_data):
        """Test processing raw data into DataFrame."""
        df = data_processor.process_raw_data('conc-001', sample_conc001_data)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) == len(sample_conc001_data['measurements'])

        # Check for calculated columns
        if 'power_w' in df.columns:
            assert df['power_w'].notna().all()

    def test_calculate_statistics(self, data_processor, sample_conc001_data):
        """Test statistical calculations."""
        df = data_processor.process_raw_data('conc-001', sample_conc001_data)
        stats = data_processor.calculate_statistics(df)

        assert isinstance(stats, dict)

        # Check if efficiency stats are present
        if 'efficiency' in stats:
            assert 'mean' in stats['efficiency']
            assert 'std' in stats['efficiency']
            assert 'min' in stats['efficiency']
            assert 'max' in stats['efficiency']

    def test_calculate_temperature_coefficient(self, data_processor):
        """Test temperature coefficient calculation."""
        # Create test data with temperature variation
        test_data = {
            "measurements": [
                {"temperature_c": 25.0, "efficiency": 22.5, "voc": 0.650},
                {"temperature_c": 50.0, "efficiency": 21.0, "voc": 0.625},
                {"temperature_c": 75.0, "efficiency": 19.5, "voc": 0.600}
            ]
        }

        df = data_processor.process_raw_data('conc-001', test_data)
        temp_coeff = data_processor.calculate_temperature_coefficient(df, 'efficiency')

        assert temp_coeff is not None
        assert isinstance(temp_coeff, float)
        # Temperature coefficient should be negative for efficiency
        assert temp_coeff < 0

    def test_calculate_temperature_coefficient_insufficient_data(self, data_processor):
        """Test temperature coefficient with insufficient data."""
        test_data = {
            "measurements": [
                {"temperature_c": 25.0, "efficiency": 22.5}
            ]
        }

        df = data_processor.process_raw_data('conc-001', test_data)
        temp_coeff = data_processor.calculate_temperature_coefficient(df, 'efficiency')

        # Should return None for insufficient data
        assert temp_coeff is None

    def test_calculate_concentration_coefficient(self, data_processor, sample_conc001_data):
        """Test concentration coefficient calculation."""
        df = data_processor.process_raw_data('conc-001', sample_conc001_data)
        conc_coeff = data_processor.calculate_concentration_coefficient(df, 'efficiency')

        assert conc_coeff is not None
        assert isinstance(conc_coeff, float)

    def test_identify_outliers_iqr(self, data_processor):
        """Test outlier detection using IQR method."""
        test_data = {
            "measurements": [
                {"efficiency": 22.0},
                {"efficiency": 22.5},
                {"efficiency": 23.0},
                {"efficiency": 22.8},
                {"efficiency": 50.0},  # Outlier
            ]
        }

        df = data_processor.process_raw_data('conc-001', test_data)
        outliers = data_processor.identify_outliers(df, 'efficiency', method='iqr')

        assert isinstance(outliers, list)
        # Should detect the outlier
        assert len(outliers) > 0

    def test_identify_outliers_zscore(self, data_processor):
        """Test outlier detection using Z-score method."""
        test_data = {
            "measurements": [
                {"efficiency": 22.0},
                {"efficiency": 22.5},
                {"efficiency": 23.0},
                {"efficiency": 22.8},
                {"efficiency": 50.0},  # Outlier
            ]
        }

        df = data_processor.process_raw_data('conc-001', test_data)
        outliers = data_processor.identify_outliers(df, 'efficiency', method='zscore')

        assert isinstance(outliers, list)

    def test_generate_summary_report(self, data_processor, sample_conc001_data):
        """Test summary report generation."""
        report = data_processor.generate_summary_report('conc-001', sample_conc001_data)

        assert isinstance(report, dict)
        assert 'protocol_id' in report
        assert 'test_run_id' in report
        assert 'data_summary' in report
        assert 'statistics' in report
        assert 'analysis' in report
        assert 'quality_indicators' in report

        # Check data summary
        data_summary = report['data_summary']
        assert data_summary['total_measurements'] == len(sample_conc001_data['measurements'])

    def test_export_to_csv(self, data_processor, sample_conc001_data, tmp_path):
        """Test CSV export functionality."""
        df = data_processor.process_raw_data('conc-001', sample_conc001_data)
        csv_file = tmp_path / "test_export.csv"

        data_processor.export_to_csv(df, str(csv_file))

        assert csv_file.exists()

        # Read back and verify
        df_read = pd.read_csv(csv_file)
        assert len(df_read) == len(df)

    def test_process_empty_data(self, data_processor):
        """Test processing empty data."""
        empty_data = {"measurements": []}

        df = data_processor.process_raw_data('conc-001', empty_data)

        assert isinstance(df, pd.DataFrame)
        assert df.empty
