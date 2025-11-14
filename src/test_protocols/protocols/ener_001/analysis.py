"""Analysis module for ENER-001 Energy Rating Test."""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats


class EnergyRatingAnalyzer:
    """Analyzes energy rating test data according to IEC 61853."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize analyzer.

        Args:
            config: Protocol configuration dictionary
        """
        self.config = config
        self.outputs = config.get("outputs", [])

        # Standard test conditions (STC)
        self.stc_irradiance = 1000  # W/m²
        self.stc_temperature = 25  # °C

    def analyze(
        self, iv_curves: Dict[str, Any], data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Perform complete analysis of energy rating test.

        Args:
            iv_curves: Dictionary of IV curves
            data: Raw measurement data

        Returns:
            Dictionary with analysis results
        """
        analysis = {}

        # Calculate performance parameters
        analysis["performance_parameters"] = self._calculate_performance_parameters(
            iv_curves
        )

        # Calculate temperature coefficients
        analysis["temperature_coefficients"] = self.calculate_temperature_coefficients(
            iv_curves
        )

        # Calculate energy rating
        analysis["energy_rating"] = self.calculate_energy_rating(iv_curves)

        # Performance at STC
        analysis["stc_performance"] = self._interpolate_stc_performance(iv_curves)

        # Statistical summary
        analysis["statistical_summary"] = self._calculate_statistical_summary(iv_curves)

        # Performance matrix
        analysis["performance_matrix"] = self._create_performance_matrix(iv_curves)

        return analysis

    def _calculate_performance_parameters(
        self, iv_curves: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate performance parameters for all test conditions."""
        params = {
            "num_conditions": len(iv_curves),
            "irradiance_range": [],
            "temperature_range": [],
            "pmpp_range": [],
            "efficiency_range": [],
            "fill_factor_range": [],
        }

        all_irr = []
        all_temp = []
        all_pmpp = []
        all_eff = []
        all_ff = []

        for key, curve in iv_curves.items():
            all_irr.append(curve["irradiance"])
            all_temp.append(curve["temperature"])
            all_pmpp.append(curve["pmpp"])
            all_ff.append(curve["fill_factor"])

            if "efficiency" in curve:
                all_eff.append(curve["efficiency"])

        params["irradiance_range"] = [min(all_irr), max(all_irr)]
        params["temperature_range"] = [min(all_temp), max(all_temp)]
        params["pmpp_range"] = [min(all_pmpp), max(all_pmpp)]
        params["fill_factor_range"] = [min(all_ff), max(all_ff)]

        if all_eff:
            params["efficiency_range"] = [min(all_eff), max(all_eff)]

        return params

    def calculate_temperature_coefficients(
        self, iv_curves: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate temperature coefficients of performance parameters.

        Args:
            iv_curves: Dictionary of IV curves

        Returns:
            Dictionary with temperature coefficients
        """
        coefficients = {
            "alpha_isc": 0.0,  # Temperature coefficient of Isc (%/°C)
            "beta_voc": 0.0,  # Temperature coefficient of Voc (%/°C)
            "gamma_pmax": 0.0,  # Temperature coefficient of Pmax (%/°C)
        }

        # For each irradiance level, calculate coefficients from temperature variation
        irradiance_groups = {}

        for key, curve in iv_curves.items():
            irr = curve["irradiance"]
            if irr not in irradiance_groups:
                irradiance_groups[irr] = []
            irradiance_groups[irr].append(curve)

        # Calculate coefficients for each irradiance level and average
        alpha_list = []
        beta_list = []
        gamma_list = []

        for irr, curves in irradiance_groups.items():
            if len(curves) < 2:
                continue

            temps = np.array([c["temperature"] for c in curves])
            iscs = np.array([c["isc"] for c in curves])
            vocs = np.array([c["voc"] for c in curves])
            pmpps = np.array([c["pmpp"] for c in curves])

            # Linear regression to find coefficients
            # Normalize to reference values at 25°C
            ref_idx = np.argmin(np.abs(temps - 25))
            isc_ref = iscs[ref_idx]
            voc_ref = vocs[ref_idx]
            pmpp_ref = pmpps[ref_idx]

            if len(temps) >= 2:
                # Calculate percentage change per degree
                try:
                    # Isc coefficient (typically positive)
                    if isc_ref > 0:
                        isc_norm = (iscs / isc_ref - 1) * 100
                        slope_isc, _, _, _, _ = stats.linregress(temps, isc_norm)
                        alpha_list.append(slope_isc)

                    # Voc coefficient (typically negative)
                    if voc_ref > 0:
                        voc_norm = (vocs / voc_ref - 1) * 100
                        slope_voc, _, _, _, _ = stats.linregress(temps, voc_norm)
                        beta_list.append(slope_voc)

                    # Pmax coefficient (typically negative)
                    if pmpp_ref > 0:
                        pmpp_norm = (pmpps / pmpp_ref - 1) * 100
                        slope_pmpp, _, _, _, _ = stats.linregress(temps, pmpp_norm)
                        gamma_list.append(slope_pmpp)

                except Exception:
                    continue

        # Average coefficients across irradiance levels
        if alpha_list:
            coefficients["alpha_isc"] = float(np.mean(alpha_list))
            coefficients["alpha_isc_std"] = float(np.std(alpha_list))

        if beta_list:
            coefficients["beta_voc"] = float(np.mean(beta_list))
            coefficients["beta_voc_std"] = float(np.std(beta_list))

        if gamma_list:
            coefficients["gamma_pmax"] = float(np.mean(gamma_list))
            coefficients["gamma_pmax_std"] = float(np.std(gamma_list))

        return coefficients

    def calculate_energy_rating(
        self, iv_curves: Dict[str, Any], climate: str = "moderate"
    ) -> Dict[str, float]:
        """
        Calculate energy rating according to IEC 61853-3.

        Args:
            iv_curves: Dictionary of IV curves
            climate: Climate zone ('hot', 'moderate', 'cold')

        Returns:
            Dictionary with energy rating in kWh/kWp
        """
        # Climate-specific weighting factors for different operating conditions
        # Based on IEC 61853-3 distribution of irradiance and temperature
        climate_weights = {
            "moderate": {
                # (irradiance, temperature): weight
                (200, 25): 0.05,
                (400, 25): 0.12,
                (600, 25): 0.15,
                (800, 25): 0.18,
                (1000, 25): 0.20,
                (200, 50): 0.03,
                (400, 50): 0.08,
                (600, 50): 0.10,
                (800, 50): 0.07,
                (1000, 50): 0.02,
            },
            "hot": {
                (200, 50): 0.08,
                (400, 50): 0.15,
                (600, 50): 0.20,
                (800, 50): 0.22,
                (1000, 50): 0.15,
                (200, 75): 0.03,
                (400, 75): 0.07,
                (600, 75): 0.06,
                (800, 75): 0.03,
                (1000, 75): 0.01,
            },
            "cold": {
                (200, 15): 0.08,
                (400, 15): 0.15,
                (600, 15): 0.18,
                (800, 15): 0.20,
                (1000, 15): 0.15,
                (200, 25): 0.05,
                (400, 25): 0.10,
                (600, 25): 0.06,
                (800, 25): 0.02,
                (1000, 25): 0.01,
            },
        }

        weights = climate_weights.get(climate, climate_weights["moderate"])

        # Calculate weighted energy
        total_energy = 0.0
        total_weight = 0.0
        rated_power = None

        # Find rated power (power at STC: 1000 W/m², 25°C)
        for key, curve in iv_curves.items():
            if (
                abs(curve["irradiance"] - 1000) < 50
                and abs(curve["temperature"] - 25) < 5
            ):
                rated_power = curve["pmpp"]
                break

        # If no STC measurement, use maximum power
        if rated_power is None:
            rated_power = max(c["pmpp"] for c in iv_curves.values())

        # Calculate energy contribution from each condition
        contributions = {}

        for (target_irr, target_temp), weight in weights.items():
            # Find closest matching test point
            best_match = None
            min_distance = float("inf")

            for key, curve in iv_curves.items():
                irr = curve["irradiance"]
                temp = curve["temperature"]

                # Normalized distance
                distance = np.sqrt(
                    ((irr - target_irr) / 1000) ** 2 + ((temp - target_temp) / 50) ** 2
                )

                if distance < min_distance:
                    min_distance = distance
                    best_match = curve

            if best_match:
                # Energy contribution (normalized to 1 kWp)
                power_normalized = (best_match["pmpp"] / rated_power) if rated_power > 0 else 0
                energy_contribution = power_normalized * weight * 1000  # kWh/kWp

                total_energy += energy_contribution
                total_weight += weight

                contributions[f"G{target_irr}_T{target_temp}"] = {
                    "power": best_match["pmpp"],
                    "weight": weight,
                    "energy_contribution": energy_contribution,
                }

        # Normalize to annual kWh/kWp
        # Assuming reference annual irradiation of 1700 kWh/m²
        annual_irradiation = 1700

        energy_rating = {
            "climate_zone": climate,
            "energy_rating_kWh_per_kWp": float(total_energy),
            "rated_power_W": float(rated_power) if rated_power else 0,
            "annual_irradiation_kWh_m2": annual_irradiation,
            "performance_ratio": float(total_energy / annual_irradiation * 100) if annual_irradiation > 0 else 0,
            "contributions": contributions,
        }

        return energy_rating

    def _interpolate_stc_performance(self, iv_curves: Dict[str, Any]) -> Dict[str, float]:
        """Interpolate performance at STC conditions."""
        # Find closest measurement to STC
        best_match = None
        min_distance = float("inf")

        for key, curve in iv_curves.items():
            distance = np.sqrt(
                (curve["irradiance"] - self.stc_irradiance) ** 2
                + (curve["temperature"] - self.stc_temperature) ** 2
            )

            if distance < min_distance:
                min_distance = distance
                best_match = curve

        if best_match:
            return {
                "pmpp": float(best_match["pmpp"]),
                "voc": float(best_match["voc"]),
                "isc": float(best_match["isc"]),
                "vmpp": float(best_match["vmpp"]),
                "impp": float(best_match["impp"]),
                "fill_factor": float(best_match["fill_factor"]),
                "efficiency": float(best_match.get("efficiency", 0)),
                "distance_from_stc": float(min_distance),
            }

        return {}

    def _calculate_statistical_summary(self, iv_curves: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistical summary of test results."""
        pmpps = [c["pmpp"] for c in iv_curves.values()]
        ffs = [c["fill_factor"] for c in iv_curves.values()]
        effs = [c.get("efficiency", 0) for c in iv_curves.values() if "efficiency" in c]

        summary = {
            "pmpp": {
                "mean": float(np.mean(pmpps)),
                "std": float(np.std(pmpps)),
                "min": float(np.min(pmpps)),
                "max": float(np.max(pmpps)),
                "cv_percent": float(np.std(pmpps) / np.mean(pmpps) * 100) if np.mean(pmpps) > 0 else 0,
            },
            "fill_factor": {
                "mean": float(np.mean(ffs)),
                "std": float(np.std(ffs)),
                "min": float(np.min(ffs)),
                "max": float(np.max(ffs)),
            },
        }

        if effs:
            summary["efficiency"] = {
                "mean": float(np.mean(effs)),
                "std": float(np.std(effs)),
                "min": float(np.min(effs)),
                "max": float(np.max(effs)),
            }

        return summary

    def _create_performance_matrix(self, iv_curves: Dict[str, Any]) -> Dict[str, Any]:
        """Create performance matrix organized by irradiance and temperature."""
        matrix = {}

        for key, curve in iv_curves.items():
            irr = int(curve["irradiance"])
            temp = int(curve["temperature"])

            if irr not in matrix:
                matrix[irr] = {}

            matrix[irr][temp] = {
                "pmpp": float(curve["pmpp"]),
                "efficiency": float(curve.get("efficiency", 0)),
                "fill_factor": float(curve["fill_factor"]),
                "voc": float(curve["voc"]),
                "isc": float(curve["isc"]),
            }

        return matrix
