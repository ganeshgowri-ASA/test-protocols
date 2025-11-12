"""
PVTP-025: IR Thermography Processor
Advanced thermal imaging analysis with AI/ML hotspot detection
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThermalAnomalyType(Enum):
    """Types of thermal anomalies"""
    BYPASS_DIODE_ACTIVATION = "bypass_diode_activation"
    CELL_HOTSPOT = "cell_hotspot"
    JUNCTION_BOX_OVERHEAT = "junction_box_overheat"
    STRING_MISMATCH = "string_mismatch"
    SHADING_EFFECT = "shading_effect"
    CELL_FAILURE = "cell_failure"
    INTERCONNECT_RESISTANCE = "interconnect_resistance"


@dataclass
class ThermalAnomaly:
    """Detected thermal anomaly"""
    anomaly_id: str
    anomaly_type: ThermalAnomalyType
    severity: str
    temperature_max: float
    temperature_delta: float
    location: Tuple[int, int]
    bounding_box: Tuple[int, int, int, int]
    area_pixels: int
    confidence: float


class IRThermographyProcessor:
    """IR Thermography image processor with AI/ML"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_thermal_image(self, image_path: str) -> Tuple[np.ndarray, Dict]:
        """
        Load radiometric thermal image

        Returns:
            Temperature array and metadata
        """
        self.logger.info(f"Loading thermal image: {image_path}")
        # In production, use specialized libraries like flir-image-extractor
        # to extract radiometric data from FLIR/thermal camera files

        # Placeholder: Load as regular image
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        # Convert to temperature (placeholder - actual conversion depends on camera)
        # Real implementation would extract temperature from radiometric data
        temperature_array = img.astype(np.float32) / 100.0  # Example conversion

        metadata = {
            'emissivity': 0.85,
            'distance': 3.0,
            'ambient_temp': 25.0
        }

        return temperature_array, metadata

    def apply_atmospheric_correction(self, temp_array: np.ndarray,
                                    distance: float,
                                    ambient_temp: float,
                                    humidity: float) -> np.ndarray:
        """Apply atmospheric attenuation correction"""
        # Simplified atmospheric correction
        # Real implementation would use more sophisticated models
        transmission = np.exp(-0.01 * distance)
        corrected = (temp_array - ambient_temp * (1 - transmission)) / transmission
        return corrected

    def detect_hotspots(self, temp_array: np.ndarray,
                       threshold_delta: float = 10.0,
                       reference_method: str = "module_mean") -> List[ThermalAnomaly]:
        """
        Detect thermal hotspots

        Args:
            temp_array: Temperature map
            threshold_delta: Temperature difference threshold
            reference_method: Reference temperature calculation method

        Returns:
            List of detected hotspots
        """
        self.logger.info("Detecting thermal hotspots")

        # Calculate reference temperature
        if reference_method == "module_mean":
            ref_temp = np.mean(temp_array)
        elif reference_method == "coolest_cell":
            ref_temp = np.percentile(temp_array, 10)
        else:
            ref_temp = np.median(temp_array)

        # Find hotspots
        hotspot_mask = (temp_array - ref_temp) > threshold_delta

        # Find connected components
        hotspot_mask_uint8 = hotspot_mask.astype(np.uint8) * 255
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            hotspot_mask_uint8, connectivity=8
        )

        anomalies = []
        for i in range(1, num_labels):  # Skip background (0)
            area = stats[i, cv2.CC_STAT_AREA]
            if area < 25:  # Minimum size filter
                continue

            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]

            # Get temperature stats in this region
            region_temps = temp_array[labels == i]
            max_temp = np.max(region_temps)
            delta_temp = max_temp - ref_temp

            # Classify severity
            if delta_temp > 25:
                severity = "severe"
            elif delta_temp > 15:
                severity = "moderate"
            else:
                severity = "minor"

            anomaly = ThermalAnomaly(
                anomaly_id=f"HS-{i:03d}",
                anomaly_type=ThermalAnomalyType.CELL_HOTSPOT,
                severity=severity,
                temperature_max=float(max_temp),
                temperature_delta=float(delta_temp),
                location=(int(centroids[i][0]), int(centroids[i][1])),
                bounding_box=(x, y, w, h),
                area_pixels=int(area),
                confidence=0.9
            )
            anomalies.append(anomaly)

        self.logger.info(f"Detected {len(anomalies)} thermal anomalies")
        return anomalies

    def calculate_temperature_statistics(self, temp_array: np.ndarray) -> Dict:
        """Calculate temperature distribution statistics"""
        stats = {
            'mean_temp': float(np.mean(temp_array)),
            'median_temp': float(np.median(temp_array)),
            'std_temp': float(np.std(temp_array)),
            'min_temp': float(np.min(temp_array)),
            'max_temp': float(np.max(temp_array)),
            'temp_range': float(np.ptp(temp_array)),
            'percentile_95': float(np.percentile(temp_array, 95)),
            'percentile_5': float(np.percentile(temp_array, 5))
        }
        return stats

    def generate_thermal_visualization(self, temp_array: np.ndarray,
                                       colormap: int = cv2.COLORMAP_JET) -> np.ndarray:
        """Generate color-coded thermal visualization"""
        # Normalize to 0-255
        temp_normalized = cv2.normalize(temp_array, None, 0, 255, cv2.NORM_MINMAX)
        temp_uint8 = temp_normalized.astype(np.uint8)

        # Apply colormap
        thermal_viz = cv2.applyColorMap(temp_uint8, colormap)

        return thermal_viz

    def grade_module_thermal(self, anomalies: List[ThermalAnomaly],
                           max_delta_t: float) -> str:
        """Grade module based on thermal performance"""
        critical_count = sum(1 for a in anomalies if a.severity == "critical")
        severe_count = sum(1 for a in anomalies if a.severity == "severe")
        moderate_count = sum(1 for a in anomalies if a.severity == "moderate")

        if critical_count > 0 or severe_count > 3 or max_delta_t > 30:
            return "F"
        elif severe_count <= 3 or max_delta_t < 30:
            if moderate_count <= 2 and max_delta_t < 25:
                if moderate_count <= 1 and max_delta_t < 15:
                    if moderate_count == 0 and max_delta_t < 10:
                        return "A"
                    return "B"
                return "C"
            return "D"
        return "F"

    def run_full_analysis(self, image_path: str,
                         test_params: Dict,
                         module_serial: str) -> Dict:
        """Run complete IR thermography analysis"""
        self.logger.info(f"Starting IR analysis for {module_serial}")

        # Load thermal image
        temp_array, metadata = self.load_thermal_image(image_path)

        # Apply corrections
        if test_params.get('apply_atmospheric_correction', True):
            temp_array = self.apply_atmospheric_correction(
                temp_array,
                test_params.get('distance', 3.0),
                test_params.get('ambient_temp', 25.0),
                test_params.get('humidity', 50.0)
            )

        # Detect anomalies
        anomalies = self.detect_hotspots(
            temp_array,
            threshold_delta=test_params.get('hotspot_threshold', 10.0)
        )

        # Calculate statistics
        stats = self.calculate_temperature_statistics(temp_array)

        # Grade module
        grade = self.grade_module_thermal(anomalies, stats['temp_range'])

        # Generate visualization
        thermal_viz = self.generate_thermal_visualization(temp_array)

        result = {
            'test_id': f"IR-{module_serial}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'module_serial': module_serial,
            'timestamp': datetime.now().isoformat(),
            'temperature_statistics': stats,
            'anomalies': [
                {
                    'id': a.anomaly_id,
                    'type': a.anomaly_type.value,
                    'severity': a.severity,
                    'max_temp': a.temperature_max,
                    'delta_temp': a.temperature_delta,
                    'location': a.location,
                    'area': a.area_pixels
                }
                for a in anomalies
            ],
            'grade': grade,
            'qc_status': 'PASS' if grade in ['A', 'B', 'C'] else 'FAIL',
            'nc_raised': grade in ['D', 'F']
        }

        self.logger.info(f"Analysis complete: Grade={grade}, Anomalies={len(anomalies)}")
        return result


if __name__ == "__main__":
    print("IR Thermography Processor initialized")
