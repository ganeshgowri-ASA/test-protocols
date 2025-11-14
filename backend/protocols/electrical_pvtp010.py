"""
PVTP-010: Flash Test / STC Performance Handler
Handles STC correction algorithms and uncertainty analysis
"""
import numpy as np
from typing import Dict, List, Optional
from backend.protocols.base import BaseProtocolHandler, StatisticalAnalysisMixin
from backend.validators.electrical import (
    PVTP010_Input, PVTP010_Measurement, PVTP010_Analysis,
    PVTP010_STCResults, PVTP010_Complete
)


class PVTP010Handler(BaseProtocolHandler, StatisticalAnalysisMixin):
    """Handler for PVTP-010 Flash Test / STC Performance"""

    def __init__(self):
        super().__init__("PVTP-010")

    def process_test(self, test_data: Dict) -> Dict:
        """Process complete PVTP-010 test"""
        # Validate input data
        validated_data = PVTP010_Complete(**test_data)

        # Extract measurements
        flash_meas = validated_data.measurements.flash_measurement
        conditions = validated_data.measurements.pre_test_conditions
        mmf = validated_data.measurements.spectral_mismatch_factor

        # Correct to STC
        stc_results = self.correct_flash_to_stc(
            flash_measurement=flash_meas.dict(),
            mmf=mmf,
            coefficients={
                'alpha_isc': 0.0005,  # Default, should be from input
                'beta_voc': -0.0035,
                'gamma_pmax': -0.004
            }
        )

        # Calculate uncertainty
        uncertainty = self.calculate_measurement_uncertainty(
            flash_measurement=flash_meas.dict(),
            conditions=conditions
        )

        stc_results.update(uncertainty)

        # Calculate performance ratio
        performance = self.calculate_performance_ratio(
            pmax_stc=stc_results['pmax_stc'],
            nameplate_power=validated_data.inputs.rated_power
        )

        # Construct analysis results
        analysis = {
            'stc_results': stc_results,
            'performance_ratio': performance['performance_ratio'],
            'power_deviation': performance['power_deviation']
        }

        # Run QC checks
        qc_results = self.run_qc_checks({
            'analysis': analysis,
            'measurements': validated_data.measurements.dict()
        })

        return {
            'analysis': analysis,
            'qc_results': qc_results,
            'status': 'completed' if all(qc['status'] == 'passed' for qc in qc_results) else 'requires_review'
        }

    def correct_flash_to_stc(self, flash_measurement: Dict, mmf: float, coefficients: Dict) -> Dict:
        """
        Correct flash measurements to STC conditions
        Implements IEC 60891:2021 Method 1
        """
        # Extract measured values
        G_meas = flash_measurement['irradiance_measured']
        T_meas = flash_measurement['temperature_measured']
        Voc_meas = flash_measurement['voc_measured']
        Isc_meas = flash_measurement['isc_measured']
        Pmax_meas = flash_measurement['pmax_measured']
        Vmpp_meas = flash_measurement['vmpp_measured']
        Impp_meas = flash_measurement['impp_measured']

        # STC conditions
        G_stc = 1000.0  # W/m²
        T_stc = 25.0    # °C

        # Temperature coefficients
        alpha = coefficients['alpha_isc']  # 1/°C or %/°C
        beta = coefficients['beta_voc']    # 1/°C or %/°C
        gamma = coefficients['gamma_pmax']  # 1/°C or %/°C

        # Irradiance correction with spectral mismatch
        G_corr = G_meas * mmf

        # Temperature difference
        dT = T_stc - T_meas

        # Correct Isc (linear with irradiance, temp coefficient)
        Isc_stc = Isc_meas * (G_stc / G_corr) * (1 + alpha * dT)

        # Correct Voc (logarithmic with irradiance, temp coefficient)
        k = 1.380649e-23  # Boltzmann constant
        q = 1.602176634e-19  # Elementary charge
        n = 1.3  # Typical ideality factor
        T_K = T_meas + 273.15
        Vt = (n * k * T_K) / q  # Thermal voltage

        Voc_stc = Voc_meas + Vt * np.log(G_stc / G_corr) + beta * Voc_meas * dT

        # Correct Vmpp and Impp
        Vmpp_stc = Vmpp_meas + Vt * np.log(G_stc / G_corr) + beta * Vmpp_meas * dT
        Impp_stc = Impp_meas * (G_stc / G_corr) * (1 + alpha * dT)

        # Correct Pmax
        Pmax_stc = Vmpp_stc * Impp_stc

        # Calculate FF at STC
        FF_stc = Pmax_stc / (Voc_stc * Isc_stc) if (Voc_stc * Isc_stc) > 0 else 0

        return {
            'voc_stc': float(Voc_stc),
            'isc_stc': float(Isc_stc),
            'pmax_stc': float(Pmax_stc),
            'vmpp_stc': float(Vmpp_stc),
            'impp_stc': float(Impp_stc),
            'ff_stc': float(FF_stc),
            'correction_factors': {
                'irradiance_ratio': G_stc / G_corr,
                'temperature_delta': dT,
                'spectral_mismatch': mmf
            }
        }

    def calculate_measurement_uncertainty(self, flash_measurement: Dict, conditions: Dict) -> Dict:
        """
        Calculate measurement uncertainty using GUM method
        Returns combined and expanded uncertainty for Pmax
        """
        # Uncertainty budget components (relative uncertainties)
        u_irradiance = 0.02        # ±2% irradiance sensor
        u_temperature = 0.01       # ±1% temperature (via coefficient)
        u_voltage = 0.005          # ±0.5% voltage measurement
        u_current = 0.01           # ±1% current measurement
        u_spectral = 0.01          # ±1% spectral mismatch
        u_nonuniformity = 0.01     # ±1% non-uniformity

        # Combined standard uncertainty (RSS method)
        u_combined = np.sqrt(
            u_irradiance**2 +
            u_temperature**2 +
            u_voltage**2 +
            u_current**2 +
            u_spectral**2 +
            u_nonuniformity**2
        )

        # Expanded uncertainty (coverage factor k=2 for 95% confidence)
        k = 2
        u_expanded = k * u_combined

        return {
            'combined_uncertainty_pmax': float(u_combined * 100),  # as percentage
            'expanded_uncertainty_pmax': float(u_expanded * 100),
            'uncertainty_budget': {
                'irradiance': u_irradiance * 100,
                'temperature': u_temperature * 100,
                'voltage': u_voltage * 100,
                'current': u_current * 100,
                'spectral_mismatch': u_spectral * 100,
                'non_uniformity': u_nonuniformity * 100
            },
            'coverage_factor': k,
            'confidence_level': 0.95
        }

    def calculate_performance_ratio(self, pmax_stc: float, nameplate_power: float) -> Dict:
        """Calculate performance ratio vs nameplate"""
        performance_ratio = (pmax_stc / nameplate_power) * 100 if nameplate_power > 0 else 0
        power_deviation = pmax_stc - nameplate_power

        return {
            'performance_ratio': float(performance_ratio),
            'power_deviation': float(power_deviation),
            'meets_positive_tolerance': performance_ratio >= 100,
            'meets_negative_tolerance': performance_ratio >= 97  # -3% typical
        }

    def generate_charts_data(self, test_data: Dict, analysis: Dict) -> Dict:
        """Generate data for charting"""
        stc_results = analysis['stc_results']

        return {
            'performance_comparison': {
                'categories': ['Voc', 'Isc', 'Pmax', 'FF'],
                'measured': [
                    test_data['measurements']['flash_measurement']['voc_measured'],
                    test_data['measurements']['flash_measurement']['isc_measured'],
                    test_data['measurements']['flash_measurement']['pmax_measured'],
                    test_data['measurements']['flash_measurement']['ff_measured']
                ],
                'stc_corrected': [
                    stc_results['voc_stc'],
                    stc_results['isc_stc'],
                    stc_results['pmax_stc'],
                    stc_results['ff_stc']
                ]
            },
            'uncertainty_budget': stc_results.get('uncertainty_budget', {}),
            'performance_ratio': {
                'value': analysis['performance_ratio'],
                'nameplate': 100,
                'tolerance_high': 105,
                'tolerance_low': 97
            }
        }
