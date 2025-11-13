"""
Unit tests for CORR-001 Corrosion Testing Protocol
"""

import pytest
import asyncio
from datetime import datetime
from protocols.corr001.python.corrosion import (
    CorrosionTestProtocol,
    CorrosionTestConfig,
    validate_config,
    run_corrosion_test
)


@pytest.fixture
def valid_config():
    """Valid test configuration"""
    return {
        "sample_id": "TEST_MODULE_001",
        "test_severity": "Level 6",
        "salt_concentration": 50.0,
        "chamber_temperature": 35.0,
        "exposure_duration": 1.0,  # 1 hour for testing
        "inspection_interval": 0.5
    }


@pytest.fixture
def test_protocol(valid_config):
    """Create test protocol instance"""
    config = validate_config(valid_config)
    return CorrosionTestProtocol(config)


class TestConfigValidation:
    """Test configuration validation"""

    def test_valid_config(self, valid_config):
        """Test valid configuration is accepted"""
        config = validate_config(valid_config)
        assert config.sample_id == "TEST_MODULE_001"
        assert config.test_severity == "Level 6"
        assert config.salt_concentration == 50.0

    def test_missing_required_field(self):
        """Test missing required field raises error"""
        invalid_config = {
            "sample_id": "TEST_001",
            # Missing other required fields
        }
        with pytest.raises(ValueError, match="Missing required field"):
            validate_config(invalid_config)

    def test_salt_concentration_too_low(self, valid_config):
        """Test salt concentration below minimum"""
        valid_config["salt_concentration"] = 30.0
        with pytest.raises(ValueError, match="Salt concentration"):
            validate_config(valid_config)

    def test_salt_concentration_too_high(self, valid_config):
        """Test salt concentration above maximum"""
        valid_config["salt_concentration"] = 70.0
        with pytest.raises(ValueError, match="Salt concentration"):
            validate_config(valid_config)

    def test_temperature_out_of_range(self, valid_config):
        """Test chamber temperature out of range"""
        valid_config["chamber_temperature"] = 50.0
        with pytest.raises(ValueError, match="Chamber temperature"):
            validate_config(valid_config)


class TestCorrosionProtocol:
    """Test corrosion protocol execution"""

    @pytest.mark.asyncio
    async def test_protocol_initialization(self, test_protocol):
        """Test protocol initializes correctly"""
        assert test_protocol.config.sample_id == "TEST_MODULE_001"
        assert test_protocol.measurements == []
        assert test_protocol.baseline_power is None

    @pytest.mark.asyncio
    async def test_initial_characterization(self, test_protocol):
        """Test initial characterization step"""
        await test_protocol._initial_characterization()
        assert test_protocol.baseline_power is not None
        assert test_protocol.baseline_power > 0

    @pytest.mark.asyncio
    async def test_setup_chamber(self, test_protocol):
        """Test chamber setup step"""
        # Should complete without error
        await test_protocol._setup_chamber()

    @pytest.mark.asyncio
    async def test_record_environmental_data(self, test_protocol):
        """Test environmental data recording"""
        measurement = await test_protocol._record_environmental_data()
        assert measurement.timestamp is not None
        assert isinstance(measurement.temperature, float)
        assert isinstance(measurement.humidity, float)
        assert isinstance(measurement.salt_concentration, float)

    @pytest.mark.asyncio
    async def test_environmental_limits_check(self, test_protocol):
        """Test environmental limits checking"""
        from protocols.corr001.python.corrosion import CorrosionMeasurement

        # Normal measurement
        normal_measurement = CorrosionMeasurement(
            timestamp=datetime.utcnow(),
            temperature=35.0,
            humidity=95.0,
            salt_concentration=50.0
        )
        # Should not raise exception
        await test_protocol._check_environmental_limits(normal_measurement)

    @pytest.mark.asyncio
    async def test_assess_corrosion(self, test_protocol):
        """Test corrosion assessment"""
        rating = await test_protocol._assess_corrosion()
        assert isinstance(rating, float)
        assert 0 <= rating <= 5.0

    @pytest.mark.asyncio
    async def test_measure_iv_curve(self, test_protocol):
        """Test IV curve measurement"""
        power = await test_protocol._measure_iv_curve()
        assert isinstance(power, float)
        assert power > 0

    @pytest.mark.asyncio
    async def test_full_execution(self, valid_config):
        """Test complete protocol execution"""
        # Use very short duration for testing
        valid_config["exposure_duration"] = 0.01  # ~36 seconds
        results = await run_corrosion_test(valid_config)

        assert results["protocol_id"] == "CORR-001"
        assert results["sample_id"] == "TEST_MODULE_001"
        assert "measurements" in results
        assert "qc_status" in results
        assert "iec_61701_compliance" in results

    def test_generate_results(self, test_protocol):
        """Test results generation"""
        test_protocol.baseline_power = 250.0
        test_protocol.current_power = 245.0
        test_protocol.test_start_time = datetime.utcnow()
        test_protocol.test_end_time = datetime.utcnow()

        # Add some measurements
        from protocols.corr001.python.corrosion import CorrosionMeasurement
        test_protocol.measurements = [
            CorrosionMeasurement(
                timestamp=datetime.utcnow(),
                temperature=35.0,
                humidity=95.0,
                salt_concentration=50.0,
                corrosion_rating=1.0
            )
        ]

        results = test_protocol._generate_results()

        assert results["sample_id"] == "TEST_MODULE_001"
        assert "measurements" in results
        assert results["measurements"]["baseline_power"] == 250.0
        assert results["measurements"]["final_power"] == 245.0
        assert "power_degradation_pct" in results["measurements"]

    def test_iec_compliance_check(self, test_protocol):
        """Test IEC 61701 compliance checking"""
        # Test passing case
        compliance = test_protocol._check_iec_compliance(3.0)
        assert compliance["compliant"] is True
        assert compliance["severity_level"] == "Level 6"
        assert compliance["measured_degradation"] == 3.0

        # Test failing case
        compliance = test_protocol._check_iec_compliance(10.0)
        assert compliance["compliant"] is False

    def test_qc_evaluation(self, test_protocol):
        """Test QC evaluation"""
        from protocols.corr001.python.corrosion import CorrosionMeasurement

        # Add measurements with stable temperature
        test_protocol.measurements = [
            CorrosionMeasurement(
                timestamp=datetime.utcnow(),
                temperature=35.0,
                humidity=95.0,
                salt_concentration=50.0
            ),
            CorrosionMeasurement(
                timestamp=datetime.utcnow(),
                temperature=35.5,
                humidity=95.0,
                salt_concentration=50.0
            ),
            CorrosionMeasurement(
                timestamp=datetime.utcnow(),
                temperature=35.2,
                humidity=95.0,
                salt_concentration=50.0
            )
        ]

        qc_status = test_protocol._evaluate_qc()
        assert qc_status == "PASS"


class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_end_to_end_corrosion_test(self):
        """Test complete end-to-end corrosion test"""
        config = {
            "sample_id": "INTEGRATION_TEST_001",
            "test_severity": "Level 6",
            "salt_concentration": 50.0,
            "chamber_temperature": 35.0,
            "exposure_duration": 0.01,  # Very short for testing
            "inspection_interval": 0.005
        }

        results = await run_corrosion_test(config)

        # Verify all expected keys are present
        assert "protocol_id" in results
        assert "sample_id" in results
        assert "test_start" in results
        assert "test_end" in results
        assert "configuration" in results
        assert "measurements" in results
        assert "qc_status" in results
        assert "iec_61701_compliance" in results

        # Verify compliance structure
        compliance = results["iec_61701_compliance"]
        assert "severity_level" in compliance
        assert "degradation_limit" in compliance
        assert "measured_degradation" in compliance
        assert "compliant" in compliance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
