"""Curve fitting models for IAM data."""

from typing import Any, Dict, List, Tuple, Protocol
import numpy as np
from scipy.optimize import curve_fit
from abc import ABC, abstractmethod


class IAMModel(ABC):
    """Abstract base class for IAM models."""

    @abstractmethod
    def function(self, angle: np.ndarray, *params: float) -> np.ndarray:
        """Model function to fit.

        Args:
            angle: Angle of incidence in degrees
            *params: Model parameters

        Returns:
            IAM values
        """
        pass

    @abstractmethod
    def get_param_names(self) -> List[str]:
        """Get parameter names for this model.

        Returns:
            List of parameter names
        """
        pass

    @abstractmethod
    def get_initial_guess(self) -> List[float]:
        """Get initial parameter guess for fitting.

        Returns:
            List of initial parameter values
        """
        pass

    @abstractmethod
    def get_bounds(self) -> Tuple[List[float], List[float]]:
        """Get parameter bounds for fitting.

        Returns:
            Tuple of (lower_bounds, upper_bounds)
        """
        pass


class ASHRAEModel(IAMModel):
    """ASHRAE incidence angle modifier model.

    IAM(θ) = 1 - b₀ * (1/cos(θ) - 1)

    This is a simple single-parameter model commonly used in building energy simulation.
    """

    def function(self, angle: np.ndarray, b0: float) -> np.ndarray:
        """ASHRAE model function.

        Args:
            angle: Angle of incidence in degrees
            b0: ASHRAE model parameter

        Returns:
            IAM values
        """
        # Convert to radians
        theta_rad = np.radians(angle)

        # Handle angles at or near 90 degrees
        cos_theta = np.cos(theta_rad)
        cos_theta = np.maximum(cos_theta, 1e-6)  # Avoid division by zero

        iam = 1.0 - b0 * (1.0 / cos_theta - 1.0)

        return np.maximum(iam, 0.0)  # IAM cannot be negative

    def get_param_names(self) -> List[str]:
        return ["b0"]

    def get_initial_guess(self) -> List[float]:
        return [0.05]

    def get_bounds(self) -> Tuple[List[float], List[float]]:
        return ([0.0], [1.0])


class PhysicalModel(IAMModel):
    """Physical model based on Fresnel equations and cover transmission.

    IAM(θ) = (1 - exp(-cos(θ)/a_r)) / (1 - exp(-1/a_r))

    This model accounts for reflective losses at the module cover.
    """

    def function(self, angle: np.ndarray, a_r: float) -> np.ndarray:
        """Physical model function.

        Args:
            angle: Angle of incidence in degrees
            a_r: Angular losses coefficient

        Returns:
            IAM values
        """
        theta_rad = np.radians(angle)
        cos_theta = np.cos(theta_rad)

        # Avoid division by zero and overflow
        cos_theta = np.maximum(cos_theta, 1e-6)
        a_r = np.maximum(a_r, 1e-6)

        numerator = 1.0 - np.exp(-cos_theta / a_r)
        denominator = 1.0 - np.exp(-1.0 / a_r)

        # Avoid division by zero
        denominator = np.maximum(denominator, 1e-6)

        iam = numerator / denominator

        return np.clip(iam, 0.0, 1.0)

    def get_param_names(self) -> List[str]:
        return ["a_r"]

    def get_initial_guess(self) -> List[float]:
        return [0.16]

    def get_bounds(self) -> Tuple[List[float], List[float]]:
        return ([0.01], [0.5])


class PolynomialModel(IAMModel):
    """Polynomial model for IAM.

    IAM(θ) = 1 + a₁*θ + a₂*θ² + a₃*θ³ + a₄*θ⁴

    This flexible model can fit a wide range of IAM behaviors.
    """

    def __init__(self, degree: int = 4) -> None:
        """Initialize polynomial model.

        Args:
            degree: Polynomial degree (2-4)
        """
        if degree < 2 or degree > 4:
            raise ValueError("Polynomial degree must be between 2 and 4")
        self.degree = degree

    def function(self, angle: np.ndarray, *params: float) -> np.ndarray:
        """Polynomial model function.

        Args:
            angle: Angle of incidence in degrees
            *params: Polynomial coefficients

        Returns:
            IAM values
        """
        # Normalize angle to [0, 1] range for better numerical stability
        angle_norm = angle / 90.0

        iam = np.ones_like(angle_norm)

        for i, coef in enumerate(params, start=1):
            iam += coef * (angle_norm ** i)

        return np.clip(iam, 0.0, 1.2)  # Allow slight exceedance of 1.0

    def get_param_names(self) -> List[str]:
        return [f"a{i}" for i in range(1, self.degree + 1)]

    def get_initial_guess(self) -> List[float]:
        return [-0.1] * self.degree

    def get_bounds(self) -> Tuple[List[float], List[float]]:
        lower = [-2.0] * self.degree
        upper = [2.0] * self.degree
        return (lower, upper)


class CurveFitter:
    """Fit IAM models to measurement data."""

    def __init__(self, iam_curve: List[Dict[str, float]]) -> None:
        """Initialize curve fitter with IAM data.

        Args:
            iam_curve: List of dictionaries with angle and iam values
        """
        self.iam_curve = iam_curve
        self.angles = np.array([point["angle"] for point in iam_curve])
        self.iam_values = np.array([point["iam"] for point in iam_curve])

    def fit_model(
        self,
        model: IAMModel,
        weights: np.ndarray = None
    ) -> Dict[str, Any]:
        """Fit a model to the IAM data.

        Args:
            model: IAM model to fit
            weights: Optional weights for data points

        Returns:
            Dictionary with fit results
        """
        try:
            # Perform curve fitting
            popt, pcov = curve_fit(
                model.function,
                self.angles,
                self.iam_values,
                p0=model.get_initial_guess(),
                bounds=model.get_bounds(),
                sigma=weights,
                absolute_sigma=False,
                maxfev=10000
            )

            # Calculate fitted values
            fitted_values = model.function(self.angles, *popt)

            # Calculate goodness of fit metrics
            r_squared = self._calculate_r_squared(self.iam_values, fitted_values)
            rmse = self._calculate_rmse(self.iam_values, fitted_values)
            mae = self._calculate_mae(self.iam_values, fitted_values)

            # Get parameter uncertainties
            perr = np.sqrt(np.diag(pcov))

            # Build parameters dictionary
            param_names = model.get_param_names()
            parameters = {}
            for name, value, error in zip(param_names, popt, perr):
                parameters[name] = {
                    "value": float(value),
                    "error": float(error)
                }

            result = {
                "model": model.__class__.__name__.replace("Model", "").lower(),
                "parameters": parameters,
                "r_squared": float(r_squared),
                "rmse": float(rmse),
                "mae": float(mae),
                "fitted_values": fitted_values.tolist(),
                "residuals": (self.iam_values - fitted_values).tolist(),
                "success": True
            }

        except Exception as e:
            result = {
                "model": model.__class__.__name__.replace("Model", "").lower(),
                "parameters": {},
                "r_squared": 0.0,
                "rmse": float("inf"),
                "mae": float("inf"),
                "fitted_values": [],
                "residuals": [],
                "success": False,
                "error": str(e)
            }

        return result

    def fit_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Fit all available models to the data.

        Returns:
            Dictionary with results for each model
        """
        models = {
            "ashrae": ASHRAEModel(),
            "physical": PhysicalModel(),
            "polynomial": PolynomialModel(degree=4)
        }

        results = {}
        for name, model in models.items():
            results[name] = self.fit_model(model)

        return results

    def select_best_model(
        self,
        fit_results: Dict[str, Dict[str, Any]],
        criterion: str = "r_squared"
    ) -> Tuple[str, Dict[str, Any]]:
        """Select the best model based on a criterion.

        Args:
            fit_results: Dictionary of fit results for different models
            criterion: Selection criterion ('r_squared', 'rmse', 'mae')

        Returns:
            Tuple of (best_model_name, best_model_results)
        """
        valid_results = {
            name: result
            for name, result in fit_results.items()
            if result.get("success", False)
        }

        if not valid_results:
            raise ValueError("No valid fit results available")

        if criterion == "r_squared":
            best_name = max(valid_results.keys(), key=lambda k: valid_results[k]["r_squared"])
        elif criterion in ["rmse", "mae"]:
            best_name = min(valid_results.keys(), key=lambda k: valid_results[k][criterion])
        else:
            raise ValueError(f"Invalid criterion: {criterion}")

        return best_name, valid_results[best_name]

    def predict(
        self,
        model: IAMModel,
        parameters: Dict[str, Any],
        angles: np.ndarray
    ) -> np.ndarray:
        """Predict IAM values using fitted model.

        Args:
            model: IAM model
            parameters: Fitted parameters dictionary
            angles: Angles to predict at

        Returns:
            Predicted IAM values
        """
        # Extract parameter values
        param_values = [parameters[name]["value"] for name in model.get_param_names()]

        # Predict
        predicted = model.function(angles, *param_values)

        return predicted

    @staticmethod
    def _calculate_r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R-squared (coefficient of determination).

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            R-squared value
        """
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

        if ss_tot == 0:
            return 0.0

        r_squared = 1.0 - (ss_res / ss_tot)
        return float(r_squared)

    @staticmethod
    def _calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Root Mean Square Error.

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            RMSE value
        """
        mse = np.mean((y_true - y_pred) ** 2)
        return float(np.sqrt(mse))

    @staticmethod
    def _calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Error.

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            MAE value
        """
        mae = np.mean(np.abs(y_true - y_pred))
        return float(mae)

    def generate_smooth_curve(
        self,
        model: IAMModel,
        parameters: Dict[str, Any],
        num_points: int = 100
    ) -> List[Dict[str, float]]:
        """Generate smooth IAM curve using fitted model.

        Args:
            model: Fitted IAM model
            parameters: Model parameters
            num_points: Number of points to generate

        Returns:
            List of dictionaries with angle and iam values
        """
        angles = np.linspace(0, 90, num_points)
        iam_values = self.predict(model, parameters, angles)

        smooth_curve = []
        for angle, iam in zip(angles, iam_values):
            smooth_curve.append({
                "angle": float(angle),
                "iam": float(iam),
                "fitted": True
            })

        return smooth_curve
