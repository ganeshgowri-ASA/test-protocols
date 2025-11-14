"""
SPEC-001: Spectral Response Test (IEC 60904-8)
Measures the spectral response of photovoltaic devices
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import constants, integrate

from .base import Protocol, ProtocolExecutor


logger = logging.getLogger(__name__)


class SpectralResponseTest(ProtocolExecutor):
    """
    Spectral Response Test executor following IEC 60904-8
    """

    # Physical constants
    H = constants.h  # Planck constant (J·s)
    C = constants.c  # Speed of light (m/s)
    Q = constants.e  # Elementary charge (C)

    def __init__(
        self,
        protocol: Optional[Protocol] = None,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize Spectral Response Test

        Args:
            protocol: Protocol instance (if None, loads SPEC-001)
            output_dir: Directory for output files
        """
        if protocol is None:
            # Load default SPEC-001 protocol
            protocol_path = (
                Path(__file__).parent.parent.parent / "protocols" / "SPEC-001.json"
            )
            protocol = Protocol(str(protocol_path))

        super().__init__(protocol, output_dir)

        # Test-specific attributes
        self.raw_data = None
        self.calculated_data = None
        self.reference_sr = None  # Reference detector spectral response

    def load_reference_calibration(
        self, calibration_file: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load reference detector calibration data

        Args:
            calibration_file: Path to calibration file (wavelength, SR columns)

        Returns:
            DataFrame with wavelength and spectral response
        """
        if calibration_file is None:
            # Use ideal reference (1 A/W for demonstration)
            logger.warning("No calibration file provided, using ideal reference (1 A/W)")
            wavelengths = np.arange(300, 1201, 10)
            self.reference_sr = pd.DataFrame(
                {"wavelength": wavelengths, "spectral_response": np.ones_like(wavelengths)}
            )
        else:
            self.reference_sr = pd.read_csv(calibration_file)

        return self.reference_sr

    def run(self) -> Dict[str, Any]:
        """
        Execute the spectral response measurement

        In a real implementation, this would:
        1. Control monochromator to sweep wavelengths
        2. Measure photocurrent from sample and reference
        3. Record temperature and other conditions

        For this framework, we'll simulate the measurement process
        """
        logger.info(f"Starting spectral response test: {self.test_id}")
        self.status = "running"

        # Get test parameters
        wavelength_start = self.test_params.get("wavelength", {}).get("start", 300)
        wavelength_end = self.test_params.get("wavelength", {}).get("end", 1200)
        step_size = self.test_params.get("wavelength", {}).get("step_size", 10)
        averaging = self.test_params.get("averaging", 3)
        temperature = self.test_params.get("temperature", 25)

        # Generate wavelength array
        wavelengths = np.arange(wavelength_start, wavelength_end + step_size, step_size)
        n_points = len(wavelengths)

        logger.info(
            f"Measuring {n_points} wavelength points from {wavelength_start} to {wavelength_end} nm"
        )

        # Simulate measurement (in real implementation, this would interface with hardware)
        photocurrent_sample = self._simulate_measurement(wavelengths, averaging)
        photocurrent_reference = self._simulate_reference(wavelengths, averaging)

        # Record temperature readings
        temperature_readings = temperature + np.random.normal(0, 0.5, n_points)

        # Create raw data DataFrame
        self.raw_data = pd.DataFrame(
            {
                "wavelength": wavelengths,
                "photocurrent_sample": photocurrent_sample,
                "photocurrent_reference": photocurrent_reference,
                "temperature": temperature_readings,
                "timestamp": np.arange(n_points) * 0.5,  # 0.5s per point
            }
        )

        # Store in results
        self.results["raw_data"] = self.raw_data.to_dict(orient="list")

        logger.info("Spectral response measurement completed")
        return self.results

    def _simulate_measurement(
        self, wavelengths: np.ndarray, averaging: int
    ) -> np.ndarray:
        """
        Simulate spectral response measurement
        In real implementation, this would control hardware and acquire data

        Args:
            wavelengths: Array of wavelength points
            averaging: Number of averages per point

        Returns:
            Array of photocurrent values
        """
        # Simulate a typical silicon solar cell spectral response
        # Peak around 800-900 nm, falloff at UV and IR

        sr_ideal = np.zeros_like(wavelengths, dtype=float)

        for i, wl in enumerate(wavelengths):
            if wl < 400:
                # UV region - low response
                sr_ideal[i] = 0.1 * np.exp((wl - 300) / 50)
            elif wl < 1100:
                # Visible to near-IR - good response
                sr_ideal[i] = 0.6 - 0.3 * ((wl - 800) / 300) ** 2
            else:
                # IR region - declining response
                sr_ideal[i] = 0.3 * np.exp(-(wl - 1100) / 50)

        # Add some realistic noise
        noise = np.random.normal(0, 0.01, len(wavelengths))
        sr_measured = sr_ideal + noise

        # Convert to photocurrent (arbitrary scale, e.g., 1 mW incident power)
        photocurrent = sr_measured * 1e-3  # Amps

        return photocurrent

    def _simulate_reference(
        self, wavelengths: np.ndarray, averaging: int
    ) -> np.ndarray:
        """
        Simulate reference detector measurement

        Args:
            wavelengths: Array of wavelength points
            averaging: Number of averages per point

        Returns:
            Array of reference photocurrent values
        """
        # Simulate relatively flat reference detector with some noise
        ref_current = np.ones_like(wavelengths) * 1e-3  # 1 mA typical
        noise = np.random.normal(0, 1e-5, len(wavelengths))
        return ref_current + noise

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze spectral response data and calculate EQE

        Returns:
            Dictionary containing analysis results
        """
        logger.info("Analyzing spectral response data")

        if self.raw_data is None:
            raise ValueError("No raw data available. Run test first.")

        # Load reference calibration if not already loaded
        if self.reference_sr is None:
            self.load_reference_calibration()

        wavelengths = self.raw_data["wavelength"].values
        i_sample = self.raw_data["photocurrent_sample"].values
        i_reference = self.raw_data["photocurrent_reference"].values

        # Interpolate reference SR to match measurement wavelengths
        sr_ref_interp = np.interp(
            wavelengths,
            self.reference_sr["wavelength"],
            self.reference_sr["spectral_response"],
        )

        # Calculate spectral response: SR(λ) = I_sample(λ) / [I_ref(λ) × SR_ref(λ)]
        # Assuming reference current corresponds to known power
        spectral_response = i_sample / (i_reference * sr_ref_interp)

        # Calculate External Quantum Efficiency: EQE(λ) = SR(λ) × (hc/qλ) × 100%
        # Convert wavelength from nm to m
        wavelengths_m = wavelengths * 1e-9

        # EQE = (SR * h * c) / (q * λ)
        eqe = (spectral_response * self.H * self.C) / (self.Q * wavelengths_m) * 100

        # Calculate integrated Jsc under AM1.5G spectrum
        integrated_jsc = self._calculate_integrated_jsc(wavelengths, spectral_response)

        # Find peak values
        peak_idx = np.argmax(eqe)
        peak_wavelength = wavelengths[peak_idx]
        peak_eqe = eqe[peak_idx]

        # Create calculated data DataFrame
        self.calculated_data = pd.DataFrame(
            {
                "wavelength": wavelengths,
                "spectral_response": spectral_response,
                "external_quantum_efficiency": eqe,
            }
        )

        # Store analysis results
        self.results["calculated_data"] = self.calculated_data.to_dict(orient="list")
        self.results["integrated_jsc"] = integrated_jsc
        self.results["peak_wavelength"] = peak_wavelength
        self.results["peak_eqe"] = peak_eqe

        logger.info(
            f"Analysis complete: Peak EQE = {peak_eqe:.1f}% at {peak_wavelength:.0f} nm, Jsc = {integrated_jsc:.2f} mA/cm²"
        )

        return self.results

    def _calculate_integrated_jsc(
        self, wavelengths: np.ndarray, spectral_response: np.ndarray
    ) -> float:
        """
        Calculate integrated short-circuit current density under AM1.5G spectrum

        Args:
            wavelengths: Wavelength array (nm)
            spectral_response: Spectral response array (A/W)

        Returns:
            Integrated Jsc (mA/cm²)
        """
        # Load AM1.5G spectrum (simplified - use tabulated data in real implementation)
        am15g_spectrum = self._get_am15g_spectrum(wavelengths)

        # Jsc = ∫ SR(λ) × Φ(λ) dλ / Area
        # where Φ(λ) is the photon flux from AM1.5G spectrum

        integrand = spectral_response * am15g_spectrum
        jsc = integrate.trapz(integrand, wavelengths)

        # Convert to mA/cm² (assuming area already normalized)
        sample_area = self.sample_info.get("area", 1.0)  # cm²
        jsc_density = (jsc / sample_area) * 1000  # mA/cm²

        return jsc_density

    def _get_am15g_spectrum(self, wavelengths: np.ndarray) -> np.ndarray:
        """
        Get AM1.5G solar spectrum at specified wavelengths

        Args:
            wavelengths: Wavelength array (nm)

        Returns:
            Spectral irradiance (W/m²/nm)

        Note: This is a simplified model. Use ASTM G173-03 reference data for real testing.
        """
        # Simplified AM1.5G model (Gaussian approximation)
        # Peak around 500 nm, total irradiance ~1000 W/m²
        center = 500
        width = 200
        am15g = 1.5 * np.exp(-((wavelengths - center) ** 2) / (2 * width**2))

        # Normalize to approximately 1000 W/m² total
        total_power = integrate.trapz(am15g, wavelengths)
        am15g = am15g * (1000 / total_power)

        return am15g

    def run_qc(self) -> Dict[str, bool]:
        """
        Run quality control checks specific to spectral response test

        Returns:
            Dictionary of QC results
        """
        logger.info("Running QC checks")

        if self.calculated_data is None:
            raise ValueError("No calculated data available. Run analysis first.")

        qc_criteria = self.protocol.get_qc_criteria()
        qc_results = {}

        # Check noise level
        sr_noise = np.std(self.calculated_data["spectral_response"].values)
        qc_results["noise_level"] = {
            "passed": sr_noise < qc_criteria["noise_level"]["threshold"],
            "value": sr_noise,
            "threshold": qc_criteria["noise_level"]["threshold"],
            "unit": "A/W",
            "action": qc_criteria["noise_level"]["action_on_fail"],
        }

        # Check reference stability
        ref_current = self.raw_data["photocurrent_reference"].values
        ref_stability = (np.std(ref_current) / np.mean(ref_current)) * 100
        qc_results["reference_stability"] = {
            "passed": ref_stability < qc_criteria["reference_stability"]["threshold"],
            "value": ref_stability,
            "threshold": qc_criteria["reference_stability"]["threshold"],
            "unit": "%",
            "action": qc_criteria["reference_stability"]["action_on_fail"],
        }

        # Check temperature stability
        temp_variation = np.ptp(self.raw_data["temperature"].values)
        qc_results["temperature_stability"] = {
            "passed": temp_variation < qc_criteria["temperature_stability"]["threshold"],
            "value": temp_variation,
            "threshold": qc_criteria["temperature_stability"]["threshold"],
            "unit": "°C",
            "action": qc_criteria["temperature_stability"]["action_on_fail"],
        }

        # Check minimum EQE
        peak_eqe = self.results.get("peak_eqe", 0)
        qc_results["min_eqe"] = {
            "passed": peak_eqe > qc_criteria["min_eqe"]["threshold"],
            "value": peak_eqe,
            "threshold": qc_criteria["min_eqe"]["threshold"],
            "unit": "%",
            "action": qc_criteria["min_eqe"]["action_on_fail"],
        }

        # Check data completeness
        expected_points = len(self.raw_data)
        valid_points = np.sum(~np.isnan(self.raw_data["photocurrent_sample"]))
        completeness = (valid_points / expected_points) * 100
        qc_results["data_completeness"] = {
            "passed": completeness >= qc_criteria["data_completeness"]["threshold"],
            "value": completeness,
            "threshold": qc_criteria["data_completeness"]["threshold"],
            "unit": "%",
            "action": qc_criteria["data_completeness"]["action_on_fail"],
        }

        self.qc_results = qc_results

        # Log QC results
        all_passed = all(result["passed"] for result in qc_results.values())
        logger.info(f"QC checks completed: {'PASSED' if all_passed else 'FAILED'}")

        for check_name, result in qc_results.items():
            status = "PASS" if result["passed"] else "FAIL"
            logger.info(
                f"  {check_name}: {status} (value={result['value']:.3f}, threshold={result['threshold']})"
            )

        return qc_results

    def generate_plots(self) -> Dict[str, Path]:
        """
        Generate spectral response and EQE plots

        Returns:
            Dictionary of plot file paths
        """
        logger.info("Generating plots")

        if self.calculated_data is None:
            raise ValueError("No calculated data available. Run analysis first.")

        plot_paths = {}

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(
            f"Spectral Response Test Results - {self.sample_info.get('sample_id', 'Unknown')}",
            fontsize=14,
            fontweight="bold",
        )

        # Plot 1: Spectral Response
        ax1 = axes[0, 0]
        ax1.plot(
            self.calculated_data["wavelength"],
            self.calculated_data["spectral_response"],
            "b-",
            linewidth=2,
        )
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("Spectral Response (A/W)")
        ax1.set_title("Spectral Response vs Wavelength")
        ax1.grid(True, alpha=0.3)

        # Plot 2: External Quantum Efficiency
        ax2 = axes[0, 1]
        ax2.plot(
            self.calculated_data["wavelength"],
            self.calculated_data["external_quantum_efficiency"],
            "r-",
            linewidth=2,
        )
        ax2.set_xlabel("Wavelength (nm)")
        ax2.set_ylabel("EQE (%)")
        ax2.set_title("External Quantum Efficiency vs Wavelength")
        ax2.grid(True, alpha=0.3)
        ax2.axhline(
            y=self.results["peak_eqe"],
            color="r",
            linestyle="--",
            alpha=0.5,
            label=f'Peak: {self.results["peak_eqe"]:.1f}%',
        )
        ax2.legend()

        # Plot 3: Raw Photocurrent Data
        ax3 = axes[1, 0]
        ax3.semilogy(
            self.raw_data["wavelength"],
            self.raw_data["photocurrent_sample"],
            "g-",
            label="Sample",
            linewidth=2,
        )
        ax3.semilogy(
            self.raw_data["wavelength"],
            self.raw_data["photocurrent_reference"],
            "b--",
            label="Reference",
            linewidth=2,
        )
        ax3.set_xlabel("Wavelength (nm)")
        ax3.set_ylabel("Photocurrent (A)")
        ax3.set_title("Raw Photocurrent Data")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Temperature Monitoring
        ax4 = axes[1, 1]
        ax4.plot(
            self.raw_data["timestamp"],
            self.raw_data["temperature"],
            "m-",
            linewidth=2,
        )
        ax4.set_xlabel("Time (s)")
        ax4.set_ylabel("Temperature (°C)")
        ax4.set_title("Temperature Monitoring")
        ax4.grid(True, alpha=0.3)
        ax4.axhline(
            y=self.test_params.get("temperature", 25),
            color="r",
            linestyle="--",
            alpha=0.5,
            label="Target",
        )
        ax4.legend()

        plt.tight_layout()

        # Save plot
        plot_path = self.output_dir / f"{self.test_id}_plots.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close()

        plot_paths["main_plot"] = plot_path
        logger.info(f"Plots saved to {plot_path}")

        return plot_paths

    def export_results(self) -> Dict[str, Path]:
        """
        Export all test results and data

        Returns:
            Dictionary of exported file paths
        """
        logger.info("Exporting results")

        exported_files = {}

        # Save raw data
        raw_data_path = self.save_data(self.raw_data, f"{self.test_id}_raw_data.csv")
        exported_files["raw_data"] = raw_data_path

        # Save calculated data
        calc_data_path = self.save_data(
            self.calculated_data, f"{self.test_id}_calculated_data.csv"
        )
        exported_files["calculated_data"] = calc_data_path

        # Generate and save plots
        plot_paths = self.generate_plots()
        exported_files.update(plot_paths)

        # Generate report
        report_path = self.generate_report()
        exported_files["report"] = report_path

        logger.info(f"Results exported to {self.output_dir}")

        return exported_files
