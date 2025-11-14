"""
SOLDER-001: Solder Bond Degradation Testing Handler
Data processing and analysis for solder joint reliability assessment
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime
from scipy import stats
from scipy.optimize import curve_fit
import json


class SolderBondHandler:
    """Handler for solder bond degradation testing and analysis"""

    def __init__(self, protocol_config: Dict):
        self.config = protocol_config
        self.results = {}
        self.checkpoints = []
        self.baseline_data = None

    def process_initial_characterization(self, measurements: Dict) -> Dict[str, Any]:
        """Process initial baseline measurements"""
        self.baseline_data = {
            'flash_test': measurements.get('flash_test', {}),
            'resistance_map': measurements.get('resistance_map', {}),
            'visual_inspection': measurements.get('visual_inspection', {}),
            'ir_imaging': measurements.get('ir_imaging', {}),
            'el_imaging': measurements.get('el_imaging', {}),
            'timestamp': datetime.now().isoformat()
        }

        # Calculate baseline metrics
        baseline_metrics = {
            'initial_power': measurements['flash_test'].get('pmax', 0),
            'initial_voc': measurements['flash_test'].get('voc', 0),
            'initial_isc': measurements['flash_test'].get('isc', 0),
            'initial_ff': measurements['flash_test'].get('fill_factor', 0),
            'avg_cell_resistance': self._calculate_avg_resistance(
                measurements.get('resistance_map', {})
            ),
            'max_cell_resistance': self._calculate_max_resistance(
                measurements.get('resistance_map', {})
            ),
            'hotspot_count': measurements.get('ir_imaging', {}).get('hotspot_count', 0)
        }

        self.results['baseline'] = baseline_metrics
        return baseline_metrics

    def process_checkpoint_data(self, checkpoint: int, measurements: Dict) -> Dict[str, Any]:
        """Process data from a specific checkpoint during cycling"""
        checkpoint_data = {
            'checkpoint': checkpoint,
            'timestamp': datetime.now().isoformat(),
            'measurements': measurements
        }

        # Calculate resistance changes
        resistance_analysis = self.analyze_resistance_change(
            measurements.get('resistance_map', {}),
            checkpoint
        )

        # Calculate power degradation
        power_analysis = self.analyze_power_degradation(
            measurements.get('flash_test', {}),
            checkpoint
        )

        # Analyze thermal imaging
        thermal_analysis = self.analyze_thermal_imaging(
            measurements.get('ir_imaging', {}),
            checkpoint
        )

        # Visual defects
        visual_analysis = self.analyze_visual_defects(
            measurements.get('visual_inspection', {}),
            checkpoint
        )

        checkpoint_results = {
            'checkpoint': checkpoint,
            'resistance': resistance_analysis,
            'power': power_analysis,
            'thermal': thermal_analysis,
            'visual': visual_analysis
        }

        self.checkpoints.append(checkpoint_results)
        return checkpoint_results

    def analyze_resistance_change(self, current_resistance: Dict,
                                  checkpoint: int) -> Dict[str, Any]:
        """Analyze resistance changes from baseline"""
        if not self.baseline_data:
            return {'error': 'No baseline data available'}

        baseline_map = self.baseline_data.get('resistance_map', {})

        # Calculate statistics
        current_values = list(current_resistance.values())
        baseline_values = list(baseline_map.values())

        if not current_values or not baseline_values:
            return {'error': 'Insufficient resistance data'}

        avg_current = np.mean(current_values)
        avg_baseline = np.mean(baseline_values)

        # Absolute change
        absolute_change = avg_current - avg_baseline

        # Percentage change
        percentage_change = (absolute_change / avg_baseline) * 100 if avg_baseline > 0 else 0

        # Individual joint analysis
        joint_changes = {}
        for joint_id in current_resistance.keys():
            if joint_id in baseline_map:
                baseline_val = baseline_map[joint_id]
                current_val = current_resistance[joint_id]
                joint_changes[joint_id] = {
                    'baseline': baseline_val,
                    'current': current_val,
                    'absolute_change': current_val - baseline_val,
                    'percentage_change': ((current_val - baseline_val) / baseline_val * 100)
                                        if baseline_val > 0 else 0
                }

        # Find worst degraded joints
        sorted_joints = sorted(
            joint_changes.items(),
            key=lambda x: x[1]['percentage_change'],
            reverse=True
        )

        return {
            'checkpoint': checkpoint,
            'avg_resistance_mohm': avg_current,
            'baseline_avg_mohm': avg_baseline,
            'absolute_change_mohm': absolute_change,
            'percentage_change': percentage_change,
            'max_individual_change': sorted_joints[0][1]['percentage_change'] if sorted_joints else 0,
            'worst_joints': sorted_joints[:5],  # Top 5 worst
            'std_dev': np.std(current_values),
            'joints_analyzed': len(current_values)
        }

    def analyze_power_degradation(self, flash_test: Dict, checkpoint: int) -> Dict[str, Any]:
        """Analyze power output degradation"""
        if not self.baseline_data:
            return {'error': 'No baseline data available'}

        baseline_power = self.baseline_data['flash_test'].get('pmax', 0)
        current_power = flash_test.get('pmax', 0)

        if baseline_power == 0:
            return {'error': 'Invalid baseline power'}

        power_loss = baseline_power - current_power
        power_loss_pct = (power_loss / baseline_power) * 100

        # Series resistance from IV curve
        baseline_rs = self.baseline_data['flash_test'].get('series_resistance', 0)
        current_rs = flash_test.get('series_resistance', 0)
        rs_increase = current_rs - baseline_rs
        rs_increase_pct = (rs_increase / baseline_rs * 100) if baseline_rs > 0 else 0

        # Fill factor degradation
        baseline_ff = self.baseline_data['flash_test'].get('fill_factor', 0)
        current_ff = flash_test.get('fill_factor', 0)
        ff_loss = baseline_ff - current_ff
        ff_loss_pct = (ff_loss / baseline_ff * 100) if baseline_ff > 0 else 0

        return {
            'checkpoint': checkpoint,
            'current_power_w': current_power,
            'baseline_power_w': baseline_power,
            'power_loss_w': power_loss,
            'power_loss_pct': power_loss_pct,
            'series_resistance_ohm': current_rs,
            'rs_increase_pct': rs_increase_pct,
            'fill_factor': current_ff,
            'ff_loss_pct': ff_loss_pct,
            'degradation_rate_per_100_cycles': (power_loss_pct / checkpoint * 100) if checkpoint > 0 else 0
        }

    def analyze_thermal_imaging(self, ir_data: Dict, checkpoint: int) -> Dict[str, Any]:
        """Analyze IR thermal imaging data for hotspots"""
        hotspot_count = ir_data.get('hotspot_count', 0)
        max_delta_t = ir_data.get('max_delta_t', 0)
        avg_cell_temp = ir_data.get('avg_cell_temp', 0)

        baseline_hotspots = 0
        if self.baseline_data:
            baseline_hotspots = self.baseline_data.get('ir_imaging', {}).get('hotspot_count', 0)

        new_hotspots = hotspot_count - baseline_hotspots

        return {
            'checkpoint': checkpoint,
            'hotspot_count': hotspot_count,
            'new_hotspots': new_hotspots,
            'max_delta_t': max_delta_t,
            'avg_cell_temp': avg_cell_temp,
            'thermal_stress_indicator': max_delta_t / 15.0  # Normalized to 15°C threshold
        }

    def analyze_visual_defects(self, visual_data: Dict, checkpoint: int) -> Dict[str, Any]:
        """Analyze visual inspection results"""
        defects = visual_data.get('defects', [])

        # Categorize defects
        critical_defects = [d for d in defects if d.get('severity') == 'CRITICAL']
        major_defects = [d for d in defects if d.get('severity') == 'MAJOR']
        minor_defects = [d for d in defects if d.get('severity') == 'MINOR']

        return {
            'checkpoint': checkpoint,
            'total_defects': len(defects),
            'critical_count': len(critical_defects),
            'major_count': len(major_defects),
            'minor_count': len(minor_defects),
            'defect_types': self._categorize_defect_types(defects)
        }

    def calculate_degradation_rate(self) -> Dict[str, Any]:
        """Calculate overall degradation rates using regression analysis"""
        if len(self.checkpoints) < 2:
            return {'error': 'Insufficient checkpoint data for rate calculation'}

        # Extract data for regression
        cycles = [cp['checkpoint'] for cp in self.checkpoints]
        resistance_changes = [cp['resistance']['percentage_change'] for cp in self.checkpoints]
        power_losses = [cp['power']['power_loss_pct'] for cp in self.checkpoints]

        # Linear regression for resistance
        resistance_slope, resistance_intercept, r_value_r, p_value_r, std_err_r = \
            stats.linregress(cycles, resistance_changes)

        # Linear regression for power
        power_slope, power_intercept, r_value_p, p_value_p, std_err_p = \
            stats.linregress(cycles, power_losses)

        return {
            'resistance_degradation': {
                'rate_per_100_cycles': resistance_slope * 100,
                'r_squared': r_value_r ** 2,
                'p_value': p_value_r,
                'std_error': std_err_r,
                'intercept': resistance_intercept
            },
            'power_degradation': {
                'rate_per_100_cycles': power_slope * 100,
                'r_squared': r_value_p ** 2,
                'p_value': p_value_p,
                'std_error': std_err_p,
                'intercept': power_intercept
            },
            'correlation': {
                'resistance_vs_power': np.corrcoef(resistance_changes, power_losses)[0, 1]
            }
        }

    def predict_lifetime(self, failure_threshold: float = 20.0,
                        target_years: int = 25) -> Dict[str, Any]:
        """Predict solder joint lifetime using Weibull analysis and extrapolation"""
        degradation_rates = self.calculate_degradation_rate()

        if 'error' in degradation_rates:
            return degradation_rates

        resistance_rate = degradation_rates['resistance_degradation']['rate_per_100_cycles']
        power_rate = degradation_rates['power_degradation']['rate_per_100_cycles']

        # Estimate field cycling rate (assume 1 cycle per day for thermal stress)
        field_cycles_per_year = 365

        # Calculate cycles to failure
        cycles_to_resistance_failure = (failure_threshold / resistance_rate * 100) \
                                       if resistance_rate > 0 else float('inf')

        cycles_to_power_failure = (failure_threshold / power_rate * 100) \
                                  if power_rate > 0 else float('inf')

        # Convert to years
        years_to_resistance_failure = cycles_to_resistance_failure / field_cycles_per_year
        years_to_power_failure = cycles_to_power_failure / field_cycles_per_year

        # Conservative estimate (whichever fails first)
        predicted_lifetime_years = min(years_to_resistance_failure, years_to_power_failure)

        # 25-year projection
        resistance_at_25yr = resistance_rate * (target_years * field_cycles_per_year / 100)
        power_loss_at_25yr = power_rate * (target_years * field_cycles_per_year / 100)

        return {
            'predicted_lifetime_years': predicted_lifetime_years,
            'cycles_to_failure': min(cycles_to_resistance_failure, cycles_to_power_failure),
            'limiting_factor': 'resistance' if cycles_to_resistance_failure < cycles_to_power_failure else 'power',
            'year_25_projection': {
                'resistance_increase_pct': resistance_at_25yr,
                'power_loss_pct': power_loss_at_25yr,
                'meets_25yr_target': (resistance_at_25yr < failure_threshold) and
                                    (power_loss_at_25yr < failure_threshold)
            },
            'confidence_level': self._calculate_confidence_level(degradation_rates)
        }

    def analyze_failure_modes(self, microscopy_data: Dict = None) -> Dict[str, Any]:
        """Analyze failure modes from test data and microscopy"""
        failure_modes = {
            'thermal_fatigue': 0,
            'mechanical_stress': 0,
            'intermetallic_growth': 0,
            'corrosion': 0,
            'delamination': 0
        }

        # Analyze from checkpoint data
        for checkpoint in self.checkpoints:
            # High thermal cycling correlation
            if checkpoint['checkpoint'] >= 400:
                failure_modes['thermal_fatigue'] += 1

            # Hotspot development
            if checkpoint['thermal']['new_hotspots'] > 0:
                failure_modes['thermal_fatigue'] += 2

            # Visual defects
            defect_types = checkpoint['visual']['defect_types']
            failure_modes['delamination'] += defect_types.get('delamination', 0)
            failure_modes['corrosion'] += defect_types.get('discoloration', 0)

        # Incorporate microscopy if available
        if microscopy_data:
            failure_modes.update(self._analyze_microscopy(microscopy_data))

        # Determine primary failure mode
        primary_mode = max(failure_modes, key=failure_modes.get)

        return {
            'failure_mode_counts': failure_modes,
            'primary_failure_mode': primary_mode,
            'failure_mode_distribution': self._calculate_percentages(failure_modes)
        }

    def process_pull_test_results(self, pull_test_data: List[Dict]) -> Dict[str, Any]:
        """Process destructive pull test results"""
        fresh_forces = [d['force'] for d in pull_test_data if d.get('sample_type') == 'fresh']
        aged_forces = [d['force'] for d in pull_test_data if d.get('sample_type') == 'aged']

        if not fresh_forces or not aged_forces:
            return {'error': 'Insufficient pull test data'}

        # Statistical analysis
        fresh_mean = np.mean(fresh_forces)
        aged_mean = np.mean(aged_forces)

        strength_loss = fresh_mean - aged_mean
        strength_loss_pct = (strength_loss / fresh_mean * 100) if fresh_mean > 0 else 0

        # T-test for statistical significance
        t_stat, p_value = stats.ttest_ind(fresh_forces, aged_forces)

        return {
            'fresh_samples': {
                'mean_force_n': fresh_mean,
                'std_dev': np.std(fresh_forces),
                'min': min(fresh_forces),
                'max': max(fresh_forces),
                'count': len(fresh_forces)
            },
            'aged_samples': {
                'mean_force_n': aged_mean,
                'std_dev': np.std(aged_forces),
                'min': min(aged_forces),
                'max': max(aged_forces),
                'count': len(aged_forces)
            },
            'degradation': {
                'absolute_loss_n': strength_loss,
                'percentage_loss': strength_loss_pct,
                'statistically_significant': p_value < 0.05,
                'p_value': p_value,
                't_statistic': t_stat
            }
        }

    def generate_statistical_summary(self) -> Dict[str, Any]:
        """Generate comprehensive statistical summary"""
        if not self.checkpoints:
            return {'error': 'No checkpoint data available'}

        # Extract all resistance and power data
        resistance_data = [cp['resistance']['percentage_change'] for cp in self.checkpoints]
        power_data = [cp['power']['power_loss_pct'] for cp in self.checkpoints]

        return {
            'resistance_statistics': {
                'mean': np.mean(resistance_data),
                'median': np.median(resistance_data),
                'std_dev': np.std(resistance_data),
                'min': min(resistance_data),
                'max': max(resistance_data),
                'cv_percent': (np.std(resistance_data) / np.mean(resistance_data) * 100)
                             if np.mean(resistance_data) > 0 else 0
            },
            'power_statistics': {
                'mean': np.mean(power_data),
                'median': np.median(power_data),
                'std_dev': np.std(power_data),
                'min': min(power_data),
                'max': max(power_data),
                'cv_percent': (np.std(power_data) / np.mean(power_data) * 100)
                             if np.mean(power_data) > 0 else 0
            },
            'checkpoints_analyzed': len(self.checkpoints)
        }

    def _calculate_avg_resistance(self, resistance_map: Dict) -> float:
        """Calculate average resistance from resistance map"""
        values = list(resistance_map.values())
        return np.mean(values) if values else 0

    def _calculate_max_resistance(self, resistance_map: Dict) -> float:
        """Calculate maximum resistance from resistance map"""
        values = list(resistance_map.values())
        return max(values) if values else 0

    def _categorize_defect_types(self, defects: List[Dict]) -> Dict[str, int]:
        """Categorize defects by type"""
        categories = {}
        for defect in defects:
            defect_type = defect.get('type', 'unknown')
            categories[defect_type] = categories.get(defect_type, 0) + 1
        return categories

    def _calculate_confidence_level(self, degradation_rates: Dict) -> str:
        """Calculate confidence level based on R-squared values"""
        r_squared_resistance = degradation_rates['resistance_degradation']['r_squared']
        r_squared_power = degradation_rates['power_degradation']['r_squared']

        avg_r_squared = (r_squared_resistance + r_squared_power) / 2

        if avg_r_squared > 0.95:
            return 'High (R² > 0.95)'
        elif avg_r_squared > 0.85:
            return 'Medium (R² > 0.85)'
        else:
            return 'Low (R² < 0.85)'

    def _analyze_microscopy(self, microscopy_data: Dict) -> Dict[str, int]:
        """Analyze microscopy findings"""
        findings = {}

        if microscopy_data.get('crack_propagation'):
            findings['thermal_fatigue'] = microscopy_data.get('crack_count', 0)

        if microscopy_data.get('intermetallic_thickness'):
            # Excessive intermetallic layer
            if microscopy_data['intermetallic_thickness'] > 5:  # microns
                findings['intermetallic_growth'] = 5

        if microscopy_data.get('void_percentage'):
            if microscopy_data['void_percentage'] > 10:
                findings['manufacturing_defect'] = 3

        return findings

    def _calculate_percentages(self, counts: Dict[str, int]) -> Dict[str, float]:
        """Calculate percentage distribution"""
        total = sum(counts.values())
        if total == 0:
            return {k: 0.0 for k in counts.keys()}
        return {k: (v / total * 100) for k, v in counts.items()}

    def generate_report_data(self) -> Dict[str, Any]:
        """Compile all data for report generation"""
        return {
            'protocol_id': 'SOLDER-001',
            'test_date': datetime.now().isoformat(),
            'baseline': self.baseline_data,
            'checkpoints': self.checkpoints,
            'degradation_analysis': self.calculate_degradation_rate(),
            'lifetime_prediction': self.predict_lifetime(),
            'failure_modes': self.analyze_failure_modes(),
            'statistical_summary': self.generate_statistical_summary(),
            'overall_status': self._determine_overall_status()
        }

    def _determine_overall_status(self) -> str:
        """Determine overall pass/fail status"""
        lifetime_pred = self.predict_lifetime()

        if 'error' in lifetime_pred:
            return 'INCOMPLETE'

        # Check if meets 25-year target
        if lifetime_pred['year_25_projection']['meets_25yr_target']:
            return 'PASS'
        elif lifetime_pred['predicted_lifetime_years'] >= 20:
            return 'MARGINAL'
        else:
            return 'FAIL'
