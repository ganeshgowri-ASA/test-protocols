"""IAM (Incidence Angle Modifier) calculations for PV modules."""

from typing import Any, Dict, List, Tuple
import numpy as np
from scipy import interpolate


class IAMCalculator:
    """Calculate Incidence Angle Modifier values from measurement data."""

    def __init__(self, measurements: List[Dict[str, Any]]) -> None:
        """Initialize IAM calculator with measurement data.

        Args:
            measurements: List of measurement dictionaries with angle and performance data
        """
        self.measurements = sorted(measurements, key=lambda x: x.get("angle", 0))
        self.angles = np.array([m.get("angle", 0) for m in self.measurements])
        self.powers = np.array([m.get("pmax", 0) for m in self.measurements])
        self.currents = np.array([m.get("isc", 0) for m in self.measurements])

    def calculate_iam(
        self,
        metric: str = "pmax",
        normalization_angle: float = 0.0
    ) -> List[Dict[str, float]]:
        """Calculate IAM values for all measurement angles.

        Args:
            metric: Performance metric to use ('pmax', 'isc', 'voc')
            normalization_angle: Angle for normalization (typically 0°)

        Returns:
            List of dictionaries with angle and IAM values
        """
        # Extract performance metric
        if metric == "pmax":
            values = self.powers
        elif metric == "isc":
            values = self.currents
        elif metric == "voc":
            values = np.array([m.get("voc", 0) for m in self.measurements])
        else:
            raise ValueError(f"Invalid metric: {metric}")

        # Find normalization value
        norm_idx = np.argmin(np.abs(self.angles - normalization_angle))
        norm_value = values[norm_idx]

        if norm_value == 0:
            raise ValueError(f"Normalization value at {normalization_angle}° is zero")

        # Calculate IAM values
        iam_values = values / norm_value

        # Create result list
        iam_curve = []
        for i, angle in enumerate(self.angles):
            iam_curve.append({
                "angle": float(angle),
                "iam": float(iam_values[i]),
                "raw_value": float(values[i])
            })

        return iam_curve

    def calculate_iam_with_correction(
        self,
        metric: str = "pmax",
        normalization_angle: float = 0.0,
        correct_irradiance: bool = True
    ) -> List[Dict[str, float]]:
        """Calculate IAM with irradiance and temperature corrections.

        Args:
            metric: Performance metric to use
            normalization_angle: Angle for normalization
            correct_irradiance: Whether to correct for irradiance variations

        Returns:
            List of dictionaries with angle and corrected IAM values
        """
        # Get raw IAM values
        iam_curve = self.calculate_iam(metric, normalization_angle)

        if not correct_irradiance:
            return iam_curve

        # Apply irradiance correction
        target_irradiance = self.measurements[0].get("irradiance_actual", 1000)

        for i, meas in enumerate(self.measurements):
            actual_irr = meas.get("irradiance_actual", target_irradiance)

            if actual_irr > 0 and abs(actual_irr - target_irradiance) > 10:
                # Apply linear correction for irradiance
                correction_factor = target_irradiance / actual_irr
                iam_curve[i]["iam"] *= correction_factor
                iam_curve[i]["irradiance_corrected"] = True
            else:
                iam_curve[i]["irradiance_corrected"] = False

        return iam_curve

    def interpolate_iam(
        self,
        iam_curve: List[Dict[str, float]],
        target_angles: List[float],
        method: str = "cubic"
    ) -> List[Dict[str, float]]:
        """Interpolate IAM values for specific angles.

        Args:
            iam_curve: IAM curve data
            target_angles: List of angles to interpolate
            method: Interpolation method ('linear', 'cubic', 'quadratic')

        Returns:
            List of interpolated IAM values
        """
        angles = np.array([point["angle"] for point in iam_curve])
        iam_values = np.array([point["iam"] for point in iam_curve])

        # Create interpolation function
        if method == "linear":
            f = interpolate.interp1d(angles, iam_values, kind="linear", fill_value="extrapolate")
        elif method == "cubic":
            if len(angles) < 4:
                # Fall back to linear for insufficient points
                f = interpolate.interp1d(angles, iam_values, kind="linear", fill_value="extrapolate")
            else:
                f = interpolate.interp1d(angles, iam_values, kind="cubic", fill_value="extrapolate")
        elif method == "quadratic":
            if len(angles) < 3:
                f = interpolate.interp1d(angles, iam_values, kind="linear", fill_value="extrapolate")
            else:
                f = interpolate.interp1d(angles, iam_values, kind="quadratic", fill_value="extrapolate")
        else:
            raise ValueError(f"Invalid interpolation method: {method}")

        # Interpolate for target angles
        target_angles = np.array(target_angles)
        interpolated_iam = f(target_angles)

        result = []
        for angle, iam in zip(target_angles, interpolated_iam):
            result.append({
                "angle": float(angle),
                "iam": float(iam),
                "interpolated": True
            })

        return result

    def calculate_effective_irradiance(
        self,
        aoi: float,
        ghi: float,
        iam_value: float
    ) -> float:
        """Calculate effective irradiance accounting for angle of incidence.

        Args:
            aoi: Angle of incidence in degrees
            ghi: Global horizontal irradiance in W/m²
            iam_value: IAM value at the given AOI

        Returns:
            Effective irradiance in W/m²
        """
        # Convert angle to radians
        aoi_rad = np.radians(aoi)

        # Geometric projection
        geometric_factor = np.cos(aoi_rad)

        # Effective irradiance
        effective_irr = ghi * geometric_factor * iam_value

        return max(0.0, float(effective_irr))

    def get_statistics(self, iam_curve: List[Dict[str, float]]) -> Dict[str, float]:
        """Calculate statistics for IAM curve.

        Args:
            iam_curve: IAM curve data

        Returns:
            Dictionary with statistical metrics
        """
        iam_values = np.array([point["iam"] for point in iam_curve])
        angles = np.array([point["angle"] for point in iam_curve])

        stats = {
            "mean_iam": float(np.mean(iam_values)),
            "std_iam": float(np.std(iam_values)),
            "min_iam": float(np.min(iam_values)),
            "max_iam": float(np.max(iam_values)),
            "iam_at_50deg": self._get_iam_at_angle(iam_curve, 50.0),
            "iam_at_60deg": self._get_iam_at_angle(iam_curve, 60.0),
            "iam_at_70deg": self._get_iam_at_angle(iam_curve, 70.0),
            "angle_range": float(np.max(angles) - np.min(angles)),
            "num_points": len(iam_curve)
        }

        return stats

    def _get_iam_at_angle(
        self,
        iam_curve: List[Dict[str, float]],
        target_angle: float
    ) -> float:
        """Get IAM value at a specific angle (with interpolation if needed).

        Args:
            iam_curve: IAM curve data
            target_angle: Target angle in degrees

        Returns:
            IAM value at target angle
        """
        # Check if exact angle exists
        for point in iam_curve:
            if abs(point["angle"] - target_angle) < 0.1:
                return point["iam"]

        # Interpolate
        try:
            interpolated = self.interpolate_iam(iam_curve, [target_angle])
            return interpolated[0]["iam"]
        except:
            return 0.0

    def validate_iam_curve(
        self,
        iam_curve: List[Dict[str, float]]
    ) -> Tuple[bool, List[str]]:
        """Validate IAM curve for physical consistency.

        Args:
            iam_curve: IAM curve data

        Returns:
            Tuple of (is_valid, list of warning messages)
        """
        warnings = []

        iam_values = np.array([point["iam"] for point in iam_curve])

        # Check for values > 1 (should be at or below 1 at normal incidence)
        if np.any(iam_values > 1.05):  # Allow 5% tolerance
            max_iam = np.max(iam_values)
            warnings.append(f"IAM values exceed 1.0: max = {max_iam:.3f}")

        # Check for negative values
        if np.any(iam_values < 0):
            warnings.append("Negative IAM values detected")

        # Check for monotonic decrease
        if len(iam_values) > 1:
            non_monotonic = sum(1 for i in range(1, len(iam_values)) if iam_values[i] > iam_values[i-1])
            if non_monotonic > len(iam_values) * 0.2:
                warnings.append(f"IAM does not decrease monotonically ({non_monotonic} violations)")

        # Check for reasonable values at high angles
        high_angle_points = [p for p in iam_curve if p["angle"] > 70]
        if high_angle_points:
            high_angle_iam = [p["iam"] for p in high_angle_points]
            if max(high_angle_iam) > 0.5:
                warnings.append(f"Unexpectedly high IAM at angles > 70°: {max(high_angle_iam):.3f}")

        return len(warnings) == 0, warnings
