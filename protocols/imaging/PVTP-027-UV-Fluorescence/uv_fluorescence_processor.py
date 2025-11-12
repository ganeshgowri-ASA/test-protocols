"""
PVTP-027: UV Fluorescence Imaging Processor
Encapsulant degradation detection through fluorescence analysis
"""

import numpy as np
import cv2
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UVFluorescenceProcessor:
    """UV fluorescence image analysis"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_fluorescence_intensity(self, image: np.ndarray,
                                      baseline: np.ndarray = None) -> Dict:
        """Analyze fluorescence intensity distribution"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        stats = {
            'mean_intensity': float(np.mean(gray)),
            'std_intensity': float(np.std(gray)),
            'cv': float(np.std(gray) / np.mean(gray)),
            'max_intensity': float(np.max(gray)),
            'min_intensity': float(np.min(gray))
        }

        if baseline is not None:
            baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY) if len(baseline.shape) == 3 else baseline
            intensity_change = (np.mean(gray) - np.mean(baseline_gray)) / np.mean(baseline_gray)
            stats['intensity_change_ratio'] = float(intensity_change)

            # Classify degradation
            if intensity_change > 0.3:
                stats['degradation_level'] = 'severe'
            elif intensity_change > 0.1:
                stats['degradation_level'] = 'moderate'
            else:
                stats['degradation_level'] = 'minor'
        else:
            stats['degradation_level'] = 'unknown'

        return stats

    def detect_degradation_patterns(self, image: np.ndarray) -> Dict:
        """Detect patterns indicating EVA degradation"""
        # Convert to LAB color space for better color analysis
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # Yellow-green fluorescence indicates EVA degradation
        # In LAB: positive b (yellow), slightly positive a
        eva_degradation_mask = (b > 128) & (a > 120)

        degradation_area = np.sum(eva_degradation_mask)
        total_area = eva_degradation_mask.size
        degradation_percentage = (degradation_area / total_area) * 100

        result = {
            'degradation_area_pixels': int(degradation_area),
            'degradation_percentage': float(degradation_percentage),
            'severity': 'severe' if degradation_percentage > 30 else
                       'moderate' if degradation_percentage > 10 else 'minor'
        }

        return result

    def run_full_analysis(self, image_path: str, baseline_path: str = None,
                         module_serial: str = None) -> Dict:
        """Run complete UV fluorescence analysis"""
        self.logger.info(f"Starting UV fluorescence analysis for {module_serial}")

        # Load images
        image = cv2.imread(image_path)
        baseline = cv2.imread(baseline_path) if baseline_path else None

        # Analyze intensity
        intensity_stats = self.analyze_fluorescence_intensity(image, baseline)

        # Detect degradation patterns
        degradation = self.detect_degradation_patterns(image)

        # Determine grade
        if degradation['severity'] == 'severe' or intensity_stats.get('degradation_level') == 'severe':
            grade = 'F'
        elif degradation['severity'] == 'moderate':
            grade = 'C'
        else:
            grade = 'A'

        result = {
            'module_serial': module_serial,
            'intensity_statistics': intensity_stats,
            'degradation_analysis': degradation,
            'grade': grade,
            'qc_status': 'PASS' if grade in ['A', 'B', 'C'] else 'FAIL'
        }

        self.logger.info(f"Analysis complete: Grade={grade}")
        return result


if __name__ == "__main__":
    print("UV Fluorescence Processor initialized")
