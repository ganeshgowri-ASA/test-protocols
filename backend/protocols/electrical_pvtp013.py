"""PVTP-013: Temperature Coefficient Handler"""
from typing import Dict
import numpy as np
from backend.protocols.base import BaseProtocolHandler, StatisticalAnalysisMixin
from backend.validators.electrical import PVTP013_Complete

class PVTP013Handler(BaseProtocolHandler, StatisticalAnalysisMixin):
    def __init__(self):
        super().__init__("PVTP-013")

    def process_test(self, test_data: Dict) -> Dict:
        validated_data = PVTP013_Complete(**test_data)
        temp_points = validated_data.measurements.temperature_points
        # Extract temperatures and parameters for regression
        temperatures = np.array([p.module_temperature_measured for p in temp_points])
        isc_values = np.array([p.isc for p in temp_points])
        voc_values = np.array([p.voc for p in temp_points])
        pmax_values = np.array([p.pmax for p in temp_points])
        
        # Calculate temperature coefficients via linear regression
        alpha_fit = self.linear_regression(temperatures, isc_values)
        beta_fit = self.linear_regression(temperatures, voc_values)
        gamma_fit = self.linear_regression(temperatures, pmax_values)
        
        return {'analysis': {
            'coefficients': {
                'alpha_isc_absolute': alpha_fit['slope'],
                'beta_voc_absolute': beta_fit['slope'],
                'gamma_pmax_absolute': gamma_fit['slope'],
                'alpha_r_squared': alpha_fit['r_squared'],
                'beta_r_squared': beta_fit['r_squared'],
                'gamma_r_squared': gamma_fit['r_squared']
            }
        }, 'qc_results': [], 'status': 'completed'}
