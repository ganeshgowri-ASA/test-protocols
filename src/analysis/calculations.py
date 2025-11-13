"""Analysis calculations for PV module testing."""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats
from scipy.interpolate import interp1d


class IVCurveAnalyzer:
    """Analyzes I-V curve data for PV modules."""

    def __init__(self, voltages: np.ndarray, currents: np.ndarray):
        """Initialize I-V curve analyzer.

        Args:
            voltages: Array of voltage measurements (V)
            currents: Array of current measurements (A)
        """
        self.voltages = np.array(voltages)
        self.currents = np.array(currents)
        self.powers = self.voltages * self.currents

        # Sort by voltage for consistent analysis
        sort_idx = np.argsort(self.voltages)
        self.voltages = self.voltages[sort_idx]
        self.currents = self.currents[sort_idx]
        self.powers = self.powers[sort_idx]

    def find_mpp(self) -> Tuple[float, float, float]:
        """Find maximum power point.

        Returns:
            Tuple of (Pmax, Vmp, Imp)
        """
        max_idx = np.argmax(self.powers)
        pmax = self.powers[max_idx]
        vmp = self.voltages[max_idx]
        imp = self.currents[max_idx]

        return float(pmax), float(vmp), float(imp)

    def find_voc(self) -> float:
        """Find open circuit voltage.

        Returns:
            Voc (V)
        """
        # Interpolate to find voltage at zero current
        if self.currents[-1] <= 0.01:  # Already at or near zero current
            return float(self.voltages[-1])

        # Create interpolation function
        f = interp1d(self.currents[::-1], self.voltages[::-1],
                     kind='linear', fill_value='extrapolate')
        voc = float(f(0))

        return max(voc, float(self.voltages[-1]))

    def find_isc(self) -> float:
        """Find short circuit current.

        Returns:
            Isc (A)
        """
        # Interpolate to find current at zero voltage
        if self.voltages[0] <= 0.01:  # Already at or near zero voltage
            return float(self.currents[0])

        # Create interpolation function
        f = interp1d(self.voltages, self.currents,
                     kind='linear', fill_value='extrapolate')
        isc = float(f(0))

        return max(isc, float(self.currents[0]))

    def calculate_fill_factor(self) -> float:
        """Calculate fill factor.

        Returns:
            Fill factor (0-1)
        """
        pmax, vmp, imp = self.find_mpp()
        voc = self.find_voc()
        isc = self.find_isc()

        if voc <= 0 or isc <= 0:
            return 0.0

        ff = pmax / (voc * isc)
        return float(np.clip(ff, 0, 1))

    def validate_curve(self) -> Tuple[bool, List[str]]:
        """Validate I-V curve quality.

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        # Check for sufficient data points
        if len(self.voltages) < 10:
            issues.append(f"Insufficient data points: {len(self.voltages)} < 10")

        # Check for monotonicity (current should decrease with voltage)
        diffs = np.diff(self.currents)
        if np.any(diffs > 0.1):  # Allow small fluctuations
            issues.append("Current not monotonically decreasing with voltage")

        # Check for negative values
        if np.any(self.voltages < 0):
            issues.append("Negative voltage values detected")
        if np.any(self.currents < 0):
            issues.append("Negative current values detected")

        # Check for reasonable ranges
        voc = self.find_voc()
        isc = self.find_isc()
        if voc < 10 or voc > 1500:
            issues.append(f"Unreasonable Voc: {voc:.1f} V")
        if isc < 0.1 or isc > 50:
            issues.append(f"Unreasonable Isc: {isc:.2f} A")

        return len(issues) == 0, issues


class PerformanceAnalyzer:
    """Analyzes PV module performance across multiple irradiance levels."""

    def __init__(self, module_area: float = 2.0):
        """Initialize performance analyzer.

        Args:
            module_area: Module area in m²
        """
        self.module_area = module_area

    def calculate_efficiency(
        self,
        pmax: float,
        irradiance: float
    ) -> float:
        """Calculate module efficiency.

        Args:
            pmax: Maximum power (W)
            irradiance: Irradiance level (W/m²)

        Returns:
            Efficiency (%)
        """
        if irradiance <= 0:
            return 0.0

        incident_power = irradiance * self.module_area
        efficiency = (pmax / incident_power) * 100

        return float(efficiency)

    def normalize_power(
        self,
        pmax: float,
        irradiance: float,
        target_irradiance: float = 1000.0
    ) -> float:
        """Normalize power to target irradiance (typically STC 1000 W/m²).

        Args:
            pmax: Measured maximum power (W)
            irradiance: Actual irradiance (W/m²)
            target_irradiance: Target irradiance for normalization (W/m²)

        Returns:
            Normalized power (W)
        """
        if irradiance <= 0:
            return 0.0

        return pmax * (target_irradiance / irradiance)

    def analyze_linearity(
        self,
        irradiances: List[float],
        powers: List[float]
    ) -> Dict[str, float]:
        """Analyze power linearity vs irradiance.

        Args:
            irradiances: List of irradiance levels (W/m²)
            powers: List of corresponding maximum powers (W)

        Returns:
            Dictionary with slope, intercept, r_squared, and linearity_coefficient
        """
        if len(irradiances) < 3:
            return {
                'slope': 0.0,
                'intercept': 0.0,
                'r_squared': 0.0,
                'linearity_coefficient': 0.0
            }

        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            irradiances, powers
        )

        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_value ** 2),
            'linearity_coefficient': float(slope),  # W/(W/m²)
            'p_value': float(p_value),
            'std_error': float(std_err)
        }

    def calculate_uniformity(
        self,
        measurements: List[float]
    ) -> Dict[str, float]:
        """Calculate spatial uniformity statistics.

        Args:
            measurements: List of measurements (e.g., irradiance at grid points)

        Returns:
            Dictionary with uniformity statistics
        """
        measurements_array = np.array(measurements)

        if len(measurements_array) == 0:
            return {
                'mean': 0.0,
                'std_dev': 0.0,
                'min': 0.0,
                'max': 0.0,
                'uniformity_percent': 0.0,
                'coefficient_of_variation': 0.0
            }

        mean = np.mean(measurements_array)
        std_dev = np.std(measurements_array)
        min_val = np.min(measurements_array)
        max_val = np.max(measurements_array)

        # Uniformity as percentage
        if mean > 0:
            uniformity_percent = (1 - (std_dev / mean)) * 100
            cv = (std_dev / mean) * 100
        else:
            uniformity_percent = 0.0
            cv = 0.0

        return {
            'mean': float(mean),
            'median': float(np.median(measurements_array)),
            'std_dev': float(std_dev),
            'min': float(min_val),
            'max': float(max_val),
            'range': float(max_val - min_val),
            'uniformity_percent': float(np.clip(uniformity_percent, 0, 100)),
            'coefficient_of_variation': float(cv)
        }


class PERF002Analyzer:
    """Specialized analyzer for PERF-002 protocol."""

    def __init__(self, module_area: float = 2.0):
        """Initialize PERF-002 analyzer.

        Args:
            module_area: Module area in m²
        """
        self.module_area = module_area
        self.performance_analyzer = PerformanceAnalyzer(module_area)
        self.expected_levels = [100, 200, 400, 600, 800, 1000, 1100]

    def analyze_test_run(
        self,
        measurements: List[Dict[str, Any]],
        iv_curves: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Perform complete analysis for PERF-002 test run.

        Args:
            measurements: List of measurement data points
            iv_curves: Optional list of I-V curve data

        Returns:
            Complete analysis results
        """
        # Group measurements by irradiance level
        by_irradiance = self._group_by_irradiance(measurements)

        # Analyze each irradiance level
        per_irradiance_results = []
        for irr_level in self.expected_levels:
            if irr_level not in by_irradiance:
                continue

            level_measurements = by_irradiance[irr_level]
            result = self._analyze_irradiance_level(irr_level, level_measurements)
            per_irradiance_results.append(result)

        # Overall analysis
        overall_results = self._analyze_overall(per_irradiance_results)

        return {
            'per_irradiance': per_irradiance_results,
            'overall': overall_results
        }

    def _group_by_irradiance(
        self,
        measurements: List[Dict[str, Any]]
    ) -> Dict[float, List[Dict[str, Any]]]:
        """Group measurements by target irradiance level."""
        grouped = {}
        for measurement in measurements:
            target_irr = measurement.get('target_irradiance')
            if target_irr is not None:
                if target_irr not in grouped:
                    grouped[target_irr] = []
                grouped[target_irr].append(measurement)
        return grouped

    def _analyze_irradiance_level(
        self,
        irradiance_level: float,
        measurements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze measurements for a single irradiance level."""
        # Extract values
        irradiances = [m['irradiance'] for m in measurements if 'irradiance' in m]
        voltages = [m['voltage'] for m in measurements if 'voltage' in m]
        currents = [m['current'] for m in measurements if 'current' in m]
        powers = [m.get('power', m.get('voltage', 0) * m.get('current', 0))
                  for m in measurements]
        temperatures = [m['module_temperature'] for m in measurements
                       if 'module_temperature' in m]

        # Basic statistics
        result = {
            'irradiance_level': irradiance_level,
            'measurement_count': len(measurements)
        }

        # Irradiance uniformity
        if irradiances:
            uniformity = self.performance_analyzer.calculate_uniformity(irradiances)
            result.update({
                'irradiance_mean': uniformity['mean'],
                'irradiance_std_dev': uniformity['std_dev'],
                'irradiance_uniformity': uniformity['uniformity_percent']
            })

        # Temperature statistics
        if temperatures:
            result.update({
                'temperature_mean': float(np.mean(temperatures)),
                'temperature_std_dev': float(np.std(temperatures))
            })

        # I-V curve analysis (if full curve available)
        if len(voltages) >= 10 and len(currents) >= 10:
            try:
                iv_analyzer = IVCurveAnalyzer(voltages, currents)

                pmax, vmp, imp = iv_analyzer.find_mpp()
                voc = iv_analyzer.find_voc()
                isc = iv_analyzer.find_isc()
                ff = iv_analyzer.calculate_fill_factor()

                result.update({
                    'pmax': pmax,
                    'vmp': vmp,
                    'imp': imp,
                    'voc': voc,
                    'isc': isc,
                    'fill_factor': ff * 100  # Convert to percentage
                })

                # Calculate efficiency
                if 'irradiance_mean' in result:
                    efficiency = self.performance_analyzer.calculate_efficiency(
                        pmax, result['irradiance_mean']
                    )
                    result['efficiency'] = efficiency

                # Validate I-V curve
                is_valid, issues = iv_analyzer.validate_curve()
                result['iv_curve_valid'] = is_valid
                if not is_valid:
                    result['iv_curve_issues'] = issues

            except Exception as e:
                result['analysis_error'] = str(e)
        else:
            # Use maximum power from measurements if I-V curve not available
            if powers:
                result['pmax'] = float(np.max(powers))

        # Normalize power to STC
        if 'pmax' in result and 'irradiance_mean' in result:
            normalized_pmax = self.performance_analyzer.normalize_power(
                result['pmax'], result['irradiance_mean']
            )
            result['normalized_pmax'] = normalized_pmax

        return result

    def _analyze_overall(
        self,
        per_irradiance_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform overall analysis across all irradiance levels."""
        if not per_irradiance_results:
            return {}

        # Extract data for linearity analysis
        irradiances = []
        powers = []
        for result in per_irradiance_results:
            if 'irradiance_mean' in result and 'pmax' in result:
                irradiances.append(result['irradiance_mean'])
                powers.append(result['pmax'])

        overall = {}

        # Linearity analysis
        if len(irradiances) >= 3:
            linearity = self.performance_analyzer.analyze_linearity(
                irradiances, powers
            )
            overall.update(linearity)

        # Summary statistics
        pmaxes = [r['pmax'] for r in per_irradiance_results if 'pmax' in r]
        efficiencies = [r['efficiency'] for r in per_irradiance_results
                       if 'efficiency' in r]
        fill_factors = [r['fill_factor'] for r in per_irradiance_results
                       if 'fill_factor' in r]

        if pmaxes:
            overall['pmax_mean'] = float(np.mean(pmaxes))
            overall['pmax_std_dev'] = float(np.std(pmaxes))

        if efficiencies:
            overall['efficiency_mean'] = float(np.mean(efficiencies))
            overall['efficiency_std_dev'] = float(np.std(efficiencies))

        if fill_factors:
            overall['fill_factor_mean'] = float(np.mean(fill_factors))
            overall['fill_factor_std_dev'] = float(np.std(fill_factors))

        # Data completeness
        overall['tested_irradiance_levels'] = len(per_irradiance_results)
        overall['expected_irradiance_levels'] = len(self.expected_levels)
        overall['completeness_percent'] = (
            len(per_irradiance_results) / len(self.expected_levels) * 100
        )

        return overall
