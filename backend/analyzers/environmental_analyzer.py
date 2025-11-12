"""
Environmental Test Data Analyzer
Statistical analysis and predictive modeling for environmental stress test data
"""

import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')


@dataclass
class DegradationModel:
    """Statistical model for performance degradation"""
    parameter: str
    model_type: str  # linear, exponential, logarithmic
    coefficients: List[float]
    r_squared: float
    rmse: float
    predicted_failure_time: Optional[float]
    confidence_interval_95: Tuple[float, float]


@dataclass
class EnvironmentalCorrelation:
    """Correlation between environmental exposure and degradation"""
    parameter: str
    correlation_coefficient: float
    p_value: float
    is_significant: bool
    humidity_sensitivity: float
    temperature_sensitivity: float


@dataclass
class FailureRiskAssessment:
    """Predictive failure analysis results"""
    module_id: str
    current_degradation_rate: float
    time_to_5_percent_loss: Optional[float]
    time_to_10_percent_loss: Optional[float]
    probability_of_failure: float
    risk_level: str  # low, moderate, high, critical
    failure_modes: List[str]


class EnvironmentalDataAnalyzer:
    """Advanced statistical analysis for environmental stress test data"""

    def __init__(self):
        self.degradation_models = {}
        self.correlation_analysis = {}

    @staticmethod
    def linear_model(x, a, b):
        """Linear degradation model: y = ax + b"""
        return a * x + b

    @staticmethod
    def exponential_model(x, a, b, c):
        """Exponential degradation model: y = a * exp(bx) + c"""
        return a * np.exp(b * x) + c

    @staticmethod
    def logarithmic_model(x, a, b):
        """Logarithmic degradation model: y = a * ln(x) + b"""
        return a * np.log(x + 1) + b  # +1 to avoid log(0)

    def fit_degradation_model(self, time_data: np.ndarray, performance_data: np.ndarray,
                              parameter_name: str, failure_threshold: float = 5.0) -> DegradationModel:
        """
        Fit multiple models to degradation data and select best fit

        Args:
            time_data: Array of time points (hours)
            performance_data: Array of performance values (% degradation)
            parameter_name: Name of the parameter being analyzed
            failure_threshold: Threshold for failure prediction (% degradation)

        Returns:
            Best-fit degradation model
        """
        if len(time_data) < 3:
            raise ValueError("Insufficient data points for model fitting (minimum 3 required)")

        models = []

        # Fit linear model
        try:
            linear_coeffs = np.polyfit(time_data, performance_data, 1)
            linear_pred = np.polyval(linear_coeffs, time_data)
            linear_r2 = self._calculate_r_squared(performance_data, linear_pred)
            linear_rmse = self._calculate_rmse(performance_data, linear_pred)

            # Predict failure time
            if linear_coeffs[0] > 0:  # Degradation is increasing
                failure_time = (failure_threshold - linear_coeffs[1]) / linear_coeffs[0]
                failure_time = failure_time if failure_time > 0 else None
            else:
                failure_time = None

            # Calculate confidence interval
            conf_int = self._calculate_confidence_interval(time_data, performance_data, linear_coeffs)

            models.append(DegradationModel(
                parameter=parameter_name,
                model_type="linear",
                coefficients=linear_coeffs.tolist(),
                r_squared=linear_r2,
                rmse=linear_rmse,
                predicted_failure_time=failure_time,
                confidence_interval_95=conf_int
            ))
        except Exception as e:
            pass

        # Fit exponential model
        try:
            # Initial guess for exponential parameters
            p0 = [1, 0.001, 0]
            exp_coeffs, _ = curve_fit(self.exponential_model, time_data, performance_data, p0=p0, maxfev=5000)
            exp_pred = self.exponential_model(time_data, *exp_coeffs)
            exp_r2 = self._calculate_r_squared(performance_data, exp_pred)
            exp_rmse = self._calculate_rmse(performance_data, exp_pred)

            # Predict failure time (numerically)
            failure_time = self._find_threshold_time(exp_coeffs, failure_threshold, "exponential")

            models.append(DegradationModel(
                parameter=parameter_name,
                model_type="exponential",
                coefficients=exp_coeffs.tolist(),
                r_squared=exp_r2,
                rmse=exp_rmse,
                predicted_failure_time=failure_time,
                confidence_interval_95=(None, None)
            ))
        except Exception as e:
            pass

        # Fit logarithmic model
        try:
            log_coeffs, _ = curve_fit(self.logarithmic_model, time_data, performance_data, maxfev=5000)
            log_pred = self.logarithmic_model(time_data, *log_coeffs)
            log_r2 = self._calculate_r_squared(performance_data, log_pred)
            log_rmse = self._calculate_rmse(performance_data, log_pred)

            # Predict failure time
            failure_time = self._find_threshold_time(log_coeffs, failure_threshold, "logarithmic")

            models.append(DegradationModel(
                parameter=parameter_name,
                model_type="logarithmic",
                coefficients=log_coeffs.tolist(),
                r_squared=log_r2,
                rmse=log_rmse,
                predicted_failure_time=failure_time,
                confidence_interval_95=(None, None)
            ))
        except Exception as e:
            pass

        # Select best model based on R-squared
        if not models:
            raise ValueError("Failed to fit any degradation model")

        best_model = max(models, key=lambda m: m.r_squared)
        self.degradation_models[parameter_name] = best_model

        return best_model

    def _calculate_r_squared(self, y_actual: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R-squared (coefficient of determination)"""
        ss_res = np.sum((y_actual - y_pred) ** 2)
        ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    def _calculate_rmse(self, y_actual: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate root mean square error"""
        return np.sqrt(np.mean((y_actual - y_pred) ** 2))

    def _calculate_confidence_interval(self, x: np.ndarray, y: np.ndarray,
                                      coeffs: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for linear model predictions"""
        n = len(x)
        if n < 3:
            return (None, None)

        y_pred = np.polyval(coeffs, x)
        residuals = y - y_pred
        std_error = np.sqrt(np.sum(residuals ** 2) / (n - 2))

        # t-statistic for 95% confidence
        t_stat = stats.t.ppf((1 + confidence) / 2, n - 2)

        # Standard error of the slope
        x_mean = np.mean(x)
        se_slope = std_error / np.sqrt(np.sum((x - x_mean) ** 2))

        margin = t_stat * se_slope
        return (coeffs[0] - margin, coeffs[0] + margin)

    def _find_threshold_time(self, coeffs: List[float], threshold: float, model_type: str) -> Optional[float]:
        """Numerically find time when degradation reaches threshold"""
        try:
            time_range = np.linspace(0, 10000, 10000)  # Search up to 10,000 hours

            if model_type == "exponential":
                values = self.exponential_model(time_range, *coeffs)
            elif model_type == "logarithmic":
                values = self.logarithmic_model(time_range, *coeffs)
            else:
                return None

            # Find first time where value exceeds threshold
            exceeds = values >= threshold
            if np.any(exceeds):
                idx = np.argmax(exceeds)
                return float(time_range[idx])
            return None
        except Exception:
            return None

    def analyze_humidity_correlation(self, exposure_hours: np.ndarray,
                                    avg_humidity: np.ndarray,
                                    avg_temperature: np.ndarray,
                                    degradation: np.ndarray,
                                    parameter_name: str) -> EnvironmentalCorrelation:
        """
        Analyze correlation between humidity exposure and degradation

        Args:
            exposure_hours: Array of cumulative exposure times
            avg_humidity: Array of average humidity values
            avg_temperature: Array of average temperature values
            degradation: Array of degradation values
            parameter_name: Name of the parameter being analyzed

        Returns:
            Environmental correlation analysis
        """
        # Calculate humidity-hours (exposure metric)
        humidity_hours = exposure_hours * (avg_humidity / 100)

        # Correlation with humidity exposure
        humidity_corr, humidity_p = stats.pearsonr(humidity_hours, degradation)

        # Correlation with temperature
        temp_corr, temp_p = stats.pearsonr(avg_temperature, degradation)

        # Multiple linear regression to separate effects
        # Model: degradation = a * humidity + b * temperature + c
        X = np.column_stack([avg_humidity, avg_temperature])
        coeffs = np.linalg.lstsq(
            np.column_stack([X, np.ones(len(degradation))]),
            degradation,
            rcond=None
        )[0]

        humidity_sensitivity = coeffs[0]
        temperature_sensitivity = coeffs[1]

        # Determine if correlation is statistically significant (p < 0.05)
        is_significant = humidity_p < 0.05

        correlation = EnvironmentalCorrelation(
            parameter=parameter_name,
            correlation_coefficient=humidity_corr,
            p_value=humidity_p,
            is_significant=is_significant,
            humidity_sensitivity=humidity_sensitivity,
            temperature_sensitivity=temperature_sensitivity
        )

        self.correlation_analysis[parameter_name] = correlation

        return correlation

    def predict_failure_risk(self, current_time: float, current_degradation: float,
                            degradation_rate: float, module_id: str,
                            visual_defects: List[str] = None) -> FailureRiskAssessment:
        """
        Assess failure risk based on current degradation trends

        Args:
            current_time: Current test time (hours)
            current_degradation: Current degradation (%)
            degradation_rate: Current degradation rate (%/1000h)
            module_id: Module identifier
            visual_defects: List of observed visual defects

        Returns:
            Failure risk assessment
        """
        if visual_defects is None:
            visual_defects = []

        # Predict time to critical thresholds
        if degradation_rate > 0:
            time_to_5_percent = ((5.0 - current_degradation) / degradation_rate) * 1000
            time_to_10_percent = ((10.0 - current_degradation) / degradation_rate) * 1000

            # Adjust if already past threshold
            time_to_5_percent = time_to_5_percent if time_to_5_percent > 0 else 0
            time_to_10_percent = time_to_10_percent if time_to_10_percent > 0 else 0
        else:
            time_to_5_percent = None
            time_to_10_percent = None

        # Calculate probability of failure using sigmoid function
        # Based on current degradation and visual defects
        base_prob = 1 / (1 + np.exp(-0.5 * (current_degradation - 3)))  # Sigmoid centered at 3%

        # Increase probability if visual defects present
        defect_multiplier = 1.0
        critical_defects = ["delamination", "broken_cells", "corrosion", "open_circuits"]
        for defect in visual_defects:
            if any(critical in defect.lower() for critical in critical_defects):
                defect_multiplier += 0.2

        probability_of_failure = min(base_prob * defect_multiplier, 1.0)

        # Identify likely failure modes
        failure_modes = []
        if current_degradation > 3:
            failure_modes.append("progressive_power_loss")
        if "delamination" in visual_defects:
            failure_modes.append("moisture_ingress")
        if "corrosion" in visual_defects:
            failure_modes.append("contact_corrosion")
        if "broken_cells" in visual_defects or "broken_interconnects" in visual_defects:
            failure_modes.append("mechanical_failure")
        if degradation_rate > 5.0:  # Fast degradation
            failure_modes.append("accelerated_degradation")

        # Determine risk level
        if probability_of_failure > 0.7 or current_degradation > 8:
            risk_level = "critical"
        elif probability_of_failure > 0.5 or current_degradation > 5:
            risk_level = "high"
        elif probability_of_failure > 0.3 or current_degradation > 3:
            risk_level = "moderate"
        else:
            risk_level = "low"

        return FailureRiskAssessment(
            module_id=module_id,
            current_degradation_rate=degradation_rate,
            time_to_5_percent_loss=time_to_5_percent,
            time_to_10_percent_loss=time_to_10_percent,
            probability_of_failure=probability_of_failure,
            risk_level=risk_level,
            failure_modes=failure_modes
        )

    def compare_modules(self, module_data: Dict[str, List[Tuple[float, float]]]) -> Dict:
        """
        Statistical comparison of degradation across multiple modules

        Args:
            module_data: Dictionary mapping module_id to list of (time, degradation) tuples

        Returns:
            Comparative analysis results
        """
        if len(module_data) < 2:
            return {"error": "Need at least 2 modules for comparison"}

        module_rates = {}
        module_predictions = {}

        # Fit models for each module
        for module_id, data in module_data.items():
            times = np.array([d[0] for d in data])
            degradations = np.array([d[1] for d in data])

            if len(times) >= 3:
                try:
                    model = self.fit_degradation_model(times, degradations, f"{module_id}_power")
                    module_rates[module_id] = model.coefficients[0]  # Slope/rate
                    module_predictions[module_id] = model.predicted_failure_time
                except Exception:
                    continue

        # Statistical tests
        if len(module_rates) >= 2:
            rates = list(module_rates.values())

            # One-way ANOVA to test if degradation rates are significantly different
            # (need at least 3 groups for meaningful ANOVA)
            if len(rates) >= 3:
                f_stat, p_value = stats.f_oneway(*[[r] for r in rates])
                significantly_different = p_value < 0.05
            else:
                # For 2 modules, use t-test
                if len(rates) == 2:
                    t_stat, p_value = stats.ttest_ind([rates[0]], [rates[1]])
                    significantly_different = p_value < 0.05
                    f_stat = None
                else:
                    f_stat, p_value = None, None
                    significantly_different = False

            # Identify outliers (modules with significantly different degradation)
            mean_rate = np.mean(rates)
            std_rate = np.std(rates)
            outliers = []

            for module_id, rate in module_rates.items():
                z_score = abs((rate - mean_rate) / std_rate) if std_rate > 0 else 0
                if z_score > 2:  # 2 standard deviations
                    outliers.append({
                        "module_id": module_id,
                        "rate": rate,
                        "z_score": z_score,
                        "deviation": rate - mean_rate
                    })

            return {
                "module_count": len(module_rates),
                "mean_degradation_rate": mean_rate,
                "std_degradation_rate": std_rate,
                "min_rate": min(rates),
                "max_rate": max(rates),
                "f_statistic": f_stat,
                "p_value": p_value,
                "significantly_different": significantly_different,
                "outliers": outliers,
                "individual_predictions": module_predictions
            }
        else:
            return {"error": "Insufficient data for statistical comparison"}

    def estimate_field_lifetime(self, test_duration: float, test_degradation: float,
                               acceleration_factor: float = 1.0,
                               target_degradation: float = 20.0) -> Dict:
        """
        Estimate field lifetime based on accelerated test results

        Args:
            test_duration: Duration of accelerated test (hours)
            test_degradation: Degradation observed in test (%)
            acceleration_factor: Acceleration factor relative to field conditions
            target_degradation: Target degradation level for lifetime estimate (%)

        Returns:
            Lifetime estimate and confidence bounds
        """
        if test_degradation <= 0 or test_duration <= 0:
            return {"error": "Invalid test data"}

        # Calculate degradation rate
        test_rate = test_degradation / test_duration  # % per hour

        # Extrapolate to target degradation
        test_time_to_target = target_degradation / test_rate  # hours in test

        # Convert to field conditions using acceleration factor
        field_hours_to_target = test_time_to_target * acceleration_factor

        # Convert to years (8760 hours per year)
        field_years_to_target = field_hours_to_target / 8760

        # Estimate confidence bounds (±30% typical for lifetime predictions)
        lower_bound = field_years_to_target * 0.7
        upper_bound = field_years_to_target * 1.3

        return {
            "test_rate_percent_per_1000h": test_rate * 1000,
            "field_rate_percent_per_year": (test_rate / acceleration_factor) * 8760,
            "estimated_lifetime_years": field_years_to_target,
            "confidence_bounds": {
                "lower": lower_bound,
                "upper": upper_bound
            },
            "acceleration_factor_used": acceleration_factor,
            "assumptions": [
                "Linear degradation extrapolation",
                "Constant acceleration factor",
                "No infant mortality or wear-out effects"
            ]
        }

    def generate_summary_statistics(self, measurements: List[Dict]) -> Dict:
        """
        Generate comprehensive summary statistics for test results

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Summary statistics
        """
        if not measurements:
            return {"error": "No measurements provided"}

        # Extract data
        power_loss = [m['power_loss_percentage'] for m in measurements]
        insulation_r = [m['insulation_resistance'] for m in measurements]
        times = [m['interval'] for m in measurements]

        stats_summary = {
            "power_degradation": {
                "initial": power_loss[0] if len(power_loss) > 0 else None,
                "final": power_loss[-1] if len(power_loss) > 0 else None,
                "mean": np.mean(power_loss),
                "median": np.median(power_loss),
                "std": np.std(power_loss),
                "min": np.min(power_loss),
                "max": np.max(power_loss),
                "total_change": power_loss[-1] - power_loss[0] if len(power_loss) > 1 else 0
            },
            "insulation_resistance": {
                "initial": insulation_r[0] if len(insulation_r) > 0 else None,
                "final": insulation_r[-1] if len(insulation_r) > 0 else None,
                "mean": np.mean(insulation_r),
                "median": np.median(insulation_r),
                "std": np.std(insulation_r),
                "min": np.min(insulation_r),
                "max": np.max(insulation_r),
                "below_threshold_count": sum(1 for r in insulation_r if r < 40)
            },
            "measurement_count": len(measurements),
            "test_duration": times[-1] if times else 0
        }

        # Calculate degradation rate if enough data
        if len(times) >= 2 and len(power_loss) >= 2:
            rate_coeffs = np.polyfit(times, power_loss, 1)
            stats_summary["degradation_rate_percent_per_1000h"] = rate_coeffs[0] * 1000

        return stats_summary
