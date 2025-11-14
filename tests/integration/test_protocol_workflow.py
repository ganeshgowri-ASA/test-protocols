"""Integration tests for complete protocol workflows."""

import pytest
from src.core import ProtocolManager, SchemaValidator, DataProcessor


class TestProtocolWorkflow:
    """Integration tests for complete protocol workflows."""

    def test_complete_conc001_workflow(self, protocol_manager, sample_conc001_data):
        """Test complete CONC-001 workflow from validation to report."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' not in protocols:
            pytest.skip("CONC-001 protocol not available")

        # Step 1: Load protocol
        protocol = protocol_manager.get_protocol('conc-001')
        assert protocol is not None

        # Step 2: Validate data
        validator = SchemaValidator(protocol_manager)
        validation_result = validator.validate_data('conc-001', sample_conc001_data)
        assert validation_result['valid'] is True

        # Step 3: Process data
        processor = DataProcessor(protocol_manager)
        df = processor.process_raw_data('conc-001', sample_conc001_data)
        assert not df.empty

        # Step 4: Calculate statistics
        stats = processor.calculate_statistics(df)
        assert 'efficiency' in stats

        # Step 5: Generate report
        report = processor.generate_summary_report('conc-001', sample_conc001_data)
        assert report['protocol_id'] == 'conc-001'
        assert report['test_run_id'] == sample_conc001_data['test_run_id']

    def test_data_validation_and_qc(self, protocol_manager, sample_conc001_data):
        """Test data validation and QC workflow."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' not in protocols:
            pytest.skip("CONC-001 protocol not available")

        validator = SchemaValidator(protocol_manager)

        # Validate data structure
        validation_result = validator.validate_data('conc-001', sample_conc001_data)
        assert 'valid' in validation_result
        assert 'errors' in validation_result
        assert 'warnings' in validation_result

        # Validate QC criteria
        qc_result = validator.validate_qc_criteria('conc-001', sample_conc001_data)
        assert 'passed' in qc_result
        assert 'overall_status' in qc_result

    def test_equipment_calibration_workflow(self, protocol_manager):
        """Test equipment calibration validation workflow."""
        from datetime import datetime, timedelta

        protocols = protocol_manager.list_protocols()

        if 'conc-001' not in protocols:
            pytest.skip("CONC-001 protocol not available")

        # Valid calibration
        equipment_data_valid = {
            "calibration_date": (datetime.now() - timedelta(days=30)).isoformat()
        }

        result = protocol_manager.validate_equipment_calibration(
            'conc-001',
            equipment_data_valid
        )

        assert result['valid'] is True

        # Expired calibration
        equipment_data_expired = {
            "calibration_date": (datetime.now() - timedelta(days=500)).isoformat()
        }

        result = protocol_manager.validate_equipment_calibration(
            'conc-001',
            equipment_data_expired
        )

        assert result['valid'] is False

    def test_data_processing_and_analysis(self, protocol_manager, sample_conc001_data):
        """Test data processing and analysis workflow."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' not in protocols:
            pytest.skip("CONC-001 protocol not available")

        processor = DataProcessor(protocol_manager)

        # Process data
        df = processor.process_raw_data('conc-001', sample_conc001_data)

        # Calculate temperature coefficient
        temp_coeff = processor.calculate_temperature_coefficient(df, 'efficiency')

        # Calculate concentration coefficient
        conc_coeff = processor.calculate_concentration_coefficient(df, 'efficiency')

        # Identify outliers
        outliers = processor.identify_outliers(df, 'efficiency')

        # All should work without errors
        assert isinstance(outliers, list)

    def test_invalid_data_handling(self, protocol_manager, invalid_conc001_data):
        """Test handling of invalid data throughout workflow."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' not in protocols:
            pytest.skip("CONC-001 protocol not available")

        validator = SchemaValidator(protocol_manager)

        # Should fail validation
        validation_result = validator.validate_data('conc-001', invalid_conc001_data)
        assert validation_result['valid'] is False
        assert len(validation_result['errors']) > 0

    def test_report_generation_workflow(self, protocol_manager, sample_conc001_data, tmp_path):
        """Test complete report generation workflow."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' not in protocols:
            pytest.skip("CONC-001 protocol not available")

        processor = DataProcessor(protocol_manager)

        # Generate summary report
        report = processor.generate_summary_report('conc-001', sample_conc001_data)

        # Verify report structure
        assert 'protocol_id' in report
        assert 'data_summary' in report
        assert 'statistics' in report
        assert 'analysis' in report

        # Export processed data
        df = processor.process_raw_data('conc-001', sample_conc001_data)
        csv_file = tmp_path / "report_data.csv"
        processor.export_to_csv(df, str(csv_file))

        assert csv_file.exists()
