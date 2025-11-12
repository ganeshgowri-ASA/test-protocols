"""
PVTP-026: Visual Inspection Processor
Computer vision and AI/ML for automated visual defect detection
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisualDefectType(Enum):
    """Visual defect types"""
    CELL_CRACK = "cell_crack"
    GLASS_CRACK = "glass_crack"
    DISCOLORATION = "discoloration"
    BUBBLES = "bubbles"
    DELAMINATION = "delamination"
    SCRATCHES = "scratches"
    CHIPS = "chips"
    FRAME_DAMAGE = "frame_damage"


@dataclass
class VisualDefect:
    """Visual defect data"""
    defect_id: str
    defect_type: VisualDefectType
    severity: str
    location: Tuple[int, int]
    bounding_box: Tuple[int, int, int, int]
    area_pixels: int
    confidence: float
    color_delta_e: float = 0.0
    size_mm: float = 0.0


class VisualInspectionProcessor:
    """Automated visual inspection with CV and AI/ML"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def detect_cracks(self, image: np.ndarray) -> List[VisualDefect]:
        """Detect cracks using edge detection and morphology"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Morphological operations to connect crack segments
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        defects = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 50 or area > 10000:  # Filter by size
                continue

            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = max(w, h) / min(w, h)

            # Cracks typically have high aspect ratio
            if aspect_ratio > 3:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                else:
                    cx, cy = x + w // 2, y + h // 2

                # Classify severity based on length
                length = max(w, h)
                if length < 25:
                    severity = "minor"
                elif length < 50:
                    severity = "moderate"
                else:
                    severity = "severe"

                defect = VisualDefect(
                    defect_id=f"CRACK-{i:03d}",
                    defect_type=VisualDefectType.CELL_CRACK,
                    severity=severity,
                    location=(cx, cy),
                    bounding_box=(x, y, w, h),
                    area_pixels=int(area),
                    confidence=0.85,
                    size_mm=float(length * 0.1)  # Placeholder conversion
                )
                defects.append(defect)

        self.logger.info(f"Detected {len(defects)} cracks")
        return defects

    def detect_discoloration(self, image: np.ndarray,
                           reference_color: np.ndarray = None) -> List[VisualDefect]:
        """Detect discoloration using color analysis"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # Calculate mean color
        if reference_color is None:
            reference_color = np.mean(lab, axis=(0, 1))

        # Calculate color difference (simplified Delta E)
        l, a, b = cv2.split(lab)
        delta_l = l - reference_color[0]
        delta_a = a - reference_color[1]
        delta_b = b - reference_color[2]
        delta_e = np.sqrt(delta_l**2 + delta_a**2 + delta_b**2)

        # Threshold for discoloration
        discolored_mask = delta_e > 15

        # Find regions
        mask_uint8 = discolored_mask.astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        defects = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 100:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            # Calculate average Delta E in this region
            mask_region = np.zeros_like(delta_e)
            cv2.drawContours(mask_region, [contour], -1, 1, -1)
            avg_delta_e = np.mean(delta_e[mask_region > 0])

            # Classify severity
            if avg_delta_e < 10:
                severity = "minor"
            elif avg_delta_e < 20:
                severity = "moderate"
            else:
                severity = "severe"

            defect = VisualDefect(
                defect_id=f"DISC-{i:03d}",
                defect_type=VisualDefectType.DISCOLORATION,
                severity=severity,
                location=(x + w // 2, y + h // 2),
                bounding_box=(x, y, w, h),
                area_pixels=int(area),
                confidence=0.80,
                color_delta_e=float(avg_delta_e)
            )
            defects.append(defect)

        self.logger.info(f"Detected {len(defects)} discolored regions")
        return defects

    def detect_bubbles(self, image: np.ndarray) -> List[VisualDefect]:
        """Detect bubbles using blob detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Blob detection parameters
        params = cv2.SimpleBlobDetector_Params()
        params.filterByCircularity = True
        params.minCircularity = 0.7
        params.filterByConvexity = True
        params.minConvexity = 0.8
        params.filterByArea = True
        params.minArea = 50
        params.maxArea = 5000

        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(gray)

        defects = []
        for i, kp in enumerate(keypoints):
            diameter = kp.size

            # Classify severity
            if diameter < 5:
                severity = "minor"
            elif diameter < 10:
                severity = "moderate"
            else:
                severity = "severe"

            x, y = int(kp.pt[0]), int(kp.pt[1])
            r = int(diameter / 2)

            defect = VisualDefect(
                defect_id=f"BUBB-{i:03d}",
                defect_type=VisualDefectType.BUBBLES,
                severity=severity,
                location=(x, y),
                bounding_box=(x - r, y - r, 2 * r, 2 * r),
                area_pixels=int(np.pi * r * r),
                confidence=0.75,
                size_mm=float(diameter * 0.1)
            )
            defects.append(defect)

        self.logger.info(f"Detected {len(defects)} bubbles")
        return defects

    def run_full_inspection(self, image_path: str,
                          module_serial: str) -> Dict:
        """Run complete visual inspection"""
        self.logger.info(f"Starting visual inspection for {module_serial}")

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        # Detect different defect types
        cracks = self.detect_cracks(image)
        discoloration = self.detect_discoloration(image)
        bubbles = self.detect_bubbles(image)

        all_defects = cracks + discoloration + bubbles

        # Grade module
        critical = sum(1 for d in all_defects if d.severity == "critical")
        severe = sum(1 for d in all_defects if d.severity == "severe")
        moderate = sum(1 for d in all_defects if d.severity == "moderate")
        minor = sum(1 for d in all_defects if d.severity == "minor")

        if critical > 0 or severe > 3:
            grade = "F"
        elif severe <= 3:
            if moderate <= 2 and minor <= 5:
                if moderate == 0 and minor <= 2:
                    grade = "A"
                elif moderate <= 1:
                    grade = "B"
                else:
                    grade = "C"
            else:
                grade = "D"
        else:
            grade = "F"

        result = {
            'module_serial': module_serial,
            'total_defects': len(all_defects),
            'defects_by_type': {
                'cracks': len(cracks),
                'discoloration': len(discoloration),
                'bubbles': len(bubbles)
            },
            'defects_by_severity': {
                'critical': critical,
                'severe': severe,
                'moderate': moderate,
                'minor': minor
            },
            'grade': grade,
            'qc_status': 'PASS' if grade in ['A', 'B', 'C'] else 'FAIL'
        }

        self.logger.info(f"Inspection complete: Grade={grade}, Defects={len(all_defects)}")
        return result


if __name__ == "__main__":
    print("Visual Inspection Processor initialized")
