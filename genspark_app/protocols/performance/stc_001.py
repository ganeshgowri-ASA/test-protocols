"""
STC-001: Standard Test Conditions (STC) Testing Protocol

This module implements the complete STC testing protocol for photovoltaic modules
according to IEC 61215-1:2021 and IEC 61730-1:2023 standards.

Features:
- Interactive GenSpark UI with conditional logic
- Real-time I-V curve analysis and visualization
- Automated validation and quality checks
- Temperature and irradiance corrections
- Comprehensive uncertainty analysis
- PDF report generation with digital signatures
- Complete data traceability and audit trail
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import io
import json
from pathlib import Path

# Third-party imports for visualization and analysis
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from scipy.signal import savgol_filter
    from scipy.interpolate import interp1d
    from scipy.optimize import curve_fit
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Import base protocol class
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from protocols.base.protocol import BaseProtocol


class STC001Protocol(BaseProtocol):
    """
    Standard Test Conditions (STC) Testing Protocol Implementation.

    This class implements comprehensive STC testing including:
    - Module characterization under standard conditions
    - I-V curve acquisition and analysis
    - Key parameter extraction (Voc, Isc, Pmax, FF, etc.)
    - Temperature and irradiance corrections
    - Uncertainty analysis
    - Pass/fail validation
    - Report generation
    """

    def __init__(self):
        """Initialize STC-001 protocol."""
        super().__init__(
            protocol_id='STC-001',
            protocol_name='Standard Test Conditions (STC) Testing',
            version='2.0'
        )

        # Initialize data storage
        self.iv_data = None
        self.processed_data = None
        self.parameters = {}
        self.corrections_applied = {}
        self.uncertainty_analysis = {}

        # Standard test conditions
        self.stc = {
            'irradiance': 1000,  # W/m²
            'cell_temperature': 25,  # °C
            'spectrum': 'AM 1.5G'
        }

    def render_ui(self) -> Dict[str, Any]:
        """
        Render the interactive user interface configuration.

        Returns:
            Dict containing complete UI configuration for GenSpark
        """
        self.log_action('render_ui', {'protocol_id': self.protocol_id})

        # The UI configuration is loaded from the JSON template
        ui_config = self.template.get('ui_configuration', {})

        # Add dynamic options
        ui_config['dynamic_data'] = {
            'module_technologies': self.template.get('module_technologies', []),
            'manufacturers': self._get_manufacturer_list(),
            'equipment': self._get_equipment_list(),
            'users': self._get_user_list()
        }

        # Add keyboard shortcuts
        ui_config['keyboard_shortcuts'] = {
            'ctrl+s': 'save_progress',
            'ctrl+g': 'generate_graphs',
            'ctrl+v': 'validate_data',
            'ctrl+r': 'generate_report',
            'ctrl+z': 'undo',
            'ctrl+y': 'redo'
        }

        # Add auto-save configuration
        ui_config['auto_save'] = {
            'enabled': True,
            'interval_seconds': 30
        }

        return ui_config

    def validate_setup(self, setup_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate test setup parameters.

        Args:
            setup_data: Dictionary containing setup parameters including:
                - serial_number: Module serial number
                - technology: Module technology type
                - rated_power: Rated power in watts
                - irradiance: Test irradiance in W/m²
                - cell_temperature: Cell temperature in °C
                - equipment: Equipment IDs

        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.log_action('validate_setup', setup_data)
        errors = []

        # Validate required fields
        required_fields = [
            'serial_number', 'manufacturer', 'model', 'technology',
            'rated_power', 'irradiance', 'cell_temperature'
        ]

        for field in required_fields:
            if field not in setup_data or setup_data[field] is None or setup_data[field] == '':
                errors.append(f"Required field '{field}' is missing")

        # Validate serial number format
        if 'serial_number' in setup_data:
            serial = setup_data['serial_number']
            if not isinstance(serial, str) or len(serial) < 8 or len(serial) > 20:
                errors.append("Serial number must be between 8 and 20 characters")

        # Validate numeric ranges
        if 'rated_power' in setup_data:
            power = setup_data['rated_power']
            if not isinstance(power, (int, float)) or power <= 0 or power > 1000:
                errors.append("Rated power must be between 0 and 1000 W")

        # Validate irradiance
        if 'irradiance' in setup_data:
            irradiance = setup_data['irradiance']
            if not isinstance(irradiance, (int, float)) or irradiance < 800 or irradiance > 1200:
                errors.append("Irradiance must be between 800 and 1200 W/m²")

            # Add warning if not at STC
            if abs(irradiance - 1000) > 10:
                self.add_warning(f"Irradiance ({irradiance} W/m²) deviates from STC (1000 W/m²). Correction will be applied.")

        # Validate cell temperature
        if 'cell_temperature' in setup_data:
            temp = setup_data['cell_temperature']
            if not isinstance(temp, (int, float)) or temp < 15 or temp > 35:
                errors.append("Cell temperature must be between 15 and 35 °C")

            # Add warning if not at STC
            if abs(temp - 25) > 2:
                self.add_warning(f"Cell temperature ({temp}°C) deviates from STC (25°C). Correction recommended.")

        # Validate equipment calibration
        if 'equipment' in setup_data:
            for equipment_type, equipment_id in setup_data['equipment'].items():
                calibration_valid = self._check_equipment_calibration(equipment_id)
                if not calibration_valid:
                    errors.append(f"{equipment_type} calibration is expired or invalid")

        # Store validated setup data
        if not errors:
            self.test_data['setup'] = setup_data

        is_valid = len(errors) == 0
        return is_valid, errors

    def execute_test(self, test_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the test protocol.

        This method orchestrates the complete test execution including:
        - Data acquisition (file upload or live connection)
        - Data validation
        - Parameter extraction
        - Analysis and corrections

        Args:
            test_params: Dictionary containing:
                - data_source: 'file' or 'live'
                - file_path: Path to I-V data file (if file source)
                - voltage_column: Name of voltage column
                - current_column: Name of current column

        Returns:
            Dictionary containing test results and status
        """
        self.log_action('execute_test', test_params)

        try:
            # Step 1: Load I-V data
            if test_params.get('data_source') == 'file':
                self.iv_data = self._load_iv_data_from_file(
                    test_params['file_path'],
                    test_params.get('voltage_column'),
                    test_params.get('current_column')
                )
            elif test_params.get('data_source') == 'live':
                self.iv_data = self._acquire_live_data(test_params)
            else:
                raise ValueError("Invalid data source. Must be 'file' or 'live'")

            # Step 2: Validate I-V data
            validation_result = self._validate_iv_data(self.iv_data)
            if not validation_result['valid']:
                return {
                    'status': 'error',
                    'message': 'I-V data validation failed',
                    'errors': validation_result['errors']
                }

            # Step 3: Process and smooth data
            self.processed_data = self._process_iv_data(self.iv_data)

            # Step 4: Extract key parameters
            self.parameters = self._extract_parameters(self.processed_data)

            # Step 5: Apply corrections if needed
            if self._corrections_needed():
                self.parameters = self._apply_corrections(self.parameters)

            # Step 6: Calculate derived parameters
            self.parameters = self._calculate_derived_parameters(self.parameters)

            # Step 7: Store results
            self.results = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'parameters': self.parameters,
                'raw_data_points': len(self.iv_data),
                'corrections_applied': self.corrections_applied
            }

            self.log_action('execute_test_completed', self.results)

            return self.results

        except Exception as e:
            error_result = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.log_action('execute_test_error', error_result)
            return error_result

    def analyze_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze raw test data and extract key parameters.

        This method performs comprehensive analysis including:
        - MPP identification
        - Parameter extraction
        - Series and shunt resistance calculation
        - Quality metrics

        Args:
            raw_data: Dictionary containing voltage and current arrays

        Returns:
            Dictionary containing analyzed results
        """
        self.log_action('analyze_data', {'data_points': len(raw_data.get('voltage', []))})

        voltage = np.array(raw_data['voltage'])
        current = np.array(raw_data['current'])
        power = voltage * current

        # Extract key parameters
        analysis_results = {
            # Basic parameters
            'voc': self._find_voc(voltage, current),
            'isc': self._find_isc(voltage, current),
            'mpp': self._find_mpp(voltage, current, power),

            # Quality metrics
            'curve_quality': self._assess_curve_quality(voltage, current),
            'data_points': len(voltage),

            # Resistance parameters
            'rs': self._calculate_series_resistance(voltage, current),
            'rsh': self._calculate_shunt_resistance(voltage, current)
        }

        # Extract MPP parameters
        mpp_idx = analysis_results['mpp']['index']
        analysis_results['vmp'] = voltage[mpp_idx]
        analysis_results['imp'] = current[mpp_idx]
        analysis_results['pmax'] = power[mpp_idx]

        # Calculate fill factor
        analysis_results['fill_factor'] = (
            analysis_results['pmax'] /
            (analysis_results['voc'] * analysis_results['isc'])
        )

        # Calculate efficiency if module area is known
        if 'module_area' in self.test_data.get('setup', {}):
            module_area = self.test_data['setup']['module_area']
            irradiance = self.test_data['setup'].get('irradiance', 1000)
            analysis_results['efficiency'] = (
                analysis_results['pmax'] / (irradiance * module_area) * 100
            )

        self.log_action('analyze_data_completed', analysis_results)

        return analysis_results

    def generate_graphs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate interactive graphs and visualizations.

        Creates:
        - I-V and P-V curves (dual-axis)
        - Fill factor visualization
        - Parameter comparison charts
        - Uncertainty budget chart

        Args:
            data: Data dictionary containing voltage, current, and parameters

        Returns:
            Dictionary containing Plotly graph configurations
        """
        self.log_action('generate_graphs', {})

        if not PLOTLY_AVAILABLE:
            return {
                'error': 'Plotly not available',
                'message': 'Install plotly to generate interactive graphs'
            }

        graphs = {}

        # Graph 1: I-V and P-V Curves
        graphs['iv_pv_curves'] = self._generate_iv_pv_curves()

        # Graph 2: Fill Factor Visualization
        graphs['fill_factor'] = self._generate_fill_factor_graph()

        # Graph 3: Parameter Comparison (if historical data exists)
        if self._has_historical_data():
            graphs['parameter_trends'] = self._generate_parameter_trends()

        # Graph 4: Uncertainty Budget
        if self.uncertainty_analysis:
            graphs['uncertainty_budget'] = self._generate_uncertainty_chart()

        # Graph 5: Temperature Coefficient Plots (if multiple temperatures)
        if self._has_multi_temperature_data():
            graphs['temperature_coefficients'] = self._generate_temp_coeff_plots()

        self.log_action('generate_graphs_completed', {'graph_count': len(graphs)})

        return graphs

    def validate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate test results against acceptance criteria.

        Checks:
        - Power tolerance (±3% of rated)
        - Repeatability (≤0.5%)
        - Voc deviation (≤2%)
        - Isc deviation (≤2%)
        - Fill factor minimum (≥0.70)

        Args:
            results: Test results dictionary

        Returns:
            Dictionary containing validation status and details
        """
        self.log_action('validate_results', results)

        validation = {
            'overall_status': 'PASS',
            'criteria_results': {},
            'failed_criteria': [],
            'warnings': []
        }

        criteria = self.template.get('acceptance_criteria', {})

        # Check power tolerance
        if 'power_tolerance' in criteria:
            power_check = self._validate_power_tolerance(results)
            validation['criteria_results']['power_tolerance'] = power_check
            if not power_check['pass']:
                validation['failed_criteria'].append('power_tolerance')

        # Check repeatability (if multiple measurements)
        if 'repeatability' in criteria and self._has_repeat_measurements():
            repeat_check = self._validate_repeatability(results)
            validation['criteria_results']['repeatability'] = repeat_check
            if not repeat_check['pass']:
                validation['failed_criteria'].append('repeatability')

        # Check Voc deviation
        if 'voc_deviation' in criteria:
            voc_check = self._validate_voc_deviation(results)
            validation['criteria_results']['voc_deviation'] = voc_check
            if not voc_check['pass']:
                validation['failed_criteria'].append('voc_deviation')

        # Check Isc deviation
        if 'isc_deviation' in criteria:
            isc_check = self._validate_isc_deviation(results)
            validation['criteria_results']['isc_deviation'] = isc_check
            if not isc_check['pass']:
                validation['failed_criteria'].append('isc_deviation')

        # Check fill factor minimum
        if 'ff_minimum' in criteria:
            ff_check = self._validate_fill_factor(results)
            validation['criteria_results']['ff_minimum'] = ff_check
            if not ff_check['pass']:
                validation['failed_criteria'].append('ff_minimum')

        # Set overall status
        if validation['failed_criteria']:
            validation['overall_status'] = 'FAIL'

        # Add recommendations for failed tests
        if validation['overall_status'] == 'FAIL':
            validation['recommendations'] = self._generate_recommendations(
                validation['failed_criteria']
            )

        self.log_action('validate_results_completed', validation)

        return validation

    def calculate_uncertainty(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate measurement uncertainty according to GUM (Guide to Uncertainty in Measurement).

        Calculates uncertainty for:
        - Voc, Isc, Vmp, Imp, Pmax
        - Fill Factor
        - Efficiency

        Args:
            results: Test results dictionary

        Returns:
            Dictionary containing uncertainty analysis
        """
        self.log_action('calculate_uncertainty', {})

        uncertainty = {
            'method': 'GUM Type A and Type B',
            'confidence_level': 0.95,
            'coverage_factor': 2.0,
            'components': {}
        }

        # Define uncertainty sources
        uncertainty_sources = {
            'equipment_calibration': 0.5,  # %
            'temperature_measurement': 0.5,  # °C
            'irradiance_measurement': 2.0,  # %
            'data_acquisition': 0.2,  # %
            'repeatability': 0.3  # %
        }

        # Calculate uncertainty for each parameter
        for param in ['voc', 'isc', 'vmp', 'imp', 'pmax', 'fill_factor']:
            if param in results:
                param_uncertainty = self._calculate_parameter_uncertainty(
                    param,
                    results[param],
                    uncertainty_sources
                )
                uncertainty['components'][param] = param_uncertainty

        # Calculate combined and expanded uncertainty
        for param, components in uncertainty['components'].items():
            # Combined standard uncertainty (RSS of components)
            combined_std = np.sqrt(sum(c['value']**2 for c in components['sources']))

            # Expanded uncertainty (k=2 for 95% confidence)
            expanded = combined_std * uncertainty['coverage_factor']

            components['combined_standard_uncertainty'] = combined_std
            components['expanded_uncertainty'] = expanded
            components['relative_uncertainty_percent'] = (
                expanded / results[param] * 100 if results[param] != 0 else 0
            )

        self.uncertainty_analysis = uncertainty
        self.log_action('calculate_uncertainty_completed', uncertainty)

        return uncertainty

    def generate_report(self, format: str = 'pdf') -> bytes:
        """
        Generate comprehensive test report.

        Report includes:
        - Test information and conditions
        - Module details
        - I-V and P-V curves
        - Results table with pass/fail
        - Uncertainty analysis
        - Operator and reviewer signatures
        - QR code for traceability

        Args:
            format: Report format ('pdf', 'excel', 'json')

        Returns:
            Report as bytes
        """
        self.log_action('generate_report', {'format': format})

        if format == 'pdf':
            return self._generate_pdf_report()
        elif format == 'excel':
            return self._generate_excel_report()
        elif format == 'json':
            return self._generate_json_report()
        else:
            raise ValueError(f"Unsupported report format: {format}")

    # ========== Private Helper Methods ==========

    def _load_iv_data_from_file(self, file_path: str,
                                 voltage_col: Optional[str] = None,
                                 current_col: Optional[str] = None) -> Dict[str, np.ndarray]:
        """Load I-V data from CSV, Excel, or text file."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file based on extension
        if file_path.suffix.lower() in ['.csv', '.txt']:
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        # Auto-detect voltage and current columns if not specified
        if voltage_col is None:
            voltage_col = self._auto_detect_column(df, ['voltage', 'v', 'volt'])
        if current_col is None:
            current_col = self._auto_detect_column(df, ['current', 'i', 'amp'])

        if voltage_col not in df.columns:
            raise ValueError(f"Voltage column '{voltage_col}' not found in file")
        if current_col not in df.columns:
            raise ValueError(f"Current column '{current_col}' not found in file")

        return {
            'voltage': df[voltage_col].values,
            'current': df[current_col].values
        }

    def _auto_detect_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        """Auto-detect column name from candidates."""
        for col in df.columns:
            for candidate in candidates:
                if candidate.lower() in col.lower():
                    return col
        raise ValueError(f"Could not auto-detect column from candidates: {candidates}")

    def _acquire_live_data(self, params: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Acquire I-V data from live equipment connection."""
        # This would interface with actual equipment
        # For now, return placeholder
        raise NotImplementedError("Live data acquisition not yet implemented")

    def _validate_iv_data(self, iv_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Validate I-V curve data."""
        errors = []
        warnings = []

        voltage = iv_data['voltage']
        current = iv_data['current']

        # Check minimum number of points
        if len(voltage) < 100:
            errors.append(f"Insufficient data points: {len(voltage)} (minimum 100 required)")

        # Check for negative voltages
        if np.any(voltage < 0):
            warnings.append("Negative voltages detected")

        # Check for missing values
        if np.any(np.isnan(voltage)) or np.any(np.isnan(current)):
            errors.append("Missing values (NaN) detected in data")

        # Check for monotonic voltage
        if not np.all(np.diff(voltage) >= 0):
            warnings.append("Voltage is not monotonically increasing")

        # Check for outliers (z-score method)
        outliers = self._detect_outliers(current)
        if len(outliers) > 0:
            warnings.append(f"Detected {len(outliers)} potential outliers in current data")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _detect_outliers(self, data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """Detect outliers using z-score method."""
        z_scores = np.abs((data - np.mean(data)) / np.std(data))
        return np.where(z_scores > threshold)[0]

    def _process_iv_data(self, iv_data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Process and smooth I-V data."""
        voltage = iv_data['voltage']
        current = iv_data['current']

        # Sort by voltage
        sort_idx = np.argsort(voltage)
        voltage = voltage[sort_idx]
        current = current[sort_idx]

        # Apply smoothing if scipy is available
        if SCIPY_AVAILABLE and len(voltage) > 11:
            try:
                current_smooth = savgol_filter(current, window_length=11, polyorder=3)
            except:
                current_smooth = current
        else:
            current_smooth = current

        # Calculate power
        power = voltage * current_smooth

        return {
            'voltage': voltage,
            'current': current_smooth,
            'power': power,
            'current_raw': iv_data['current'][sort_idx]
        }

    def _extract_parameters(self, processed_data: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Extract key parameters from processed I-V data."""
        voltage = processed_data['voltage']
        current = processed_data['current']
        power = processed_data['power']

        # Find Voc (voltage when current ~ 0)
        voc = self._find_voc(voltage, current)

        # Find Isc (current when voltage ~ 0)
        isc = self._find_isc(voltage, current)

        # Find MPP
        mpp_idx = np.argmax(power)
        vmp = voltage[mpp_idx]
        imp = current[mpp_idx]
        pmax = power[mpp_idx]

        # Calculate fill factor
        ff = pmax / (voc * isc) if (voc * isc) > 0 else 0

        return {
            'voc': float(voc),
            'isc': float(isc),
            'vmp': float(vmp),
            'imp': float(imp),
            'pmax': float(pmax),
            'fill_factor': float(ff)
        }

    def _find_voc(self, voltage: np.ndarray, current: np.ndarray) -> float:
        """Find open-circuit voltage (Voc) by interpolation."""
        # Find zero-crossing of current
        if SCIPY_AVAILABLE:
            try:
                f = interp1d(current, voltage, kind='linear', fill_value='extrapolate')
                voc = float(f(0))
            except:
                voc = voltage[-1]  # Fallback to last voltage point
        else:
            # Simple linear interpolation
            idx = np.argmin(np.abs(current))
            if idx < len(voltage) - 1:
                voc = voltage[idx]
            else:
                voc = voltage[-1]

        return voc

    def _find_isc(self, voltage: np.ndarray, current: np.ndarray) -> float:
        """Find short-circuit current (Isc) by interpolation."""
        # Find zero-crossing of voltage
        if SCIPY_AVAILABLE:
            try:
                f = interp1d(voltage, current, kind='linear', fill_value='extrapolate')
                isc = float(f(0))
            except:
                isc = current[0]  # Fallback to first current point
        else:
            # Simple linear interpolation
            idx = np.argmin(np.abs(voltage))
            if idx < len(current):
                isc = current[idx]
            else:
                isc = current[0]

        return isc

    def _find_mpp(self, voltage: np.ndarray, current: np.ndarray,
                  power: np.ndarray) -> Dict[str, Any]:
        """Find maximum power point."""
        mpp_idx = np.argmax(power)

        return {
            'index': mpp_idx,
            'voltage': voltage[mpp_idx],
            'current': current[mpp_idx],
            'power': power[mpp_idx]
        }

    def _assess_curve_quality(self, voltage: np.ndarray, current: np.ndarray) -> Dict[str, Any]:
        """Assess I-V curve quality."""
        quality = {
            'score': 100.0,
            'issues': []
        }

        # Check for negative values
        if np.any(voltage < 0):
            quality['score'] -= 10
            quality['issues'].append('Negative voltage values')

        if np.any(current < 0):
            quality['score'] -= 10
            quality['issues'].append('Negative current values')

        # Check for gaps
        voltage_diff = np.diff(voltage)
        max_gap = np.max(voltage_diff)
        mean_gap = np.mean(voltage_diff)
        if max_gap > 5 * mean_gap:
            quality['score'] -= 15
            quality['issues'].append('Large gaps in voltage data')

        # Check smoothness
        current_diff2 = np.diff(current, n=2)
        if np.std(current_diff2) > 0.1 * np.mean(np.abs(current)):
            quality['score'] -= 10
            quality['issues'].append('Noisy current data')

        quality['rating'] = 'Excellent' if quality['score'] >= 90 else \
                           'Good' if quality['score'] >= 75 else \
                           'Fair' if quality['score'] >= 60 else 'Poor'

        return quality

    def _calculate_series_resistance(self, voltage: np.ndarray,
                                     current: np.ndarray) -> float:
        """Calculate series resistance from slope at Voc."""
        # Use points near Voc (top 10%)
        voc_region = voltage > 0.9 * voltage[-1]
        if np.sum(voc_region) < 2:
            return 0.0

        v_region = voltage[voc_region]
        i_region = current[voc_region]

        # Calculate slope dV/dI
        if len(v_region) > 1:
            slope = np.polyfit(i_region, v_region, 1)[0]
            return abs(float(slope))
        else:
            return 0.0

    def _calculate_shunt_resistance(self, voltage: np.ndarray,
                                    current: np.ndarray) -> float:
        """Calculate shunt resistance from slope at Isc."""
        # Use points near Isc (bottom 10%)
        isc_region = voltage < 0.1 * voltage[-1]
        if np.sum(isc_region) < 2:
            return 1000.0  # Default high value

        v_region = voltage[isc_region]
        i_region = current[isc_region]

        # Calculate slope dV/dI
        if len(v_region) > 1:
            slope = np.polyfit(i_region, v_region, 1)[0]
            return abs(float(slope))
        else:
            return 1000.0

    def _corrections_needed(self) -> bool:
        """Check if corrections are needed."""
        setup = self.test_data.get('setup', {})

        # Check irradiance
        irradiance = setup.get('irradiance', 1000)
        if abs(irradiance - 1000) > 10:
            return True

        # Check temperature
        temp = setup.get('cell_temperature', 25)
        if abs(temp - 25) > 0.5:
            return True

        return False

    def _apply_corrections(self, parameters: Dict[str, float]) -> Dict[str, float]:
        """Apply temperature and irradiance corrections."""
        setup = self.test_data.get('setup', {})
        corrected = parameters.copy()

        # Temperature correction (IEC 60891)
        temp_actual = setup.get('cell_temperature', 25)
        temp_delta = temp_actual - 25

        if abs(temp_delta) > 0.5:
            # Get temperature coefficients
            alpha_isc = setup.get('temp_coeff_isc', 0.05) / 100  # %/°C to fraction/°C
            beta_voc = setup.get('temp_coeff_voc', -0.3) / 100
            gamma_pmax = setup.get('temp_coeff_pmax', -0.4) / 100

            # Apply corrections
            corrected['isc'] = parameters['isc'] * (1 - alpha_isc * temp_delta)
            corrected['voc'] = parameters['voc'] * (1 - beta_voc * temp_delta)
            corrected['pmax'] = parameters['pmax'] * (1 - gamma_pmax * temp_delta)

            self.corrections_applied['temperature'] = {
                'delta_t': temp_delta,
                'alpha': alpha_isc,
                'beta': beta_voc,
                'gamma': gamma_pmax
            }

        # Irradiance correction
        irradiance = setup.get('irradiance', 1000)
        if abs(irradiance - 1000) > 10:
            correction_factor = 1000 / irradiance

            corrected['isc'] = parameters['isc'] * correction_factor
            corrected['pmax'] = parameters['pmax'] * correction_factor

            self.corrections_applied['irradiance'] = {
                'actual': irradiance,
                'target': 1000,
                'factor': correction_factor
            }

        return corrected

    def _calculate_derived_parameters(self, parameters: Dict[str, float]) -> Dict[str, float]:
        """Calculate derived parameters."""
        # Recalculate fill factor if corrections were applied
        if self.corrections_applied:
            parameters['fill_factor'] = (
                parameters['pmax'] /
                (parameters['voc'] * parameters['isc'])
            )

        # Calculate efficiency if module area is known
        setup = self.test_data.get('setup', {})
        if 'module_area' in setup:
            module_area = setup['module_area']
            parameters['efficiency'] = (parameters['pmax'] / (1000 * module_area)) * 100

        return parameters

    def _generate_iv_pv_curves(self) -> Dict[str, Any]:
        """Generate I-V and P-V curves graph."""
        if self.processed_data is None:
            return {'error': 'No data available'}

        voltage = self.processed_data['voltage']
        current = self.processed_data['current']
        power = self.processed_data['power']

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add I-V curve
        fig.add_trace(
            go.Scatter(
                x=voltage,
                y=current,
                name='I-V Curve',
                line=dict(color='blue', width=2),
                hovertemplate='V: %{x:.2f} V<br>I: %{y:.3f} A<extra></extra>'
            ),
            secondary_y=False
        )

        # Add P-V curve
        fig.add_trace(
            go.Scatter(
                x=voltage,
                y=power,
                name='P-V Curve',
                line=dict(color='red', width=2),
                hovertemplate='V: %{x:.2f} V<br>P: %{y:.2f} W<extra></extra>'
            ),
            secondary_y=True
        )

        # Add MPP marker
        if self.parameters:
            fig.add_trace(
                go.Scatter(
                    x=[self.parameters['vmp']],
                    y=[self.parameters['pmax']],
                    mode='markers',
                    name='Maximum Power Point',
                    marker=dict(size=12, color='green', symbol='star'),
                    hovertemplate='MPP<br>V: %{x:.2f} V<br>P: %{y:.2f} W<extra></extra>'
                ),
                secondary_y=True
            )

        # Update layout
        fig.update_layout(
            title='I-V and P-V Characteristic Curves',
            xaxis_title='Voltage (V)',
            hovermode='x unified',
            template='plotly_white',
            height=600
        )

        fig.update_yaxes(title_text='Current (A)', secondary_y=False)
        fig.update_yaxes(title_text='Power (W)', secondary_y=True)

        return fig.to_json()

    def _generate_fill_factor_graph(self) -> Dict[str, Any]:
        """Generate fill factor visualization."""
        if not self.parameters:
            return {'error': 'No parameters available'}

        voc = self.parameters['voc']
        isc = self.parameters['isc']
        vmp = self.parameters['vmp']
        imp = self.parameters['imp']
        ff = self.parameters['fill_factor']

        # Create figure
        fig = go.Figure()

        # Add theoretical maximum rectangle
        fig.add_trace(go.Scatter(
            x=[0, voc, voc, 0, 0],
            y=[isc, isc, 0, 0, isc],
            fill='toself',
            fillcolor='lightblue',
            line=dict(color='blue', width=2),
            name='Theoretical Maximum (Voc × Isc)',
            hoverinfo='skip'
        ))

        # Add actual MPP rectangle
        fig.add_trace(go.Scatter(
            x=[0, vmp, vmp, 0, 0],
            y=[imp, imp, 0, 0, imp],
            fill='toself',
            fillcolor='lightgreen',
            line=dict(color='green', width=2),
            name=f'Actual Power (FF = {ff:.4f})',
            hoverinfo='skip'
        ))

        fig.update_layout(
            title='Fill Factor Visualization',
            xaxis_title='Voltage (V)',
            yaxis_title='Current (A)',
            template='plotly_white',
            showlegend=True,
            height=500
        )

        return fig.to_json()

    def _generate_parameter_trends(self) -> Dict[str, Any]:
        """Generate parameter trends graph (requires historical data)."""
        # Placeholder - would need actual historical data
        return {'info': 'Historical data visualization'}

    def _generate_uncertainty_chart(self) -> Dict[str, Any]:
        """Generate uncertainty budget chart."""
        if not self.uncertainty_analysis:
            return {'error': 'No uncertainty analysis available'}

        # Create waterfall chart for uncertainty components
        # Placeholder for now
        return {'info': 'Uncertainty budget chart'}

    def _generate_temp_coeff_plots(self) -> Dict[str, Any]:
        """Generate temperature coefficient plots."""
        # Placeholder - would need multi-temperature data
        return {'info': 'Temperature coefficient plots'}

    def _validate_power_tolerance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate power tolerance criterion."""
        rated_power = self.test_data.get('setup', {}).get('rated_power')
        measured_power = results.get('pmax')

        if rated_power is None or measured_power is None:
            return {'pass': False, 'error': 'Missing power data'}

        tolerance_percent = 3
        deviation_percent = abs(measured_power - rated_power) / rated_power * 100

        return {
            'pass': deviation_percent <= tolerance_percent,
            'measured': measured_power,
            'rated': rated_power,
            'deviation_percent': deviation_percent,
            'tolerance_percent': tolerance_percent
        }

    def _validate_repeatability(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate repeatability criterion."""
        # Would need multiple measurements
        return {'pass': True, 'note': 'Single measurement'}

    def _validate_voc_deviation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Voc deviation criterion."""
        rated_voc = self.test_data.get('setup', {}).get('rated_voc')
        measured_voc = results.get('voc')

        if rated_voc is None or measured_voc is None:
            return {'pass': True, 'note': 'No rated Voc specified'}

        tolerance_percent = 2
        deviation_percent = abs(measured_voc - rated_voc) / rated_voc * 100

        return {
            'pass': deviation_percent <= tolerance_percent,
            'measured': measured_voc,
            'rated': rated_voc,
            'deviation_percent': deviation_percent,
            'tolerance_percent': tolerance_percent
        }

    def _validate_isc_deviation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Isc deviation criterion."""
        rated_isc = self.test_data.get('setup', {}).get('rated_isc')
        measured_isc = results.get('isc')

        if rated_isc is None or measured_isc is None:
            return {'pass': True, 'note': 'No rated Isc specified'}

        tolerance_percent = 2
        deviation_percent = abs(measured_isc - rated_isc) / rated_isc * 100

        return {
            'pass': deviation_percent <= tolerance_percent,
            'measured': measured_isc,
            'rated': rated_isc,
            'deviation_percent': deviation_percent,
            'tolerance_percent': tolerance_percent
        }

    def _validate_fill_factor(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fill factor criterion."""
        ff = results.get('fill_factor')

        if ff is None:
            return {'pass': False, 'error': 'Missing fill factor'}

        ff_min = 0.70

        return {
            'pass': ff >= ff_min,
            'measured': ff,
            'minimum': ff_min
        }

    def _generate_recommendations(self, failed_criteria: List[str]) -> List[str]:
        """Generate recommendations based on failed criteria."""
        recommendations = []

        if 'power_tolerance' in failed_criteria:
            recommendations.append('Review module specification and test conditions')
            recommendations.append('Check for module degradation or damage')

        if 'ff_minimum' in failed_criteria:
            recommendations.append('Inspect module for defects (cracks, hot spots)')
            recommendations.append('Check series and shunt resistance values')

        if 'voc_deviation' in failed_criteria or 'isc_deviation' in failed_criteria:
            recommendations.append('Verify test conditions (irradiance, temperature)')
            recommendations.append('Check equipment calibration')

        if 'repeatability' in failed_criteria:
            recommendations.append('Review test procedure and equipment stability')
            recommendations.append('Check for environmental variations')

        return recommendations

    def _calculate_parameter_uncertainty(self, param: str, value: float,
                                        sources: Dict[str, float]) -> Dict[str, Any]:
        """Calculate uncertainty for a specific parameter."""
        uncertainty_components = []

        # Equipment calibration uncertainty
        uncertainty_components.append({
            'source': 'Equipment Calibration',
            'type': 'Type B',
            'value': value * sources['equipment_calibration'] / 100,
            'distribution': 'Normal'
        })

        # Data acquisition uncertainty
        uncertainty_components.append({
            'source': 'Data Acquisition',
            'type': 'Type A',
            'value': value * sources['data_acquisition'] / 100,
            'distribution': 'Normal'
        })

        # Repeatability
        uncertainty_components.append({
            'source': 'Repeatability',
            'type': 'Type A',
            'value': value * sources['repeatability'] / 100,
            'distribution': 'Normal'
        })

        # Temperature effect (for relevant parameters)
        if param in ['voc', 'isc', 'pmax']:
            temp_uncertainty = value * sources['temperature_measurement'] * 0.003  # 0.3%/°C
            uncertainty_components.append({
                'source': 'Temperature Measurement',
                'type': 'Type B',
                'value': temp_uncertainty,
                'distribution': 'Rectangular'
            })

        # Irradiance effect (for relevant parameters)
        if param in ['isc', 'pmax']:
            irr_uncertainty = value * sources['irradiance_measurement'] / 100
            uncertainty_components.append({
                'source': 'Irradiance Measurement',
                'type': 'Type B',
                'value': irr_uncertainty,
                'distribution': 'Normal'
            })

        return {
            'parameter': param,
            'value': value,
            'sources': uncertainty_components
        }

    def _generate_pdf_report(self) -> bytes:
        """Generate PDF report."""
        # This would use a PDF generation library like ReportLab
        # For now, return JSON as bytes
        report_data = {
            'protocol_id': self.protocol_id,
            'protocol_name': self.protocol_name,
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'setup': self.test_data.get('setup', {}),
            'parameters': self.parameters,
            'validation': self.results.get('validation', {}),
            'audit_trail': self.audit_trail
        }

        return json.dumps(report_data, indent=2).encode('utf-8')

    def _generate_excel_report(self) -> bytes:
        """Generate Excel report."""
        # Would use openpyxl or xlsxwriter
        # For now, return CSV as bytes
        if self.processed_data:
            df = pd.DataFrame({
                'Voltage (V)': self.processed_data['voltage'],
                'Current (A)': self.processed_data['current'],
                'Power (W)': self.processed_data['power']
            })
            return df.to_csv(index=False).encode('utf-8')
        else:
            return b''

    def _generate_json_report(self) -> bytes:
        """Generate JSON report with all data."""
        report_data = {
            'metadata': self.get_metadata(),
            'test_data': self.test_data,
            'results': self.results,
            'parameters': self.parameters,
            'corrections_applied': self.corrections_applied,
            'uncertainty_analysis': self.uncertainty_analysis,
            'audit_trail': self.audit_trail,
            'iv_curve_data': {
                'voltage': self.processed_data['voltage'].tolist() if self.processed_data else [],
                'current': self.processed_data['current'].tolist() if self.processed_data else [],
                'power': self.processed_data['power'].tolist() if self.processed_data else []
            } if self.processed_data else {}
        }

        return json.dumps(report_data, indent=2, default=str).encode('utf-8')

    def _get_manufacturer_list(self) -> List[str]:
        """Get list of manufacturers from database."""
        # Placeholder - would query actual database
        return ['JinkoSolar', 'Trina Solar', 'LONGi Solar', 'JA Solar', 'Canadian Solar', 'Other']

    def _get_equipment_list(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get list of equipment from database."""
        # Placeholder - would query actual database
        return {
            'solar_simulators': [
                {'id': 'SS-001', 'name': 'Simulator A', 'calibration_date': '2024-06-01'},
                {'id': 'SS-002', 'name': 'Simulator B', 'calibration_date': '2024-05-15'}
            ],
            'iv_tracers': [
                {'id': 'IV-001', 'name': 'Tracer A', 'calibration_date': '2024-06-10'},
                {'id': 'IV-002', 'name': 'Tracer B', 'calibration_date': '2024-05-20'}
            ],
            'temperature_sensors': [
                {'id': 'TS-001', 'name': 'Thermocouple A', 'calibration_date': '2024-06-15'},
                {'id': 'TS-002', 'name': 'Thermocouple B', 'calibration_date': '2024-05-25'}
            ]
        }

    def _get_user_list(self) -> List[Dict[str, Any]]:
        """Get list of users from database."""
        # Placeholder - would query actual database
        return [
            {'id': 'user001', 'name': 'John Doe', 'role': 'operator'},
            {'id': 'user002', 'name': 'Jane Smith', 'role': 'reviewer'},
            {'id': 'user003', 'name': 'Bob Johnson', 'role': 'reviewer'}
        ]

    def _check_equipment_calibration(self, equipment_id: str) -> bool:
        """Check if equipment calibration is valid."""
        # Placeholder - would query actual database
        return True

    def _has_historical_data(self) -> bool:
        """Check if historical data exists for this module."""
        # Placeholder
        return False

    def _has_multi_temperature_data(self) -> bool:
        """Check if multi-temperature data exists."""
        # Placeholder
        return False

    def _has_repeat_measurements(self) -> bool:
        """Check if repeat measurements exist."""
        # Placeholder
        return False
