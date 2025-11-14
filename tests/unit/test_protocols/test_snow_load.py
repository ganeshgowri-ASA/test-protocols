"""Unit tests for Snow Load protocol - SNOW-001"""

import pytest
from datetime import datetime

from protocols.mechanical.snow_load.protocol import (
    SnowLoadTestProtocol,
    SnowLoadTestConfig,
    ModuleSpecs,
    LoadPhase,
    VisualCondition
)
from protocols.mechanical.snow_load.validators import (
    validate_snow_load_config,
    validate_module_specs,
    validate_acceptance_criteria,
    validate_measurement
)
from protocols.mechanical.snow_load.analysis import (
    SnowLoadAnalyzer,
    plot_load_deflection_curve,
    calculate_safety_factor
)
from protocols.base.validators import ValidationError


class TestModuleSpecs:
    """Test module specifications validation"""

    def test_valid_module_specs(self, sample_module_specs):
        """Valid module specs should not raise"""
        sample_module_specs.validate()  # Should not raise

    def test_module_area_calculation(self, sample_module_specs):
        """Module area should be calculated correctly"""
        expected_area = (1650 * 992) / 1_000_000
        assert sample_module_specs.area_m2 == pytest.approx(expected_area, rel=1e-3)

    def test_invalid_dimensions(self):
        """Invalid dimensions should raise ValidationError"""
        with pytest.raises(ValidationError):
            specs = ModuleSpecs(
                module_id="TEST",
                length_mm=-100,  # Invalid
                width_mm=992,
                thickness_mm=35,
                mass_kg=18.5
            )
            specs.validate()

    def test_invalid_mass(self):
        """Invalid mass should raise ValidationError"""
        with pytest.raises(ValidationError):
            specs = ModuleSpecs(
                module_id="TEST",
                length_mm=1650,
                width_mm=992,
                thickness_mm=35,
                mass_kg=-10  # Invalid
            )
            specs.validate()


class TestSnowLoadConfig:
    """Test snow load configuration validation"""

    def test_valid_config(self, sample_snow_load_config):
        """Valid configuration should not raise"""
        sample_snow_load_config.validate()  # Should not raise

    def test_snow_load_conversion(self, sample_snow_load_config):
        """Pa to kg/m² conversion should be correct"""
        # 2400 Pa ≈ 244.8 kg/m²
        expected_kg_m2 = 2400 * 0.102
        assert sample_snow_load_config.snow_load_kg_m2 == pytest.approx(expected_kg_m2, rel=1e-2)

    def test_invalid_snow_load(self):
        """Invalid snow load should raise"""
        with pytest.raises(ValidationError):
            config = SnowLoadTestConfig(
                snow_load_pa=20000,  # Too high
                hold_duration_hours=1.0
            )
            config.validate()

    def test_invalid_duration(self):
        """Invalid duration should raise"""
        with pytest.raises(ValidationError):
            config = SnowLoadTestConfig(
                snow_load_pa=2400,
                hold_duration_hours=0.1  # Too short
            )
            config.validate()

    def test_invalid_temperature(self):
        """Invalid temperature should raise"""
        with pytest.raises(ValidationError):
            config = SnowLoadTestConfig(
                snow_load_pa=2400,
                hold_duration_hours=1.0,
                test_temperature_c=-100  # Too low
            )
            config.validate()

    def test_invalid_cycles(self):
        """Invalid cycles should raise"""
        with pytest.raises(ValidationError):
            config = SnowLoadTestConfig(
                snow_load_pa=2400,
                hold_duration_hours=1.0,
                cycles=0  # Must be at least 1
            )
            config.validate()


class TestSnowLoadProtocol:
    """Test snow load protocol execution"""

    def test_protocol_initialization(self, snow_load_protocol, sample_module_specs):
        """Protocol should initialize correctly"""
        assert snow_load_protocol.module_specs.module_id == sample_module_specs.module_id
        assert snow_load_protocol.config.snow_load_pa == 2400
        assert len(snow_load_protocol.measurements) == 0
        assert snow_load_protocol.test_result is None

    def test_deflection_calculation_zero_load(self, snow_load_protocol):
        """Zero load should give minimal deflection"""
        deflection = snow_load_protocol._measure_deflection(load_pa=0)
        assert deflection >= 0
        assert deflection < 1.0  # Should be very small

    def test_deflection_calculation_increases_with_load(self, snow_load_protocol):
        """Deflection should increase with load"""
        deflection_1000 = snow_load_protocol._measure_deflection(load_pa=1000)
        deflection_2000 = snow_load_protocol._measure_deflection(load_pa=2000)
        deflection_3000 = snow_load_protocol._measure_deflection(load_pa=3000)

        assert deflection_2000 > deflection_1000
        assert deflection_3000 > deflection_2000

    def test_measurement_recording(self, snow_load_protocol):
        """Measurements should be recorded correctly"""
        initial_count = len(snow_load_protocol.measurements)

        snow_load_protocol._record_measurement(
            load_applied_pa=2400,
            deflection_mm=25.0,
            phase=LoadPhase.LOADING,
            visual_condition=VisualCondition.NORMAL
        )

        assert len(snow_load_protocol.measurements) == initial_count + 1
        measurement = snow_load_protocol.measurements[-1]
        assert measurement.load_applied_pa == 2400
        assert measurement.deflection_mm == 25.0
        assert measurement.phase == LoadPhase.LOADING

    def test_execute_single_cycle(self, snow_load_protocol):
        """Single cycle execution should complete"""
        result = snow_load_protocol.execute()

        assert result is not None
        assert isinstance(result, bool)
        assert len(snow_load_protocol.steps) > 0
        assert len(snow_load_protocol.measurements) > 0
        assert snow_load_protocol.test_result is not None

    def test_execute_multiple_cycles(self, sample_module_specs):
        """Multi-cycle test should execute all cycles"""
        config = SnowLoadTestConfig(
            snow_load_pa=2400,
            hold_duration_hours=0.5,
            cycles=3
        )
        protocol = SnowLoadTestProtocol(config, sample_module_specs)

        result = protocol.execute()

        assert protocol.current_cycle == 3
        # Should have multiple baseline measurements (one per cycle)
        baseline_measurements = [
            m for m in protocol.measurements if m.phase == LoadPhase.BASELINE
        ]
        assert len(baseline_measurements) == 3

    def test_evaluation_pass_criteria(self, sample_module_specs):
        """Module should pass if within criteria"""
        config = SnowLoadTestConfig(
            snow_load_pa=2400,
            hold_duration_hours=0.5,
            max_deflection_mm=100.0,  # Generous limit
            max_permanent_deflection_mm=10.0
        )
        protocol = SnowLoadTestProtocol(config, sample_module_specs)

        result = protocol.execute()
        assert result is True

    def test_evaluation_fail_excessive_deflection(self, sample_module_specs):
        """Module should fail if deflection exceeds limit"""
        config = SnowLoadTestConfig(
            snow_load_pa=2400,
            hold_duration_hours=0.5,
            max_deflection_mm=1.0,  # Very strict limit
            max_permanent_deflection_mm=0.5
        )
        protocol = SnowLoadTestProtocol(config, sample_module_specs)

        result = protocol.execute()
        assert result is False

    def test_visual_inspection_normal(self, snow_load_protocol):
        """Visual inspection should detect normal condition"""
        snow_load_protocol.max_deflection_observed = 20.0
        snow_load_protocol.config.max_deflection_mm = 50.0

        condition = snow_load_protocol._perform_visual_inspection()
        assert condition == VisualCondition.NORMAL

    def test_visual_inspection_cracking(self, snow_load_protocol):
        """Visual inspection should detect cracking"""
        snow_load_protocol.max_deflection_observed = 80.0
        snow_load_protocol.config.max_deflection_mm = 50.0

        condition = snow_load_protocol._perform_visual_inspection()
        assert condition in [
            VisualCondition.MICRO_CRACK,
            VisualCondition.HAIRLINE_CRACK,
            VisualCondition.VISIBLE_CRACK
        ]

    def test_report_generation(self, snow_load_protocol):
        """Report should contain all test data"""
        snow_load_protocol.execute()
        report = snow_load_protocol.get_report_data()

        assert report["protocol_id"] == "SNOW-001"
        assert report["module_id"] == "TEST-MOD-001"
        assert "test_conditions" in report
        assert "results" in report
        assert "measurements" in report
        assert "steps" in report
        assert len(report["measurements"]) > 0


class TestSnowLoadValidators:
    """Test validation functions"""

    def test_validate_snow_load_config_valid(self):
        """Valid config should not raise"""
        config = {
            "snow_load_pa": 2400,
            "hold_duration_hours": 1.0,
            "cycles": 1
        }
        validate_snow_load_config(config)  # Should not raise

    def test_validate_snow_load_config_invalid_load(self):
        """Invalid load should raise"""
        config = {
            "snow_load_pa": 20000,
            "hold_duration_hours": 1.0,
            "cycles": 1
        }
        with pytest.raises(ValidationError):
            validate_snow_load_config(config)

    def test_validate_module_specs_valid(self):
        """Valid module specs should not raise"""
        specs = {
            "module_id": "TEST-001",
            "dimensions": {
                "length_mm": 1650,
                "width_mm": 992,
                "thickness_mm": 35
            },
            "mass_kg": 18.5
        }
        validate_module_specs(specs)  # Should not raise

    def test_validate_module_specs_missing_required(self):
        """Missing required field should raise"""
        specs = {
            "module_id": "TEST-001",
            "mass_kg": 18.5
            # Missing dimensions
        }
        with pytest.raises(ValidationError):
            validate_module_specs(specs)

    def test_validate_acceptance_criteria_valid(self):
        """Valid criteria should not raise"""
        criteria = {
            "max_deflection_mm": 50.0,
            "max_cracking": "none"
        }
        validate_acceptance_criteria(criteria)  # Should not raise

    def test_validate_acceptance_criteria_invalid_permanent(self):
        """Permanent deflection > max deflection should raise"""
        criteria = {
            "max_deflection_mm": 50.0,
            "max_permanent_deflection_mm": 60.0,
            "max_cracking": "none"
        }
        with pytest.raises(ValidationError):
            validate_acceptance_criteria(criteria)

    def test_validate_measurement_valid(self):
        """Valid measurement should not raise"""
        measurement = {
            "timestamp": datetime.now().isoformat(),
            "phase": "loading",
            "load_applied_pa": 2400,
            "deflection_mm": 25.0
        }
        validate_measurement(measurement)  # Should not raise

    def test_validate_measurement_invalid_phase(self):
        """Invalid phase should raise"""
        measurement = {
            "timestamp": datetime.now().isoformat(),
            "phase": "invalid_phase",
            "load_applied_pa": 2400,
            "deflection_mm": 25.0
        }
        with pytest.raises(ValidationError):
            validate_measurement(measurement)


class TestSnowLoadAnalyzer:
    """Test analysis functions"""

    def test_analyzer_initialization(self, sample_measurements):
        """Analyzer should initialize correctly"""
        analyzer = SnowLoadAnalyzer(sample_measurements, baseline_deflection=0.2)
        assert len(analyzer.measurements) == len(sample_measurements)
        assert analyzer.baseline_deflection == 0.2

    def test_analyze_results(self, sample_measurements):
        """Analysis should produce results"""
        analyzer = SnowLoadAnalyzer(sample_measurements, baseline_deflection=0.2)
        results = analyzer.analyze()

        assert results.max_deflection_mm > 0
        assert results.permanent_deflection_mm >= 0
        assert results.elastic_recovery_pct >= 0
        assert len(results.load_deflection_curve) > 0

    def test_stiffness_calculation(self, sample_measurements):
        """Stiffness should be calculated"""
        analyzer = SnowLoadAnalyzer(sample_measurements, baseline_deflection=0.2)
        results = analyzer.analyze()

        # Stiffness may be None if insufficient data
        if results.stiffness_n_mm is not None:
            assert results.stiffness_n_mm > 0

    def test_elastic_recovery_calculation(self, sample_measurements):
        """Elastic recovery should be calculated correctly"""
        analyzer = SnowLoadAnalyzer(sample_measurements, baseline_deflection=0.2)
        results = analyzer.analyze()

        # Recovery should be high (most deflection is elastic)
        assert results.elastic_recovery_pct > 80

    def test_generate_summary(self, sample_measurements):
        """Summary should contain key metrics"""
        analyzer = SnowLoadAnalyzer(sample_measurements, baseline_deflection=0.2)
        summary = analyzer.generate_summary()

        assert "max_deflection_mm" in summary
        assert "permanent_deflection_mm" in summary
        assert "test_result" in summary
        assert "total_measurements" in summary

    def test_plot_load_deflection_curve(self, sample_measurements):
        """Plot data should be generated"""
        analyzer = SnowLoadAnalyzer(sample_measurements, baseline_deflection=0.2)
        results = analyzer.analyze()

        plot_data = plot_load_deflection_curve(
            results.load_deflection_curve,
            "Test Plot"
        )

        assert plot_data["title"] == "Test Plot"
        assert "x_label" in plot_data
        assert "y_label" in plot_data
        assert "series" in plot_data
        assert len(plot_data["series"]) > 0

    def test_calculate_safety_factor(self):
        """Safety factor should be calculated correctly"""
        sf = calculate_safety_factor(test_load_pa=2400, design_load_pa=1200)
        assert sf == pytest.approx(2.0)

    def test_safety_factor_zero_design_load(self):
        """Zero design load should return infinity"""
        sf = calculate_safety_factor(test_load_pa=2400, design_load_pa=0)
        assert sf == float('inf')


class TestStepExecution:
    """Test individual step execution"""

    def test_baseline_step(self, snow_load_protocol):
        """Baseline step should execute correctly"""
        result = snow_load_protocol._baseline_measurement()

        assert result.success is True
        assert len(snow_load_protocol.measurements) == 1
        assert snow_load_protocol.measurements[0].phase == LoadPhase.BASELINE
        assert snow_load_protocol.measurements[0].load_applied_pa == 0

    def test_load_application_step(self, snow_load_protocol):
        """Load application step should execute correctly"""
        result = snow_load_protocol._apply_load()

        assert result.success is True
        assert len(snow_load_protocol.measurements) > 0
        # Last measurement should be at full load
        last_measurement = snow_load_protocol.measurements[-1]
        assert last_measurement.load_applied_pa == pytest.approx(2400, rel=1e-2)

    def test_hold_step(self, snow_load_protocol):
        """Hold step should execute correctly"""
        result = snow_load_protocol._hold_under_load()

        assert result.success is True
        assert len(snow_load_protocol.measurements) > 0

    def test_unload_step(self, snow_load_protocol):
        """Unload step should execute correctly"""
        result = snow_load_protocol._unload()

        assert result.success is True
        assert len(snow_load_protocol.measurements) > 0
        # Last measurement should be at zero load
        last_measurement = snow_load_protocol.measurements[-1]
        assert last_measurement.load_applied_pa == pytest.approx(0, abs=1e-6)

    def test_recovery_step(self, snow_load_protocol):
        """Recovery step should execute correctly"""
        snow_load_protocol.baseline_deflection = 0.5
        result = snow_load_protocol._recovery_measurement()

        assert result.success is True
        assert len(snow_load_protocol.measurements) > 0
        assert snow_load_protocol.measurements[-1].phase == LoadPhase.RECOVERY
