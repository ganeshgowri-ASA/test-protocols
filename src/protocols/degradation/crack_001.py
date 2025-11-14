"""
CRACK-001: Cell Crack Propagation Protocol Implementation

Implements the testing and analysis workflow for monitoring crack propagation
in photovoltaic cells under mechanical and thermal stress.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from ..base import (
    BaseProtocol,
    ProtocolDefinition,
    ProtocolResult,
    ProtocolStatus,
    SampleMetadata,
    protocol_registry
)

logger = logging.getLogger(__name__)


class CrackPropagationProtocol(BaseProtocol):
    """Implementation of CRACK-001 protocol for cell crack propagation testing."""

    def __init__(self, definition: ProtocolDefinition):
        """Initialize CRACK-001 protocol."""
        super().__init__(definition)
        if definition.protocol_id != "CRACK-001":
            raise ValueError(f"Invalid protocol ID: {definition.protocol_id}")

    def validate_setup(self, samples: List[SampleMetadata],
                      parameters: Dict[str, Any]) -> List[str]:
        """
        Validate setup for crack propagation testing.

        Args:
            samples: List of sample metadata
            parameters: Test parameters

        Returns:
            List of validation errors
        """
        errors = []

        # Validate sample count
        min_samples = self.definition.data['data_collection']['sample_size']['min']
        if len(samples) < min_samples:
            errors.append(
                f"Minimum {min_samples} samples required, got {len(samples)}"
            )

        # Validate parameters against definition
        param_errors = self.definition.validate_parameters(parameters)
        errors.extend(param_errors)

        # Validate required metadata fields
        required_fields = self.definition.data['data_collection']['metadata']['required_fields']
        for i, sample in enumerate(samples):
            sample_dict = vars(sample)
            for field in required_fields:
                if field not in sample_dict or sample_dict[field] is None:
                    errors.append(f"Sample {i}: Missing required field '{field}'")

        # Validate stress type compatibility
        stress_type = parameters.get('stress_type', 'thermal_cycling')
        if stress_type == 'mechanical_load':
            if 'mechanical_load' not in parameters:
                errors.append("mechanical_load parameter required for mechanical stress test")
        elif stress_type == 'thermal_cycling':
            required_thermal = ['thermal_cycles', 'chamber_temp_low', 'chamber_temp_high']
            for param in required_thermal:
                if param not in parameters:
                    errors.append(f"{param} required for thermal cycling test")

        return errors

    def execute(self, samples: List[SampleMetadata],
                parameters: Dict[str, Any]) -> List[ProtocolResult]:
        """
        Execute crack propagation protocol.

        Args:
            samples: List of sample metadata
            parameters: Test parameters

        Returns:
            List of protocol results
        """
        # Validate before execution
        errors = self.validate_setup(samples, parameters)
        if errors:
            logger.error(f"Validation failed: {errors}")
            raise ValueError(f"Setup validation failed: {errors}")

        self.status = ProtocolStatus.IN_PROGRESS
        results = []

        try:
            for sample in samples:
                logger.info(f"Processing sample: {sample.sample_id}")
                result = self._execute_single_sample(sample, parameters)
                results.append(result)

            self.status = ProtocolStatus.COMPLETED

        except Exception as e:
            logger.error(f"Protocol execution failed: {e}")
            self.status = ProtocolStatus.FAILED
            raise

        return results

    def _execute_single_sample(self, sample: SampleMetadata,
                               parameters: Dict[str, Any]) -> ProtocolResult:
        """Execute protocol for a single sample."""
        result = ProtocolResult(
            protocol_id=self.definition.protocol_id,
            sample_id=sample.sample_id,
            status=ProtocolStatus.IN_PROGRESS,
            start_time=datetime.now()
        )

        try:
            # Step 1: Initial characterization
            logger.info(f"Step 1: Initial characterization - {sample.sample_id}")
            initial_measurements = self._perform_initial_characterization(sample)
            result.measurements['initial'] = initial_measurements

            # Step 2 & 3: Stress application with interim measurements
            logger.info(f"Step 2-3: Stress application - {sample.sample_id}")
            interim_data = self._perform_stress_cycles(sample, parameters)
            result.measurements['interim'] = interim_data

            # Step 4: Final characterization
            logger.info(f"Step 4: Final characterization - {sample.sample_id}")
            final_measurements = self._perform_final_characterization(sample)
            result.measurements['final'] = final_measurements

            # Step 5: Analysis
            logger.info(f"Step 5: Analysis - {sample.sample_id}")
            analysis_results = self.analyze(result.measurements)
            result.analysis_results = analysis_results

            # Evaluate pass/fail
            result.pass_fail = self.evaluate_pass_fail(analysis_results)
            result.status = ProtocolStatus.COMPLETED
            result.end_time = datetime.now()

        except Exception as e:
            logger.error(f"Sample execution failed: {e}")
            result.status = ProtocolStatus.FAILED
            result.errors.append(str(e))
            result.end_time = datetime.now()

        return result

    def _perform_initial_characterization(self, sample: SampleMetadata) -> Dict[str, Any]:
        """Perform initial characterization measurements."""
        # In production, this would interface with actual measurement equipment
        # For now, we structure the expected data format

        measurements = {
            'timestamp': datetime.now().isoformat(),
            'el_imaging': {
                'image_path': f"data/el_images/{sample.sample_id}_initial.png",
                'current': 9.0,  # A
                'exposure_time': 5000,  # ms
                'metadata': {
                    'resolution': '2048x2048',
                    'bit_depth': 16
                }
            },
            'iv_curve': {
                'voltage': [],  # Would be populated with actual measurements
                'current': [],
                'pmax': sample.initial_pmax,
                'voc': sample.initial_voc,
                'isc': sample.initial_isc,
                'ff': sample.initial_ff,
                'conditions': {
                    'irradiance': 1000,  # W/m²
                    'temperature': 25.0   # °C
                }
            },
            'visual_inspection': {
                'image_path': f"data/visual/{sample.sample_id}_initial.jpg",
                'observations': []
            }
        }

        return measurements

    def _perform_stress_cycles(self, sample: SampleMetadata,
                               parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform stress cycling with interim measurements."""
        interim_data = []

        total_cycles = parameters.get('thermal_cycles', 200)
        measurement_interval = parameters.get('measurement_interval', 50)
        stress_type = parameters.get('stress_type', 'thermal_cycling')

        # Calculate measurement points
        measurement_cycles = list(range(measurement_interval, total_cycles + 1, measurement_interval))

        for cycle in measurement_cycles:
            logger.info(f"Measurement at cycle {cycle} for {sample.sample_id}")

            interim_measurement = {
                'cycle': cycle,
                'timestamp': datetime.now().isoformat(),
                'el_imaging': {
                    'image_path': f"data/el_images/{sample.sample_id}_cycle_{cycle}.png",
                    'current': 9.0,
                    'exposure_time': 5000
                },
                'iv_curve': {
                    'voltage': [],
                    'current': [],
                    'pmax': None,  # Would be calculated from IV sweep
                    'voc': None,
                    'isc': None,
                    'ff': None,
                    'conditions': {
                        'irradiance': 1000,
                        'temperature': 25.0
                    }
                },
                'stress_conditions': {
                    'type': stress_type,
                    'cycles_completed': cycle
                }
            }

            interim_data.append(interim_measurement)

        return interim_data

    def _perform_final_characterization(self, sample: SampleMetadata) -> Dict[str, Any]:
        """Perform final characterization measurements."""
        measurements = {
            'timestamp': datetime.now().isoformat(),
            'el_imaging': {
                'image_path': f"data/el_images/{sample.sample_id}_final.png",
                'current': 9.0,
                'exposure_time': 5000,
                'metadata': {
                    'resolution': '2048x2048',
                    'bit_depth': 16
                }
            },
            'iv_curve': {
                'voltage': [],
                'current': [],
                'pmax': None,
                'voc': None,
                'isc': None,
                'ff': None,
                'conditions': {
                    'irradiance': 1000,
                    'temperature': 25.0
                }
            },
            'visual_inspection': {
                'image_path': f"data/visual/{sample.sample_id}_final.jpg",
                'observations': []
            }
        }

        return measurements

    def analyze(self, measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze crack propagation measurements.

        Args:
            measurements: Dict containing initial, interim, and final measurements

        Returns:
            Analysis results including degradation metrics
        """
        initial = measurements.get('initial', {})
        final = measurements.get('final', {})
        interim = measurements.get('interim', [])

        # Extract initial values
        initial_pmax = initial.get('iv_curve', {}).get('pmax', 0)
        initial_ff = initial.get('iv_curve', {}).get('ff', 0)

        # Extract final values
        final_pmax = final.get('iv_curve', {}).get('pmax', 0)
        final_ff = final.get('iv_curve', {}).get('ff', 0)

        # Calculate degradation
        if initial_pmax > 0:
            pmax_degradation = ((initial_pmax - final_pmax) / initial_pmax) * 100
        else:
            pmax_degradation = 0

        if initial_ff > 0:
            ff_degradation = ((initial_ff - final_ff) / initial_ff) * 100
        else:
            ff_degradation = 0

        # Analyze crack progression (placeholder - would use image analysis)
        crack_analysis = self._analyze_crack_progression(measurements)

        analysis = {
            'power_degradation': {
                'initial_pmax': initial_pmax,
                'final_pmax': final_pmax,
                'degradation_percent': pmax_degradation,
                'degradation_absolute': initial_pmax - final_pmax
            },
            'fill_factor': {
                'initial_ff': initial_ff,
                'final_ff': final_ff,
                'degradation_percent': ff_degradation
            },
            'crack_propagation': crack_analysis,
            'degradation_rate': self._calculate_degradation_rate(interim),
            'isolated_cells': crack_analysis.get('isolated_cells', 0)
        }

        return analysis

    def _analyze_crack_progression(self, measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze crack progression from EL images.

        In production, this would use image processing algorithms to detect
        and quantify cracks. For now, returns structure for expected results.
        """
        # Placeholder for actual image analysis
        return {
            'initial_crack_area': 0.0,  # mm²
            'final_crack_area': 0.0,    # mm²
            'crack_growth': 0.0,         # mm²
            'crack_growth_percent': 0.0,
            'crack_length': 0.0,         # mm
            'isolated_cells': 0,
            'crack_locations': [],
            'severity': 'low'  # low, medium, high
        }

    def _calculate_degradation_rate(self, interim_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate degradation rate from interim measurements."""
        if not interim_data:
            return {'rate_percent_per_cycle': 0.0, 'linear_fit': None}

        cycles = [m['cycle'] for m in interim_data]
        pmax_values = [m.get('iv_curve', {}).get('pmax', 0) for m in interim_data]

        if len(cycles) > 1 and len(pmax_values) > 1:
            # Linear fit to degradation
            coeffs = np.polyfit(cycles, pmax_values, 1)
            slope = coeffs[0]  # Power change per cycle

            return {
                'rate_percent_per_cycle': float(slope),
                'linear_fit': {
                    'slope': float(slope),
                    'intercept': float(coeffs[1])
                }
            }

        return {'rate_percent_per_cycle': 0.0, 'linear_fit': None}

    def evaluate_pass_fail(self, analysis_results: Dict[str, Any]) -> bool:
        """
        Evaluate pass/fail criteria for crack propagation test.

        Args:
            analysis_results: Results from analyze()

        Returns:
            True if sample passes all criteria
        """
        criteria = self.definition.pass_fail_criteria

        # Check power degradation
        max_pmax_deg = criteria['max_power_degradation']['threshold']
        actual_pmax_deg = analysis_results['power_degradation']['degradation_percent']
        if actual_pmax_deg > max_pmax_deg:
            logger.warning(
                f"Power degradation {actual_pmax_deg:.2f}% exceeds limit {max_pmax_deg}%"
            )
            return False

        # Check fill factor degradation
        max_ff_deg = criteria['fill_factor_degradation']['threshold']
        actual_ff_deg = analysis_results['fill_factor']['degradation_percent']
        if actual_ff_deg > max_ff_deg:
            logger.warning(
                f"FF degradation {actual_ff_deg:.2f}% exceeds limit {max_ff_deg}%"
            )
            return False

        # Check crack propagation
        max_crack_growth = criteria['max_crack_propagation']['threshold']
        actual_crack_growth = analysis_results['crack_propagation']['crack_growth_percent']
        if actual_crack_growth > max_crack_growth:
            logger.warning(
                f"Crack growth {actual_crack_growth:.2f}% exceeds limit {max_crack_growth}%"
            )
            return False

        # Check isolated cells
        max_isolated = criteria['isolated_cells']['threshold']
        actual_isolated = analysis_results.get('isolated_cells', 0)
        if actual_isolated > max_isolated:
            logger.warning(
                f"Isolated cells {actual_isolated} exceeds limit {max_isolated}"
            )
            return False

        return True


# Register protocol
def register():
    """Register CRACK-001 protocol with global registry."""
    definition_path = Path(__file__).parent.parent.parent.parent / \
                     "protocols" / "degradation" / "crack-001" / "protocol.json"

    if definition_path.exists():
        definition = ProtocolDefinition(definition_path)
        protocol_registry.register("CRACK-001", CrackPropagationProtocol)
        logger.info("CRACK-001 protocol registered")
    else:
        logger.warning(f"Protocol definition not found: {definition_path}")


# Auto-register when module is imported
register()
