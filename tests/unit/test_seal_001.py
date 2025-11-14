"""Unit tests for SEAL-001 Edge Seal Degradation Protocol."""

import pytest
from protocols.degradation.seal_001 import SEAL001Protocol


class TestSEAL001Initialization:
    """Test SEAL-001 protocol initialization."""

    def test_protocol_initialization(self, seal_001_protocol):
        """Test basic protocol initialization."""
        assert seal_001_protocol.protocol_id == 'SEAL-001'
        assert seal_001_protocol.name == 'Edge Seal Degradation Protocol'
        assert seal_001_protocol.version == '1.0.0'
        assert seal_001_protocol.category == 'degradation'

    def test_steps_loaded(self, seal_001_protocol):
        """Test that all protocol steps are loaded."""
        assert len(seal_001_protocol.steps) == 4
        step_ids = [step.step_id for step in seal_001_protocol.steps]
        assert 'SEAL-001-01' in step_ids
        assert 'SEAL-001-02' in step_ids
        assert 'SEAL-001-03' in step_ids
        assert 'SEAL-001-04' in step_ids

    def test_equipment_validation(self, seal_001_protocol):
        """Test equipment validation."""
        result = seal_001_protocol.validate_equipment()
        assert isinstance(result, bool)

    def test_sample_preparation(self, seal_001_protocol):
        """Test sample preparation."""
        result = seal_001_protocol.prepare_samples()
        assert isinstance(result, bool)


class TestInitialInspection:
    """Test initial visual inspection (SEAL-001-01)."""

    def test_initial_inspection_execution(
        self,
        seal_001_protocol,
        mock_initial_inspection_data
    ):
        """Test executing initial inspection step."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        assert len(seal_001_protocol.results) == 1
        result = seal_001_protocol.results[0]
        assert result.step_id == 'SEAL-001-01'
        assert result.operator == 'test_inspector'
        assert result.status == 'pass'

    def test_initial_inspection_measurements(
        self,
        seal_001_protocol,
        mock_initial_inspection_data
    ):
        """Test initial inspection measurements are captured."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        result = seal_001_protocol.results[0]
        assert result.measurements['edge_seal_width_top_1'] == 12.5
        assert result.measurements['edge_seal_width_top_2'] == 12.3
        assert result.measurements['initial_defects_count'] == 0

    def test_initial_inspection_validation_min_max(self, seal_001_protocol):
        """Test measurement validation with min/max constraints."""
        invalid_data = {
            'edge_seal_width_top_1': -5,  # Invalid: below minimum
            'edge_seal_width_top_2': 12.3,
            'edge_seal_width_bottom_1': 12.4,
            'edge_seal_width_bottom_2': 12.6,
            'edge_seal_width_left_1': 12.2,
            'edge_seal_width_left_2': 12.7,
            'edge_seal_width_right_1': 12.5,
            'edge_seal_width_right_2': 12.4,
            'initial_defects_count': 0,
            'baseline_image_top': 'test.jpg',
            'baseline_image_bottom': 'test.jpg',
            'baseline_image_left': 'test.jpg',
            'baseline_image_right': 'test.jpg'
        }

        with pytest.raises(ValueError, match="below minimum"):
            seal_001_protocol.perform_initial_inspection('test_inspector', invalid_data)

    def test_initial_inspection_required_fields(self, seal_001_protocol):
        """Test that required fields are validated."""
        incomplete_data = {
            'edge_seal_width_top_1': 12.5,
            # Missing other required fields
        }

        with pytest.raises(ValueError, match="Required measurement"):
            seal_001_protocol.perform_initial_inspection('test_inspector', incomplete_data)


class TestHumidityFreezeCycling:
    """Test humidity-freeze cycling (SEAL-001-02)."""

    def test_single_cycle_execution(self, seal_001_protocol, mock_chamber_data):
        """Test executing a single humidity-freeze cycle."""
        seal_001_protocol.execute_humidity_freeze_cycle(
            cycle_number=1,
            chamber_data=mock_chamber_data,
            operator='test_operator'
        )

        assert len(seal_001_protocol.results) == 1
        result = seal_001_protocol.results[0]
        assert result.step_id == 'SEAL-001-02'
        assert result.measurements['cycle_number'] == 1

    def test_multiple_cycles(self, seal_001_protocol, mock_chamber_data):
        """Test executing multiple cycles."""
        for cycle in range(1, 6):
            seal_001_protocol.execute_humidity_freeze_cycle(
                cycle_number=cycle,
                chamber_data=mock_chamber_data,
                operator='test_operator'
            )

        # Should have 5 results, one per cycle
        cycle_results = [
            r for r in seal_001_protocol.results
            if r.step_id == 'SEAL-001-02'
        ]
        assert len(cycle_results) == 5

        # Verify cycle numbers
        cycle_numbers = [r.measurements['cycle_number'] for r in cycle_results]
        assert cycle_numbers == [1, 2, 3, 4, 5]

    def test_chamber_deviation_warning(self, seal_001_protocol):
        """Test that chamber deviations trigger warnings."""
        deviation_data = {
            'temp_damp_heat': 90.0,  # Outside tolerance
            'humidity_damp_heat': 84.5,
            'temp_freeze': -40.1,
            'deviation_flag': True,
            'deviation_notes': 'Temperature exceeded target by 5°C'
        }

        seal_001_protocol.execute_humidity_freeze_cycle(
            cycle_number=1,
            chamber_data=deviation_data,
            operator='test_operator'
        )

        result = seal_001_protocol.results[0]
        # Note: QC status depends on QC criteria implementation
        assert result.measurements['chamber_deviation_flag'] is True

    def test_cycle_data_tracking(self, seal_001_protocol, mock_chamber_data):
        """Test that cycle data is tracked for analysis."""
        seal_001_protocol.execute_humidity_freeze_cycle(
            cycle_number=1,
            chamber_data=mock_chamber_data,
            operator='test_operator'
        )

        assert len(seal_001_protocol.cycle_data) == 1
        cycle_info = seal_001_protocol.cycle_data[0]
        assert cycle_info['cycle'] == 1
        assert cycle_info['status'] in ['pass', 'warning', 'fail']


class TestFinalInspection:
    """Test final post-conditioning inspection (SEAL-001-04)."""

    def test_final_inspection_execution(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test executing final inspection."""
        # Need initial inspection first
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        final_results = [
            r for r in seal_001_protocol.results
            if r.step_id == 'SEAL-001-04'
        ]
        assert len(final_results) == 1

    def test_final_inspection_measurements(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test final inspection captures all measurements."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        result = seal_001_protocol.results[-1]
        assert result.measurements['final_delamination_length_top'] == 0.8
        assert result.measurements['moisture_ingress_detected'] is False
        assert result.measurements['adhesion_loss_percentage'] == 5.0


class TestCalculations:
    """Test protocol calculations."""

    def test_average_seal_width_calculation(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test average initial seal width calculation."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        calculations = seal_001_protocol.calculate_results()

        assert 'average_initial_seal_width' in calculations
        # Average of all 8 measurements
        expected_avg = (12.5 + 12.3 + 12.4 + 12.6 + 12.2 + 12.7 + 12.5 + 12.4) / 8
        assert abs(calculations['average_initial_seal_width'] - expected_avg) < 0.01

    def test_total_delamination_calculation(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test total delamination length calculation."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        calculations = seal_001_protocol.calculate_results()

        assert 'total_delamination_length' in calculations
        expected_total = 0.8 + 0.5 + 0.6 + 0.7  # Sum of all edges
        assert calculations['total_delamination_length'] == expected_total

    def test_degradation_rate_calculation(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test degradation rate percentage calculation."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        calculations = seal_001_protocol.calculate_results()

        assert 'degradation_rate_percentage' in calculations
        # Should be (max_delamination / avg_seal_width) * 100
        # Max delamination is 0.8mm
        avg_width = calculations['average_initial_seal_width']
        expected_rate = (0.8 / avg_width) * 100
        assert abs(calculations['degradation_rate_percentage'] - expected_rate) < 0.01


class TestPassFailEvaluation:
    """Test pass/fail evaluation logic."""

    def test_passing_evaluation(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test that good test results pass evaluation."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        evaluation = seal_001_protocol.evaluate_pass_fail()

        assert evaluation['overall_pass'] is True
        assert all(c['passed'] for c in evaluation['criteria'])

    def test_failing_evaluation_moisture_ingress(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_failed_inspection_data
    ):
        """Test that moisture ingress causes failure."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_failed_inspection_data
        )

        evaluation = seal_001_protocol.evaluate_pass_fail()

        assert evaluation['overall_pass'] is False

        # Check moisture ingress criterion
        moisture_criterion = next(
            (c for c in evaluation['criteria']
             if c['parameter'] == 'moisture_ingress_detected'),
            None
        )
        assert moisture_criterion is not None
        assert moisture_criterion['passed'] is False
        assert moisture_criterion['severity'] == 'critical'

    def test_individual_criteria(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test individual pass/fail criteria."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        evaluation = seal_001_protocol.evaluate_pass_fail()

        # Check all expected criteria are evaluated
        criteria_params = [c['parameter'] for c in evaluation['criteria']]
        assert 'degradation_rate_percentage' in criteria_params
        assert 'max_delamination_length' in criteria_params
        assert 'moisture_ingress_detected' in criteria_params
        assert 'adhesion_loss_percentage' in criteria_params


class TestReportGeneration:
    """Test report generation."""

    def test_generate_report(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_chamber_data,
        mock_final_inspection_data
    ):
        """Test complete report generation."""
        # Execute protocol steps
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        for cycle in range(1, 6):
            seal_001_protocol.execute_humidity_freeze_cycle(
                cycle, mock_chamber_data, 'test_operator'
            )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        # Generate report
        report = seal_001_protocol.generate_report()

        # Verify report structure
        assert 'protocol' in report
        assert 'test_summary' in report
        assert 'measurements' in report
        assert 'calculations' in report
        assert 'evaluation' in report
        assert 'visual_documentation' in report
        assert 'conclusions' in report
        assert 'recommendations' in report

    def test_report_protocol_info(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test report contains correct protocol information."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        report = seal_001_protocol.generate_report()

        assert report['protocol']['id'] == 'SEAL-001'
        assert report['protocol']['name'] == 'Edge Seal Degradation Protocol'
        assert report['protocol']['version'] == '1.0.0'

    def test_report_conclusions(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test report generates appropriate conclusions."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        report = seal_001_protocol.generate_report()

        assert len(report['conclusions']) > 0
        assert isinstance(report['conclusions'], list)
        assert all(isinstance(c, str) for c in report['conclusions'])

    def test_report_recommendations(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_failed_inspection_data
    ):
        """Test report generates recommendations for failed tests."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_failed_inspection_data
        )

        report = seal_001_protocol.generate_report()

        assert len(report['recommendations']) > 0
        # For failed test with moisture ingress
        recommendations_text = ' '.join(report['recommendations'])
        assert 'moisture' in recommendations_text.lower()


class TestProtocolSummary:
    """Test protocol execution summary."""

    def test_get_summary(
        self,
        seal_001_protocol,
        mock_initial_inspection_data,
        mock_final_inspection_data
    ):
        """Test protocol summary generation."""
        seal_001_protocol.perform_initial_inspection(
            'test_inspector',
            mock_initial_inspection_data
        )

        seal_001_protocol.perform_final_inspection(
            'test_inspector',
            mock_final_inspection_data
        )

        summary = seal_001_protocol.get_summary()

        assert summary['protocol']['id'] == 'SEAL-001'
        assert summary['execution']['total_steps'] == 4
        assert summary['execution']['completed_steps'] == 2
        assert 'status' in summary
