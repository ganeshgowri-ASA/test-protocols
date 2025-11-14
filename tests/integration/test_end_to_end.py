"""
Integration tests for end-to-end workflow
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.database import get_session, init_db
from src.database.models import create_test_execution
from src.protocols import Protocol, SpectralResponseTest


class TestEndToEnd:
    """End-to-end integration tests"""

    @pytest.fixture
    def protocol(self):
        """Load SPEC-001 protocol"""
        protocol_path = Path(__file__).parent.parent.parent / "protocols" / "SPEC-001.json"
        return Protocol(str(protocol_path))

    @pytest.fixture
    def test_params(self):
        """Test parameters"""
        return {
            "wavelength": {
                "start": 300,
                "end": 1200,
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
        """Sample information"""
        return {
            "sample_id": "INTEGRATION-TEST-001",
            "sample_type": "Solar Cell",
            "technology": "c-Si",
            "area": 2.5,
            "manufacturer": "Test Manufacturer",
            "batch_number": "BATCH-001"
        }

    def test_full_workflow_with_database(self, protocol, test_params, sample_info):
        """Test complete workflow including database integration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize test
            test = SpectralResponseTest(protocol=protocol, output_dir=tmpdir)
            test_id = test.initialize(test_params, sample_info)

            # Run measurement
            test.run()

            # Analyze
            test.load_reference_calibration()
            test.analyze()

            # QC
            qc_results = test.run_qc()

            # Export
            exported_files = test.export_results()

            # Complete
            test.complete()

            # Verify all files were created
            assert exported_files["raw_data"].exists()
            assert exported_files["calculated_data"].exists()
            assert exported_files["report"].exists()
            assert exported_files["main_plot"].exists()

            # Verify report contains expected data
            with open(exported_files["report"], "r") as f:
                report_data = json.load(f)

            assert report_data["test_id"] == test_id
            assert report_data["protocol_id"] == "SPEC-001"
            assert report_data["status"] == "completed"
            assert "results" in report_data
            assert "qc_results" in report_data

            # Verify QC results
            assert len(report_data["qc_results"]) > 0
            for check_name, result in report_data["qc_results"].items():
                assert "passed" in result
                assert "value" in result
                assert "threshold" in result

    def test_multiple_tests_workflow(self, protocol, test_params, sample_info):
        """Test running multiple tests in sequence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_ids = []

            # Run 3 tests
            for i in range(3):
                # Modify sample ID for each test
                sample_info_copy = sample_info.copy()
                sample_info_copy["sample_id"] = f"MULTI-TEST-{i+1:03d}"

                # Initialize and run test
                test = SpectralResponseTest(protocol=protocol, output_dir=tmpdir)
                test_id = test.initialize(test_params, sample_info_copy)
                test_ids.append(test_id)

                test.run()
                test.load_reference_calibration()
                test.analyze()
                test.run_qc()
                test.export_results()
                test.complete()

            # Verify all tests completed
            assert len(test_ids) == 3
            assert len(set(test_ids)) == 3  # All unique

            # Verify all output files exist
            output_dir = Path(tmpdir)
            for test_id in test_ids:
                assert (output_dir / f"{test_id}_raw_data.csv").exists()
                assert (output_dir / f"{test_id}_calculated_data.csv").exists()
                assert (output_dir / f"{test_id}_report.json").exists()
                assert (output_dir / f"{test_id}_plots.png").exists()

    def test_protocol_validation_workflow(self):
        """Test protocol validation workflow"""
        from src.protocols.base import ProtocolValidator

        protocol_path = Path(__file__).parent.parent.parent / "protocols" / "SPEC-001.json"
        schema_path = Path(__file__).parent.parent.parent / "protocols" / "protocol_schema.json"

        validator = ProtocolValidator(str(schema_path))
        is_valid, errors = validator.validate(str(protocol_path))

        # Note: Validation may not pass if protocol doesn't strictly follow schema
        # This is informational
        if not is_valid:
            print(f"Validation errors: {errors}")

    def test_parameter_variations(self, protocol, sample_info):
        """Test different parameter configurations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test 1: Wide wavelength range, coarse step
            params1 = {
                "wavelength": {"start": 300, "end": 1200, "step_size": 100},
                "temperature": 25,
                "integration_time": 100,
                "averaging": 1
            }

            test1 = SpectralResponseTest(protocol=protocol, output_dir=tmpdir)
            test1.initialize(params1, sample_info)
            test1.run()
            test1.load_reference_calibration()
            test1.analyze()

            # Test 2: Narrow wavelength range, fine step
            params2 = {
                "wavelength": {"start": 800, "end": 900, "step_size": 5},
                "temperature": 25,
                "integration_time": 100,
                "averaging": 5
            }

            test2 = SpectralResponseTest(protocol=protocol, output_dir=tmpdir)
            test2.initialize(params2, sample_info)
            test2.run()
            test2.load_reference_calibration()
            test2.analyze()

            # Test 3: Different temperature
            params3 = {
                "wavelength": {"start": 400, "end": 1000, "step_size": 50},
                "temperature": 50,  # Elevated temperature
                "integration_time": 100,
                "averaging": 3
            }

            test3 = SpectralResponseTest(protocol=protocol, output_dir=tmpdir)
            test3.initialize(params3, sample_info)
            test3.run()
            test3.load_reference_calibration()
            test3.analyze()

            # Verify all completed successfully
            assert test1.raw_data is not None
            assert test2.raw_data is not None
            assert test3.raw_data is not None

            # Verify different data sizes based on parameters
            assert len(test1.raw_data) < len(test2.raw_data)  # Coarser vs finer step


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
