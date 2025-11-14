"""Unit tests for protocol implementations."""

import pytest

from test_protocols.constants import QCStatus
from test_protocols.protocols.registry import protocol_registry
from test_protocols.protocols.salt_001 import SALT001Protocol


class TestSALT001Protocol:
    """Tests for SALT-001 protocol implementation."""

    @pytest.fixture
    def protocol(self):
        """Create SALT-001 protocol instance."""
        return SALT001Protocol()

    def test_protocol_initialization(self, protocol):
        """Test protocol initialization."""
        assert protocol.metadata.code == "SALT-001"
        assert protocol.metadata.version == "1.0.0"
        assert protocol.metadata.standard == "IEC 61701:2020"
        assert protocol.cycle_log == []
        assert protocol.iv_measurements == []
        assert protocol.visual_inspections == []

    def test_validate_inputs_success(self, protocol, sample_salt_001_data):
        """Test successful input validation."""
        is_valid = protocol.validate_inputs(sample_salt_001_data)
        assert is_valid is True
        assert len(protocol.validation_errors) == 0

    def test_validate_inputs_missing_field(self, protocol):
        """Test validation fails with missing required field."""
        data = {"module_type": "Crystalline Silicon"}

        is_valid = protocol.validate_inputs(data)
        assert is_valid is False
        assert len(protocol.validation_errors) > 0

        # Check for specific errors
        error_fields = [err.field for err in protocol.validation_errors]
        assert "specimen_id" in error_fields
        assert "severity_level" in error_fields

    def test_validate_inputs_invalid_ranges(self, protocol, invalid_salt_001_data):
        """Test validation fails with out-of-range values."""
        for invalid_data in invalid_salt_001_data:
            is_valid = protocol.validate_inputs(invalid_data)
            assert is_valid is False
            assert len(protocol.validation_errors) > 0
            protocol.validation_errors.clear()  # Reset for next test

    def test_execute_success(self, protocol, sample_salt_001_data):
        """Test protocol execution."""
        results = protocol.execute(sample_salt_001_data)

        assert results is not None
        assert results["specimen_id"] == sample_salt_001_data["specimen_id"]
        assert results["severity_level"] == sample_salt_001_data["severity_level"]
        assert results["total_duration_hours"] == 240
        assert results["total_cycles"] == 10
        assert results["status"] == "initialized"

    def test_execute_validation_failure(self, protocol):
        """Test protocol execution fails with invalid inputs."""
        invalid_data = {"specimen_id": "TEST-001"}

        with pytest.raises(ValueError) as excinfo:
            protocol.execute(invalid_data)

        assert "Input validation failed" in str(excinfo.value)

    def test_update_cycle(self, protocol, sample_salt_001_data):
        """Test cycle update with environmental data."""
        # Initialize protocol first
        protocol.execute(sample_salt_001_data)

        # Update cycle
        cycle_data = protocol.update_cycle(
            cycle_number=1,
            phase="spray",
            temperature=35.0,
            humidity=95.0,
            salt_concentration=5.0,
            spray_rate=1.5,
        )

        assert cycle_data["cycle_number"] == 1
        assert cycle_data["phase"] == "spray"
        assert cycle_data["qc_status"] == "PASS"
        assert len(protocol.cycle_log) == 1
        assert len(protocol.environmental_log) == 1

    def test_update_cycle_out_of_range(self, protocol, sample_salt_001_data):
        """Test cycle update with out-of-range environmental data."""
        protocol.execute(sample_salt_001_data)

        # Temperature out of range
        cycle_data = protocol.update_cycle(
            cycle_number=1,
            phase="spray",
            temperature=40.0,  # Too high
            humidity=95.0,
            salt_concentration=5.0,
        )

        assert cycle_data["qc_status"] == "FAIL"
        assert len(cycle_data["qc_messages"]) > 0

    def test_record_iv_measurement(self, protocol, sample_salt_001_data, sample_iv_curve):
        """Test I-V curve measurement recording."""
        protocol.execute(sample_salt_001_data)

        iv_data = protocol.record_iv_measurement(
            elapsed_hours=0.0,
            voltage=sample_iv_curve["voltage"],
            current=sample_iv_curve["current"],
            irradiance=sample_iv_curve["irradiance"],
            temperature=sample_iv_curve["temperature"],
        )

        assert iv_data["elapsed_hours"] == 0.0
        assert iv_data["max_power"] > 0
        assert iv_data["voc"] > 0
        assert iv_data["isc"] > 0
        assert iv_data["fill_factor"] > 0
        assert iv_data["degradation_percent"] == 0.0  # First measurement
        assert len(protocol.iv_measurements) == 1

    def test_record_iv_measurement_degradation(
        self, protocol, sample_salt_001_data, sample_iv_curve
    ):
        """Test I-V measurement degradation calculation."""
        protocol.execute(sample_salt_001_data)

        # Initial measurement
        protocol.record_iv_measurement(
            elapsed_hours=0.0,
            voltage=sample_iv_curve["voltage"],
            current=sample_iv_curve["current"],
        )

        # Degraded measurement (reduced current)
        degraded_current = [i * 0.95 for i in sample_iv_curve["current"]]

        iv_data = protocol.record_iv_measurement(
            elapsed_hours=120.0,
            voltage=sample_iv_curve["voltage"],
            current=degraded_current,
        )

        assert iv_data["degradation_percent"] > 0
        assert iv_data["degradation_percent"] < 10  # Should be around 5%
        assert len(protocol.iv_measurements) == 2

    def test_record_visual_inspection(self, protocol, sample_salt_001_data):
        """Test visual inspection recording."""
        protocol.execute(sample_salt_001_data)

        inspection_data = protocol.record_visual_inspection(
            elapsed_hours=24.0,
            corrosion_rating="1 - Slight corrosion, <1% of area",
            notes="Minor corrosion observed on edges",
            affected_area_percent=0.5,
        )

        assert inspection_data["elapsed_hours"] == 24.0
        assert inspection_data["corrosion_rating"] == "1 - Slight corrosion, <1% of area"
        assert inspection_data["affected_area_percent"] == 0.5
        assert len(protocol.visual_inspections) == 1

    def test_quality_check(self, protocol, sample_salt_001_data):
        """Test quality control checks."""
        protocol.execute(sample_salt_001_data)

        # Add some environmental data
        for i in range(10):
            protocol.update_cycle(
                cycle_number=i + 1,
                phase="spray",
                temperature=35.0 + (i % 2) * 0.1,
                humidity=95.0 + (i % 3) * 0.2,
                salt_concentration=5.0,
            )

        # Perform QC
        qc_status = protocol.quality_check(protocol.results)

        assert qc_status == QCStatus.PASS
        assert len(protocol.qc_results) > 0

        # Check that temperature and humidity checks exist
        check_names = [qc.check_name for qc in protocol.qc_results]
        assert "chamber_temperature" in check_names
        assert "relative_humidity" in check_names

    def test_calculate_metrics(
        self, protocol, sample_salt_001_data, sample_iv_curve
    ):
        """Test metrics calculation."""
        protocol.execute(sample_salt_001_data)

        # Add some data
        protocol.record_iv_measurement(
            elapsed_hours=0.0,
            voltage=sample_iv_curve["voltage"],
            current=sample_iv_curve["current"],
        )

        protocol.record_visual_inspection(
            elapsed_hours=0.0,
            corrosion_rating="0 - No corrosion",
            affected_area_percent=0.0,
        )

        protocol.update_cycle(
            cycle_number=1,
            phase="spray",
            temperature=35.0,
            humidity=95.0,
        )

        # Calculate metrics
        metrics = protocol.calculate_metrics(protocol.results)

        assert "initial_power_w" in metrics
        assert "avg_temperature_c" in metrics
        assert "avg_humidity_percent" in metrics
        assert "final_corrosion_rating" in metrics


class TestProtocolRegistry:
    """Tests for protocol registry."""

    def test_registry_initialization(self):
        """Test registry is initialized with built-in protocols."""
        assert len(protocol_registry) > 0
        assert "SALT-001" in protocol_registry

    def test_get_protocol(self):
        """Test getting protocol from registry."""
        protocol = protocol_registry.get_protocol("SALT-001")
        assert isinstance(protocol, SALT001Protocol)
        assert protocol.metadata.code == "SALT-001"

    def test_get_protocol_not_found(self):
        """Test getting non-existent protocol raises error."""
        with pytest.raises(KeyError):
            protocol_registry.get_protocol("INVALID-001")

    def test_list_protocols(self):
        """Test listing all protocols."""
        protocols = protocol_registry.list_protocols()
        assert isinstance(protocols, list)
        assert "SALT-001" in protocols

    def test_get_protocol_info(self):
        """Test getting protocol metadata."""
        info = protocol_registry.get_protocol_info("SALT-001")

        assert info["code"] == "SALT-001"
        assert info["name"] == "Salt Mist Corrosion Test"
        assert info["version"] == "1.0.0"
        assert info["category"] == "Environmental"
        assert info["standard"] == "IEC 61701:2020"

    def test_search_protocols_by_category(self):
        """Test searching protocols by category."""
        results = protocol_registry.search_protocols(category="Environmental")
        assert "SALT-001" in results

    def test_search_protocols_by_keyword(self):
        """Test searching protocols by keyword."""
        results = protocol_registry.search_protocols(keyword="corrosion")
        assert "SALT-001" in results

        results = protocol_registry.search_protocols(keyword="nonexistent")
        assert len(results) == 0
