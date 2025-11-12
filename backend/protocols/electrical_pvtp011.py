"""
PVTP-011: I-V Curve Characterization Handler
Automated parameter extraction (Voc, Isc, Pmax, FF, Rs, Rsh)
"""
from typing import Dict
from backend.protocols.base import BaseProtocolHandler, IVAnalysisMixin
from backend.validators.electrical import PVTP011_Complete


class PVTP011Handler(BaseProtocolHandler, IVAnalysisMixin):
    """Handler for PVTP-011 I-V Curve Characterization"""

    def __init__(self):
        super().__init__("PVTP-011")

    def process_test(self, test_data: Dict) -> Dict:
        """Process complete PVTP-011 test"""
        validated_data = PVTP011_Complete(**test_data)

        # Extract I-V curve data
        iv_curve = [point.dict() for point in validated_data.measurements.iv_curve_data.data_points]

        # Extract electrical parameters
        params = self.extract_iv_parameters(iv_curve)

        # Fit single diode model
        import numpy as np
        V = np.array([p['voltage'] for p in iv_curve])
        I = np.array([p['current'] for p in iv_curve])
        T = validated_data.measurements.test_conditions.module_temperature

        model_fit = self.fit_single_diode_model(V, I, T)

        analysis = {
            'extracted_parameters': params,
            'model_fit': model_fit
        }

        qc_results = self.run_qc_checks({'analysis': analysis})

        return {
            'analysis': analysis,
            'qc_results': qc_results,
            'status': 'completed'
        }
