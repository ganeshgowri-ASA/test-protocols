"""
Unit tests for SPEC-001 Spectral Response Test
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.protocols import Protocol, SpectralResponseTest


class TestSpectralResponseTest:
    """Test SPEC-001 Spectral Response Test implementation"""

    @pytest.fixture
    def protocol(self):
        """Load SPEC-001 protocol"""
        protocol_path = Path(__file__).parent.parent.parent / "protocols" / "SPEC-001.json"
        return Protocol(str(protocol_path))

    @pytest.fixture
    def test_params(self):
        """Standard test parameters"""
        return {
            "wavelength": {
                "start": 400,
                "end": 1000,
                "step_size": 50
            },
            "temperature": 25,
            "bias_voltage": 0,
            "bias_light_intensity": 0,
            "integration_time": 100,
            "averaging": 3
        }

    @pytest.fixture
    def sample_info(self):
        """Standard sample information"""
        return {
            "sample_id": "TEST-CELL-001",
            "sample_type": "Solar Cell",
            "technology": "c-Si",
            "area": 1.0
        }

    def test_initialization(self, protocol):
        """Test SpectralResponseTest initialization"""
        test = SpectralResponseTest(protocol=protocol)
        assert test.protocol.protocol_id == "SPEC-001"
        assert test.status == "initialized"

    def test_load_reference_calibration_default(self, protocol):
        """Test loading default reference calibration"""
        test = SpectralResponseTest(protocol=protocol)
        ref_cal = test.load_reference_calibration()

        assert ref_cal is not None
        assert "wavelength" in ref_cal.columns
        assert "spectral_response" in ref_cal.columns
        assert len(ref_cal) > 0

    def test_initialize_test(self, protocol, test_params, sample_info):
        """Test test initialization"""
        test = SpectralResponseTest(protocol=protocol)
        test_id = test.initialize(test_params, sample_info)

        assert test_id is not None
        assert "SPEC-001" in test_id
        assert "TEST-CELL-001" in test_id
        assert test.test_params == test_params
        assert test.sample_info == sample_info

    def test_run_measurement(self, protocol, test_params, sample_info):
        """Test running spectral response measurement"""
        test = SpectralResponseTest(protocol=protocol)
        test.initialize(test_params, sample_info)

        results = test.run()

        assert "raw_data" in results
        assert test.raw_data is not None
        assert len(test.raw_data) > 0
        assert "wavelength" in test.raw_data.columns
        assert "photocurrent_sample" in test.raw_data.columns
        assert "photocurrent_reference" in test.raw_data.columns
        assert "temperature" in test.raw_data.columns

    def test_wavelength_range(self, protocol, test_params, sample_info):
        """Test correct wavelength range in measurement"""
        test = SpectralResponseTest(protocol=protocol)
        test.initialize(test_params, sample_info)
        test.run()

        wavelengths = test.raw_data["wavelength"].values
        assert min(wavelengths) == test_params["wavelength"]["start"]
        assert max(wavelengths) == test_params["wavelength"]["end"]

        # Check step size
        steps = np.diff(wavelengths)
        assert np.allclose(steps, test_params["wavelength"]["step_size"])

    def test_analyze_data(self, protocol, test_params, sample_info):
        """Test data analysis"""
        test = SpectralResponseTest(protocol=protocol)
        test.initialize(test_params, sample_info)
        test.run()
        test.load_reference_calibration()

        analysis_results = test.analyze()

        assert "calculated_data" in analysis_results
        assert "integrated_jsc" in analysis_results
        assert "peak_wavelength" in analysis_results
        assert "peak_eqe" in analysis_results

        assert test.calculated_data is not None
        assert "spectral_response" in test.calculated_data.columns
        assert "external_quantum_efficiency" in test.calculated_data.columns

    def test_eqe_values_reasonable(self, protocol, test_params, sample_info):
        """Test that EQE values are in reasonable range"""
        test = SpectralResponseTest(protocol=protocol)
        test.initialize(test_params, sample_info)
        test.run()
        test.load_reference_calibration()
        test.analyze()

        eqe_values = test.calculated_data["external_quantum_efficiency"].values

        # EQE should be between 0 and 100%
        assert np.all(eqe_values >= 0)
        assert np.all(eqe_values <= 100)

        # Peak EQE should be positive
        assert test.results["peak_eqe"] > 0

    def test_integrated_jsc_positive(self, protocol, test_params, sample_info):
        """Test that integrated Jsc is positive"""
        test = SpectralResponseTest(protocol=protocol)
        test.initialize(test_params, sample_info)
        test.run()
        test.load_reference_calibration()
        test.analyze()

        assert test.results["integrated_jsc"] > 0

    def test_qc_checks(self, protocol, test_params, sample_info):
        """Test quality control checks"""
        test = SpectralResponseTest(protocol=protocol)
        test.initialize(test_params, sample_info)
        test.run()
        test.load_reference_calibration()
        test.analyze()

        qc_results = test.run_qc()

        assert qc_results is not None
        assert len(qc_results) > 0

        # Check that all QC checks have required fields
        for check_name, result in qc_results.items():
            assert "passed" in result
            assert "value" in result
            assert "threshold" in result
            assert isinstance(result["passed"], bool)

    def test_qc_specific_checks(self, protocol, test_params, sample_info):
        """Test specific QC checks"""
        test = SpectralResponseTest(protocol=protocol)
        test.initialize(test_params, sample_info)
        test.run()
        test.load_reference_calibration()
        test.analyze()

        qc_results = test.run_qc()

        # Expected QC checks
        expected_checks = [
            "noise_level",
            "reference_stability",
            "temperature_stability",
            "min_eqe",
            "data_completeness"
        ]

        for check in expected_checks:
            assert check in qc_results

    def test_generate_plots(self, protocol, test_params, sample_info):
        """Test plot generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test = SpectralResponseTest(protocol=protocol, output_dir=tmpdir)
            test.initialize(test_params, sample_info)
            test.run()
            test.load_reference_calibration()
            test.analyze()

            plot_paths = test.generate_plots()

            assert "main_plot" in plot_paths
            assert plot_paths["main_plot"].exists()

    def test_export_results(self, protocol, test_params, sample_info):
        """Test results export"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test = SpectralResponseTest(protocol=protocol, output_dir=tmpdir)
            test.initialize(test_params, sample_info)
            test.run()
            test.load_reference_calibration()
            test.analyze()
            test.run_qc()

            exported_files = test.export_results()

            assert "raw_data" in exported_files
            assert "calculated_data" in exported_files
            assert "report" in exported_files

            # Check files exist
            for file_path in exported_files.values():
                assert file_path.exists()

    def test_complete_workflow(self, protocol, test_params, sample_info):
        """Test complete test workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test = SpectralResponseTest(protocol=protocol, output_dir=tmpdir)

            # Initialize
            test_id = test.initialize(test_params, sample_info)
            assert test.status == "initialized"

            # Run
            test.run()
            assert test.raw_data is not None

            # Analyze
            test.load_reference_calibration()
            test.analyze()
            assert test.calculated_data is not None

            # QC
            qc_results = test.run_qc()
            assert len(qc_results) > 0

            # Export
            exported_files = test.export_results()
            assert len(exported_files) > 0

            # Complete
            test.complete()
            assert test.status == "completed"
            assert test.end_time is not None

    def test_invalid_wavelength_range(self, protocol, sample_info):
        """Test with invalid wavelength range"""
        invalid_params = {
            "wavelength": {
                "start": 1000,  # start > end
                "end": 400,
                "step_size": 50
            },
            "temperature": 25,
            "integration_time": 100,
            "averaging": 3
        }

        test = SpectralResponseTest(protocol=protocol)

        # This should still initialize (validation could be added)
        test.initialize(invalid_params, sample_info)
        test.run()

        # Should handle gracefully (may produce empty or reversed data)
        assert test.raw_data is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
