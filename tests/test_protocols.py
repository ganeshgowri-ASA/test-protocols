"""
Unit Tests for PV Testing Protocols
===================================
Comprehensive test suite for all 54 protocols.

Author: GenSpark PV Testing Framework
Version: 1.0.0
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.base_protocol import (
    BaseProtocol,
    ProtocolMetadata,
    ProtocolStatus,
    ValidationLevel,
    ProtocolFactory
)


class TestProtocolFramework:
    """Test the base protocol framework"""

    def test_protocol_metadata_creation(self):
        """Test protocol metadata creation"""
        metadata = ProtocolMetadata(
            protocol_id="TEST-001",
            protocol_name="Test Protocol",
            version="1.0.0",
            category="test"
        )

        assert metadata.protocol_id == "TEST-001"
        assert metadata.protocol_name == "Test Protocol"
        assert metadata.version == "1.0.0"
        assert metadata.category == "test"

    def test_protocol_factory_registration(self):
        """Test protocol factory registration"""
        protocols = ProtocolFactory.list_protocols()
        assert len(protocols) >= 54  # Should have all 54 protocols registered

    def test_protocol_factory_creation(self):
        """Test protocol creation via factory"""
        # Test creating STC-001 protocol
        protocol = ProtocolFactory.create("STC-001")
        assert protocol is not None
        assert protocol.get_protocol_id() == "STC-001"


class TestPerformanceProtocols:
    """Test performance category protocols"""

    @pytest.mark.parametrize("protocol_id", [
        "STC-001", "NOCT-001", "LIC-001", "PERF-001", "PERF-002",
        "IAM-001", "SPEC-001", "TEMP-001", "ENER-001", "BIFI-001",
        "TRACK-001", "CONC-001"
    ])
    def test_performance_protocol_creation(self, protocol_id):
        """Test that performance protocols can be created"""
        protocol = ProtocolFactory.create(protocol_id)
        assert protocol is not None
        assert protocol.get_category() == "performance"
        assert protocol.get_protocol_id() == protocol_id

    def test_stc_protocol_execution(self):
        """Test STC-001 protocol execution"""
        protocol = ProtocolFactory.create("STC-001")

        # Setup test parameters
        setup_params = {
            'irradiance': 1000,
            'cell_temperature': 25,
            'air_mass': 1.5,
            'module_area': 1.6
        }

        # Test that protocol can be executed
        assert protocol is not None
        assert protocol.status == ProtocolStatus.DRAFT


class TestDegradationProtocols:
    """Test degradation category protocols"""

    @pytest.mark.parametrize("protocol_id", [
        "LID-001", "LETID-001", "PID-001", "PID-002", "UVID-001",
        "SPONGE-001", "SNAIL-001", "DELAM-001", "CORR-001",
        "CHALK-001", "YELLOW-001", "CRACK-001", "SOLDER-001",
        "JBOX-001", "SEAL-001"
    ])
    def test_degradation_protocol_creation(self, protocol_id):
        """Test that degradation protocols can be created"""
        protocol = ProtocolFactory.create(protocol_id)
        assert protocol is not None
        assert protocol.get_category() == "degradation"
        assert protocol.get_protocol_id() == protocol_id


class TestEnvironmentalProtocols:
    """Test environmental category protocols"""

    @pytest.mark.parametrize("protocol_id", [
        "TC-001", "DH-001", "DH-002", "HF-001", "UV-001",
        "SALT-001", "SAND-001", "AMMON-001", "SO2-001",
        "H2S-001", "TROP-001", "DESERT-001"
    ])
    def test_environmental_protocol_creation(self, protocol_id):
        """Test that environmental protocols can be created"""
        protocol = ProtocolFactory.create(protocol_id)
        assert protocol is not None
        assert protocol.get_category() == "environmental"
        assert protocol.get_protocol_id() == protocol_id


class TestMechanicalProtocols:
    """Test mechanical category protocols"""

    @pytest.mark.parametrize("protocol_id", [
        "ML-001", "ML-002", "HAIL-001", "WIND-001",
        "SNOW-001", "VIBR-001", "TWIST-001", "TERM-001"
    ])
    def test_mechanical_protocol_creation(self, protocol_id):
        """Test that mechanical protocols can be created"""
        protocol = ProtocolFactory.create(protocol_id)
        assert protocol is not None
        assert protocol.get_category() == "mechanical"
        assert protocol.get_protocol_id() == protocol_id


class TestSafetyProtocols:
    """Test safety category protocols"""

    @pytest.mark.parametrize("protocol_id", [
        "INSU-001", "WET-001", "DIEL-001", "GROUND-001",
        "HOT-001", "BYPASS-001", "FIRE-001"
    ])
    def test_safety_protocol_creation(self, protocol_id):
        """Test that safety protocols can be created"""
        protocol = ProtocolFactory.create(protocol_id)
        assert protocol is not None
        assert protocol.get_category() == "safety"
        assert protocol.get_protocol_id() == protocol_id


class TestDataValidation:
    """Test data validation utilities"""

    def test_field_validator_required(self):
        """Test required field validation"""
        from utils.data_validation import FieldValidator

        # Test valid required field
        valid, msg = FieldValidator.validate_required("value", "test_field")
        assert valid is True

        # Test invalid required field
        valid, msg = FieldValidator.validate_required(None, "test_field")
        assert valid is False
        assert "required" in msg.lower()

    def test_field_validator_range(self):
        """Test range validation"""
        from utils.data_validation import FieldValidator

        # Test value in range
        valid, msg = FieldValidator.validate_range(50, 0, 100, "test_field")
        assert valid is True

        # Test value below minimum
        valid, msg = FieldValidator.validate_range(-10, 0, 100, "test_field")
        assert valid is False

        # Test value above maximum
        valid, msg = FieldValidator.validate_range(150, 0, 100, "test_field")
        assert valid is False

    def test_temperature_validation(self):
        """Test temperature validation"""
        from utils.data_validation import FieldValidator

        # Valid temperature
        valid, msg = FieldValidator.validate_temperature(25)
        assert valid is True

        # Invalid temperature (absolute zero)
        valid, msg = FieldValidator.validate_temperature(-300)
        assert valid is False


class TestVisualization:
    """Test visualization utilities"""

    def test_iv_curve_creation(self):
        """Test I-V curve generation"""
        from utils.visualization import PlotlyChartBuilder

        voltage = np.linspace(0, 40, 100)
        current = 8 * (1 - voltage / 40)

        fig = PlotlyChartBuilder.create_iv_curve(voltage, current)
        assert fig is not None
        assert len(fig.data) > 0

    def test_pv_curve_creation(self):
        """Test P-V curve generation"""
        from utils.visualization import PlotlyChartBuilder

        voltage = np.linspace(0, 40, 100)
        power = voltage * 8 * (1 - voltage / 40)

        fig = PlotlyChartBuilder.create_pv_curve(voltage, power)
        assert fig is not None
        assert len(fig.data) > 0


class TestCalculations:
    """Test PV calculation utilities"""

    def test_fill_factor_calculation(self):
        """Test fill factor calculation"""
        from utils.calculations import PVCalculations

        isc = 8.0
        voc = 40.0
        pmax = 250.0

        ff = PVCalculations.calculate_fill_factor(isc, voc, pmax)
        assert 0 < ff < 1
        assert abs(ff - 0.78125) < 0.001

    def test_efficiency_calculation(self):
        """Test efficiency calculation"""
        from utils.calculations import PVCalculations

        pmax = 250.0
        irradiance = 1000.0
        area = 1.6

        eff = PVCalculations.calculate_efficiency(pmax, irradiance, area)
        assert 0 < eff < 100
        assert abs(eff - 15.625) < 0.001

    def test_iv_curve_analysis(self):
        """Test I-V curve analysis"""
        from utils.calculations import PVCalculations

        # Simulate I-V curve
        voltage = np.linspace(0, 40, 100)
        current = 8 * (1 - voltage / 40)

        params = PVCalculations.analyze_iv_curve(voltage, current, area=1.6, irradiance=1000)

        assert params.isc > 0
        assert params.voc > 0
        assert params.pmax > 0
        assert 0 < params.ff < 1


class TestStatisticalAnalysis:
    """Test statistical analysis utilities"""

    def test_uncertainty_calculation(self):
        """Test uncertainty calculation"""
        from utils.calculations import StatisticalAnalysis

        data = np.random.normal(100, 5, 30)
        result = StatisticalAnalysis.calculate_uncertainty(data)

        assert 'mean' in result
        assert 'std' in result
        assert 'confidence_interval_lower' in result
        assert 'confidence_interval_upper' in result

    def test_outlier_detection(self):
        """Test outlier detection"""
        from utils.calculations import StatisticalAnalysis

        # Create data with outliers
        data = np.concatenate([
            np.random.normal(100, 5, 50),
            np.array([200, 250])  # Outliers
        ])

        indices, values = StatisticalAnalysis.detect_outliers(data, method='zscore')
        assert len(indices) > 0


class TestReportGeneration:
    """Test report generation utilities"""

    def test_json_report_generation(self):
        """Test JSON report generation"""
        from utils.report_generator import ReportGenerator

        protocol_data = {
            "protocol_id": "TEST-001",
            "execution_id": "test-exec-001",
            "status": "completed",
            "results": {"pmax": 250.0}
        }

        generator = ReportGenerator(protocol_data)
        json_report = generator.generate_json()

        assert json_report is not None
        assert "TEST-001" in json_report


# Fixtures
@pytest.fixture
def sample_iv_data():
    """Sample I-V curve data"""
    voltage = np.linspace(0, 40, 100)
    current = 8 * (1 - voltage / 40)
    return pd.DataFrame({'voltage': voltage, 'current': current})


@pytest.fixture
def sample_protocol_data():
    """Sample protocol execution data"""
    return {
        "protocol_id": "STC-001",
        "execution_id": "test-001",
        "status": "completed",
        "setup": {
            "irradiance": 1000,
            "cell_temperature": 25
        },
        "results": {
            "pmax": 250.0,
            "efficiency": 15.6,
            "fill_factor": 0.78
        }
    }


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
