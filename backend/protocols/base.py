"""
Base protocol handler with common analysis functions
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from scipy.optimize import curve_fit, minimize
from scipy import stats
import json


class BaseProtocolHandler:
    """Base class for all protocol handlers"""

    def __init__(self, protocol_id: str):
        self.protocol_id = protocol_id
        self.template = self.load_template()

    def load_template(self) -> Dict:
        """Load JSON protocol template"""
        template_path = f"protocols/templates/{self.protocol_id.replace('-', '_').lower()}_*.json"
        # Implementation would use glob to find the file
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Template not found for protocol {self.protocol_id}")

    def validate_inputs(self, inputs: Dict) -> Tuple[bool, List[str]]:
        """Validate input data against template"""
        errors = []
        required_fields = self.template.get('inputs', {}).get('required', {})

        for field, config in required_fields.items():
            if field not in inputs:
                errors.append(f"Missing required field: {field}")
                continue

            # Type validation
            field_type = config.get('type')
            value = inputs[field]

            if field_type == 'number':
                validation = config.get('validation', {})
                if 'min' in validation and value < validation['min']:
                    errors.append(f"{field}: value {value} below minimum {validation['min']}")
                if 'max' in validation and value > validation['max']:
                    errors.append(f"{field}: value {value} above maximum {validation['max']}")

        return len(errors) == 0, errors

    def run_qc_checks(self, data: Dict) -> List[Dict]:
        """Run automated QC checks"""
        qc_results = []
        qc_checks = self.template.get('qc_checks', {}).get('automatic', [])

        for check in qc_checks:
            result = self._evaluate_qc_check(check, data)
            qc_results.append(result)

        return qc_results

    def _evaluate_qc_check(self, check: Dict, data: Dict) -> Dict:
        """Evaluate single QC check"""
        parameter = check.get('parameter')
        condition = check.get('condition')
        threshold = check.get('threshold')

        # Extract value from nested data structure
        value = self._extract_value(data, parameter)

        if value is None:
            return {
                'check_id': check['check_id'],
                'status': 'not_checked',
                'message': f"Parameter {parameter} not found"
            }

        # Evaluate condition
        passed = self._evaluate_condition(value, condition, threshold, check)

        return {
            'check_id': check['check_id'],
            'parameter': parameter,
            'measured_value': value,
            'threshold': threshold,
            'status': 'passed' if passed else 'failed',
            'severity': check.get('severity'),
            'message': check.get('message') if not passed else None
        }

    def _evaluate_condition(self, value: float, condition: str, threshold: float, check: Dict) -> bool:
        """Evaluate QC condition"""
        if condition == 'greater_than':
            return value > threshold
        elif condition == 'less_than':
            return value < threshold
        elif condition == 'within_range':
            range_val = check.get('range', [])
            return range_val[0] <= value <= range_val[1]
        elif condition == 'within_tolerance':
            tolerance = check.get('tolerance')
            nameplate = check.get('nameplate_value')
            if nameplate:
                deviation = abs((value - nameplate) / nameplate) * 100
                return deviation <= tolerance
        else:
            return True

    def _extract_value(self, data: Dict, path: str) -> Optional[float]:
        """Extract value from nested dictionary using dot notation"""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current if isinstance(current, (int, float)) else None

    def calculate_uncertainty(self, budget: Dict) -> Dict[str, float]:
        """Calculate combined and expanded uncertainty using GUM method"""
        # Extract uncertainty components
        components = []
        for source, config in budget.items():
            rel_unc = config.get('relative_uncertainty', 0)
            components.append(rel_unc ** 2)

        # Combined standard uncertainty (RSS)
        combined = np.sqrt(sum(components))

        # Expanded uncertainty (k=2 for 95% confidence)
        expanded = combined * 2

        return {
            'combined_uncertainty': combined * 100,  # as percentage
            'expanded_uncertainty': expanded * 100,
            'coverage_factor': 2,
            'confidence_level': 0.95
        }

    def correct_to_stc(self, measured: Dict, conditions: Dict, coefficients: Dict) -> Dict:
        """
        Correct measurements to STC using IEC 60891 method
        STC: 25°C, 1000 W/m², AM1.5G
        """
        G_meas = conditions.get('irradiance', 1000)
        T_meas = conditions.get('temperature', 25)
        G_stc = 1000
        T_stc = 25

        alpha = coefficients.get('alpha_isc', 0.0005)  # A/°C or %/°C
        beta = coefficients.get('beta_voc', -0.0035)  # V/°C or %/°C

        # Irradiance correction (linear for current)
        isc_stc = measured['isc'] * (G_stc / G_meas)

        # Temperature correction
        voc_stc = measured['voc'] + beta * measured['voc'] * (T_stc - T_meas)

        # Power correction (using both corrections)
        # Simplified approach - full method requires iterative correction
        pmax_stc = measured['pmax'] * (G_stc / G_meas) * (1 + coefficients.get('gamma_pmax', -0.004) * (T_stc - T_meas))

        return {
            'voc_stc': voc_stc,
            'isc_stc': isc_stc,
            'pmax_stc': pmax_stc,
            'conditions': {'irradiance': G_stc, 'temperature': T_stc}
        }


class IVAnalysisMixin:
    """Mixin for I-V curve analysis"""

    def extract_iv_parameters(self, iv_data: List[Dict]) -> Dict:
        """Extract electrical parameters from I-V curve"""
        voltages = np.array([p['voltage'] for p in iv_data])
        currents = np.array([p['current'] for p in iv_data])
        powers = voltages * currents

        # Find Voc (interpolate to I=0)
        voc = np.interp(0, currents[::-1], voltages[::-1])

        # Find Isc (interpolate to V=0)
        isc = np.interp(0, voltages, currents)

        # Find MPP
        pmax_idx = np.argmax(powers)
        pmax = powers[pmax_idx]
        vmpp = voltages[pmax_idx]
        impp = currents[pmax_idx]

        # Calculate fill factor
        ff = pmax / (voc * isc) if (voc * isc) > 0 else 0

        # Calculate series resistance (slope near Voc)
        rs = self._calculate_series_resistance(voltages, currents, voc)

        # Calculate shunt resistance (slope near Isc)
        rsh = self._calculate_shunt_resistance(voltages, currents)

        return {
            'voc': float(voc),
            'isc': float(isc),
            'pmax': float(pmax),
            'vmpp': float(vmpp),
            'impp': float(impp),
            'fill_factor': float(ff),
            'series_resistance': float(rs),
            'shunt_resistance': float(rsh)
        }

    def _calculate_series_resistance(self, V: np.ndarray, I: np.ndarray, voc: float) -> float:
        """Calculate series resistance from high-voltage region"""
        # Use last 10% of current range
        threshold = 0.1 * I.max()
        mask = I < threshold
        if np.sum(mask) < 2:
            return 0.0

        V_region = V[mask]
        I_region = I[mask]

        # Linear fit: V = V0 + Rs*I, so Rs = dV/dI
        if len(V_region) > 1:
            slope, _ = np.polyfit(I_region, V_region, 1)
            return abs(slope)
        return 0.0

    def _calculate_shunt_resistance(self, V: np.ndarray, I: np.ndarray) -> float:
        """Calculate shunt resistance from low-voltage region"""
        # Use region near V=0 (±0.5V)
        mask = np.abs(V) < 0.5
        if np.sum(mask) < 2:
            return 1e6  # Very high if cannot calculate

        V_region = V[mask]
        I_region = I[mask]

        # Linear fit near origin: I = V/Rsh, so Rsh = dV/dI
        if len(V_region) > 1:
            slope, _ = np.polyfit(V_region, I_region, 1)
            return 1.0 / slope if slope != 0 else 1e6
        return 1e6

    def fit_single_diode_model(self, V: np.ndarray, I: np.ndarray, T: float = 25) -> Dict:
        """
        Fit single diode model to I-V data
        I = I_L - I_0 * [exp(q*(V+I*Rs)/(n*k*T)) - 1] - (V+I*Rs)/Rsh
        """
        k = 1.380649e-23  # Boltzmann constant
        q = 1.602176634e-19  # Elementary charge
        T_K = T + 273.15  # Temperature in Kelvin

        def single_diode(V, I_L, I_0, Rs, Rsh, n):
            """Single diode equation (implicit)"""
            # Simplified explicit form for fitting
            V_diode = V - I * Rs
            I_diode = I_0 * (np.exp(q * V_diode / (n * k * T_K)) - 1)
            I_shunt = V_diode / Rsh
            return I_L - I_diode - I_shunt

        # Initial guess
        I_L_guess = I.max()
        I_0_guess = 1e-9
        Rs_guess = 0.5
        Rsh_guess = 1000
        n_guess = 1.5

        try:
            # Fit using curve_fit
            popt, pcov = curve_fit(
                single_diode,
                V, I,
                p0=[I_L_guess, I_0_guess, Rs_guess, Rsh_guess, n_guess],
                bounds=([0, 1e-15, 0, 10, 0.5], [I_L_guess*1.5, 1e-6, 10, 1e6, 5]),
                maxfev=5000
            )

            I_L, I_0, Rs, Rsh, n = popt

            # Calculate R²
            I_fit = single_diode(V, *popt)
            ss_res = np.sum((I - I_fit) ** 2)
            ss_tot = np.sum((I - I.mean()) ** 2)
            r_squared = 1 - (ss_res / ss_tot)

            return {
                'I_L': float(I_L),
                'I_0': float(I_0),
                'Rs': float(Rs),
                'Rsh': float(Rsh),
                'n': float(n),
                'r_squared': float(r_squared),
                'fit_successful': True
            }
        except Exception as e:
            return {
                'fit_successful': False,
                'error': str(e)
            }


class StatisticalAnalysisMixin:
    """Mixin for statistical analysis"""

    def linear_regression(self, x: np.ndarray, y: np.ndarray) -> Dict:
        """Perform linear regression and return statistics"""
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'std_err': float(std_err),
            'equation': f'y = {slope:.6f}x + {intercept:.6f}'
        }

    def calculate_confidence_interval(self, data: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval"""
        mean = np.mean(data)
        sem = stats.sem(data)
        ci = sem * stats.t.ppf((1 + confidence) / 2, len(data) - 1)
        return float(mean - ci), float(mean + ci)
