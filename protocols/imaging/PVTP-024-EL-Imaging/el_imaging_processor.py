"""
PVTP-024: Electroluminescence (EL) Imaging Processor
Advanced image processing and AI/ML-based defect detection for solar module EL imaging
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DefectType(Enum):
    """Enumeration of EL defect types"""
    CELL_CRACK = "cell_crack"
    FINGER_INTERRUPTION = "finger_interruption"
    BUSBAR_INTERRUPTION = "busbar_interruption"
    INACTIVE_AREA = "inactive_area"
    SHUNT = "shunt"
    DARK_CELL = "dark_cell"
    CORROSION = "corrosion"
    SOLDER_BOND_FAILURE = "solder_bond_failure"


class SeverityLevel(Enum):
    """Defect severity classification"""
    NO_DEFECT = "no_defect"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class Grade(Enum):
    """Module quality grading"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


@dataclass
class Defect:
    """Represents a detected defect"""
    defect_id: str
    defect_type: DefectType
    severity: SeverityLevel
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, width, height)
    center_point: Tuple[int, int]
    area_pixels: int
    affected_cells: List[int]
    intensity_reduction: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert defect to dictionary"""
        return {
            'defect_id': self.defect_id,
            'defect_type': self.defect_type.value,
            'severity': self.severity.value,
            'confidence': float(self.confidence),
            'bounding_box': list(self.bounding_box),
            'center_point': list(self.center_point),
            'area_pixels': int(self.area_pixels),
            'affected_cells': self.affected_cells,
            'intensity_reduction': float(self.intensity_reduction),
            'metadata': self.metadata
        }


@dataclass
class ELImageData:
    """Container for EL image data and metadata"""
    raw_image: np.ndarray
    processed_image: np.ndarray
    dark_frame: Optional[np.ndarray] = None
    flat_field: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ELTestResult:
    """Complete EL test results"""
    test_id: str
    module_serial: str
    test_sequence: str
    timestamp: datetime
    defects: List[Defect]
    grade: Grade
    overall_intensity: float
    uniformity_cv: float
    image_paths: Dict[str, str]
    metrics: Dict[str, Any]
    qc_status: str
    nc_raised: bool
    comparison_data: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert result to dictionary"""
        return {
            'test_id': self.test_id,
            'module_serial': self.module_serial,
            'test_sequence': self.test_sequence,
            'timestamp': self.timestamp.isoformat(),
            'defects': [d.to_dict() for d in self.defects],
            'grade': self.grade.value,
            'overall_intensity': float(self.overall_intensity),
            'uniformity_cv': float(self.uniformity_cv),
            'image_paths': self.image_paths,
            'metrics': self.metrics,
            'qc_status': self.qc_status,
            'nc_raised': self.nc_raised,
            'comparison_data': self.comparison_data
        }


class ELImageProcessor:
    """Main EL image processing class"""

    def __init__(self, config: Dict):
        """
        Initialize EL image processor

        Args:
            config: Configuration dictionary from protocol JSON
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing EL Image Processor")

    def load_image(self, image_path: str, bit_depth: int = 16) -> np.ndarray:
        """
        Load EL image from file

        Args:
            image_path: Path to image file
            bit_depth: Expected bit depth (12, 14, or 16)

        Returns:
            Loaded image as numpy array
        """
        self.logger.info(f"Loading image: {image_path}")

        # Load image with appropriate bit depth
        if bit_depth == 16:
            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        else:
            img = cv2.imread(image_path, cv2.IMREAD_ANYDEPTH)

        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")

        # Convert to float for processing
        img = img.astype(np.float32)

        self.logger.info(f"Image loaded: shape={img.shape}, dtype={img.dtype}")
        return img

    def apply_dark_frame_subtraction(self, image: np.ndarray,
                                    dark_frame: np.ndarray) -> np.ndarray:
        """
        Subtract dark frame from image

        Args:
            image: Raw image
            dark_frame: Dark frame

        Returns:
            Dark-corrected image
        """
        self.logger.info("Applying dark frame subtraction")

        # Ensure shapes match
        if image.shape != dark_frame.shape:
            raise ValueError("Image and dark frame shapes must match")

        # Subtract with clipping to prevent negative values
        corrected = np.clip(image - dark_frame, 0, None)

        return corrected

    def apply_flat_field_correction(self, image: np.ndarray,
                                    flat_field: np.ndarray) -> np.ndarray:
        """
        Apply flat-field correction to compensate for vignetting

        Args:
            image: Dark-corrected image
            flat_field: Flat-field reference image

        Returns:
            Flat-field corrected image
        """
        self.logger.info("Applying flat-field correction")

        # Normalize flat field
        flat_normalized = flat_field / np.median(flat_field)

        # Avoid division by zero
        flat_normalized = np.where(flat_normalized < 0.1, 0.1, flat_normalized)

        # Apply correction
        corrected = image / flat_normalized

        return corrected

    def normalize_intensity(self, image: np.ndarray,
                           injection_current: float,
                           reference_current: float = 9.0) -> np.ndarray:
        """
        Normalize image intensity to reference current

        Args:
            image: Input image
            injection_current: Actual injection current used
            reference_current: Reference current for normalization

        Returns:
            Normalized image
        """
        self.logger.info(f"Normalizing intensity: {injection_current}A -> {reference_current}A")

        normalization_factor = reference_current / injection_current
        normalized = image * normalization_factor

        return normalized

    def enhance_contrast(self, image: np.ndarray,
                        method: str = "CLAHE") -> np.ndarray:
        """
        Enhance image contrast for better defect visibility

        Args:
            image: Input image
            method: Enhancement method ("CLAHE", "histogram_eq", "adaptive")

        Returns:
            Enhanced image
        """
        self.logger.info(f"Enhancing contrast using {method}")

        # Convert to 8-bit for CLAHE
        img_8bit = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        if method == "CLAHE":
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(img_8bit)
        elif method == "histogram_eq":
            enhanced = cv2.equalizeHist(img_8bit)
        else:
            enhanced = img_8bit

        # Convert back to float
        enhanced = enhanced.astype(np.float32) / 255.0

        return enhanced

    def reduce_noise(self, image: np.ndarray,
                    method: str = "bilateral") -> np.ndarray:
        """
        Apply noise reduction while preserving edges

        Args:
            image: Input image
            method: Noise reduction method

        Returns:
            Denoised image
        """
        self.logger.info(f"Reducing noise using {method}")

        if method == "bilateral":
            # Bilateral filter preserves edges
            denoised = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
        elif method == "gaussian":
            denoised = cv2.GaussianBlur(image, (5, 5), 0)
        elif method == "median":
            denoised = cv2.medianBlur(image.astype(np.uint8), 5)
        else:
            denoised = image

        return denoised

    def process_image(self, raw_image: np.ndarray,
                     dark_frame: Optional[np.ndarray] = None,
                     flat_field: Optional[np.ndarray] = None,
                     injection_current: float = 9.0,
                     enhance: bool = True) -> np.ndarray:
        """
        Complete image processing pipeline

        Args:
            raw_image: Raw EL image
            dark_frame: Optional dark frame
            flat_field: Optional flat field
            injection_current: Injection current used
            enhance: Apply enhancement steps

        Returns:
            Fully processed image
        """
        self.logger.info("Starting image processing pipeline")

        processed = raw_image.copy()

        # Dark frame subtraction
        if dark_frame is not None:
            processed = self.apply_dark_frame_subtraction(processed, dark_frame)

        # Flat-field correction
        if flat_field is not None:
            processed = self.apply_flat_field_correction(processed, flat_field)

        # Intensity normalization
        processed = self.normalize_intensity(processed, injection_current)

        # Enhancement steps
        if enhance:
            processed = self.reduce_noise(processed, method="bilateral")
            processed = self.enhance_contrast(processed, method="CLAHE")

        self.logger.info("Image processing pipeline complete")
        return processed

    def detect_defects_ml(self, image: np.ndarray,
                         model_config: Dict) -> List[Defect]:
        """
        ML-based defect detection (placeholder for actual ML model integration)

        Args:
            image: Processed image
            model_config: ML model configuration

        Returns:
            List of detected defects
        """
        self.logger.info("Running ML defect detection")

        # This is a placeholder for actual ML model integration
        # In production, this would call PyTorch/TensorFlow models

        defects = []

        # Simulate defect detection
        # In real implementation, load and run trained models
        # model = load_model(model_config['model_id'])
        # predictions = model.predict(image)
        # defects = parse_predictions(predictions)

        self.logger.info(f"Detected {len(defects)} defects")
        return defects

    def calculate_intensity_metrics(self, image: np.ndarray,
                                   cell_mask: Optional[np.ndarray] = None) -> Dict:
        """
        Calculate intensity distribution metrics

        Args:
            image: Processed EL image
            cell_mask: Optional mask defining cell regions

        Returns:
            Dictionary of metrics
        """
        self.logger.info("Calculating intensity metrics")

        if cell_mask is not None:
            masked_image = image[cell_mask > 0]
        else:
            masked_image = image.flatten()

        metrics = {
            'mean_intensity': float(np.mean(masked_image)),
            'median_intensity': float(np.median(masked_image)),
            'std_intensity': float(np.std(masked_image)),
            'min_intensity': float(np.min(masked_image)),
            'max_intensity': float(np.max(masked_image)),
            'coefficient_of_variation': float(np.std(masked_image) / np.mean(masked_image)),
            'uniformity': float(1.0 - np.std(masked_image) / np.mean(masked_image))
        }

        return metrics

    def classify_severity(self, defect: Defect,
                         classification_rules: Dict) -> SeverityLevel:
        """
        Classify defect severity based on rules

        Args:
            defect: Detected defect
            classification_rules: Classification rules from protocol

        Returns:
            Severity level
        """
        # Placeholder for rule-based severity classification
        # In production, implement based on classification_rules

        return SeverityLevel.MINOR

    def grade_module(self, defects: List[Defect],
                    grading_rules: Dict) -> Grade:
        """
        Grade module based on detected defects

        Args:
            defects: List of detected defects
            grading_rules: Grading criteria from protocol

        Returns:
            Module grade
        """
        self.logger.info("Grading module")

        # Count defects by severity
        critical_count = sum(1 for d in defects if d.severity == SeverityLevel.CRITICAL)
        severe_count = sum(1 for d in defects if d.severity == SeverityLevel.SEVERE)
        moderate_count = sum(1 for d in defects if d.severity == SeverityLevel.MODERATE)
        minor_count = sum(1 for d in defects if d.severity == SeverityLevel.MINOR)

        # Apply grading rules
        if critical_count > 0 or severe_count > 3:
            grade = Grade.F
        elif severe_count <= 3 and moderate_count <= 2 and minor_count <= 5:
            if severe_count == 0 and moderate_count == 0 and minor_count <= 2:
                grade = Grade.A
            elif severe_count == 0 and moderate_count <= 1 and minor_count <= 5:
                grade = Grade.B
            else:
                grade = Grade.C
        elif severe_count <= 3:
            grade = Grade.D
        else:
            grade = Grade.F

        self.logger.info(f"Module grade: {grade.value}")
        return grade

    def compare_images(self, pre_image: np.ndarray,
                      post_image: np.ndarray,
                      align: bool = True) -> Dict:
        """
        Compare pre-test and post-test images

        Args:
            pre_image: Pre-test EL image
            post_image: Post-test EL image
            align: Perform image alignment

        Returns:
            Comparison metrics and difference map
        """
        self.logger.info("Comparing pre/post images")

        if align:
            # Align images using feature-based registration
            post_aligned = self._align_images(pre_image, post_image)
        else:
            post_aligned = post_image

        # Calculate difference
        difference = post_image - pre_image
        abs_difference = np.abs(difference)

        # Calculate metrics
        correlation = np.corrcoef(pre_image.flatten(), post_aligned.flatten())[0, 1]

        # Structural Similarity Index (SSIM)
        ssim = self._calculate_ssim(pre_image, post_aligned)

        comparison = {
            'correlation_coefficient': float(correlation),
            'ssim': float(ssim),
            'mean_difference': float(np.mean(difference)),
            'max_difference': float(np.max(abs_difference)),
            'rms_difference': float(np.sqrt(np.mean(difference**2))),
            'difference_map': difference,
            'aligned_post_image': post_aligned
        }

        return comparison

    def _align_images(self, reference: np.ndarray,
                     target: np.ndarray) -> np.ndarray:
        """
        Align target image to reference using feature matching

        Args:
            reference: Reference image
            target: Image to align

        Returns:
            Aligned target image
        """
        # Convert to 8-bit for feature detection
        ref_8bit = cv2.normalize(reference, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        tgt_8bit = cv2.normalize(target, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Detect ORB features (faster than SIFT)
        orb = cv2.ORB_create(5000)
        kp1, des1 = orb.detectAndCompute(ref_8bit, None)
        kp2, des2 = orb.detectAndCompute(tgt_8bit, None)

        # Match features
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        # Extract matched points
        points1 = np.float32([kp1[m.queryIdx].pt for m in matches[:100]]).reshape(-1, 1, 2)
        points2 = np.float32([kp2[m.trainIdx].pt for m in matches[:100]]).reshape(-1, 1, 2)

        # Find homography
        H, mask = cv2.findHomography(points2, points1, cv2.RANSAC, 5.0)

        # Warp target image
        height, width = reference.shape[:2]
        aligned = cv2.warpPerspective(target, H, (width, height))

        return aligned

    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate Structural Similarity Index

        Args:
            img1: First image
            img2: Second image

        Returns:
            SSIM value
        """
        # Simple SSIM implementation
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2

        mu1 = cv2.GaussianBlur(img1, (11, 11), 1.5)
        mu2 = cv2.GaussianBlur(img2, (11, 11), 1.5)

        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2

        sigma1_sq = cv2.GaussianBlur(img1 ** 2, (11, 11), 1.5) - mu1_sq
        sigma2_sq = cv2.GaussianBlur(img2 ** 2, (11, 11), 1.5) - mu2_sq
        sigma12 = cv2.GaussianBlur(img1 * img2, (11, 11), 1.5) - mu1_mu2

        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
                   ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))

        return float(np.mean(ssim_map))

    def run_full_analysis(self,
                         raw_image_path: str,
                         dark_frame_path: Optional[str] = None,
                         flat_field_path: Optional[str] = None,
                         test_params: Dict = None,
                         module_serial: str = None,
                         test_sequence: str = "pre_test") -> ELTestResult:
        """
        Run complete EL analysis pipeline

        Args:
            raw_image_path: Path to raw EL image
            dark_frame_path: Path to dark frame
            flat_field_path: Path to flat field
            test_params: Test parameters
            module_serial: Module serial number
            test_sequence: Test sequence type

        Returns:
            Complete test results
        """
        self.logger.info(f"Starting full EL analysis for {module_serial}")

        # Load images
        raw_image = self.load_image(raw_image_path)
        dark_frame = self.load_image(dark_frame_path) if dark_frame_path else None
        flat_field = self.load_image(flat_field_path) if flat_field_path else None

        # Process image
        processed_image = self.process_image(
            raw_image,
            dark_frame,
            flat_field,
            injection_current=test_params.get('injection_current', 9.0)
        )

        # Detect defects
        ml_config = self.config.get('ai_ml_defect_detection', {})
        defects = self.detect_defects_ml(processed_image, ml_config)

        # Calculate metrics
        metrics = self.calculate_intensity_metrics(processed_image)

        # Grade module
        grading_rules = self.config.get('quality_control', {}).get('automated_grading', {})
        grade = self.grade_module(defects, grading_rules)

        # Determine QC status
        qc_status = "PASS" if grade in [Grade.A, Grade.B, Grade.C] else "FAIL"
        nc_raised = grade in [Grade.D, Grade.F]

        # Create result object
        result = ELTestResult(
            test_id=f"EL-{module_serial}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            module_serial=module_serial or "UNKNOWN",
            test_sequence=test_sequence,
            timestamp=datetime.now(),
            defects=defects,
            grade=grade,
            overall_intensity=metrics['mean_intensity'],
            uniformity_cv=metrics['coefficient_of_variation'],
            image_paths={
                'raw': raw_image_path,
                'processed': raw_image_path.replace('.tif', '_processed.tif')
            },
            metrics=metrics,
            qc_status=qc_status,
            nc_raised=nc_raised
        )

        self.logger.info(f"Analysis complete: Grade={grade.value}, Defects={len(defects)}")
        return result


# Example usage
if __name__ == "__main__":
    # Load protocol configuration
    protocol_path = Path(__file__).parent / "protocol.json"
    with open(protocol_path, 'r') as f:
        config = json.load(f)

    # Initialize processor
    processor = ELImageProcessor(config)

    # Run analysis (example)
    # result = processor.run_full_analysis(
    #     raw_image_path="/path/to/el_image.tif",
    #     dark_frame_path="/path/to/dark_frame.tif",
    #     test_params={'injection_current': 9.0},
    #     module_serial="MOD123456",
    #     test_sequence="pre_test"
    # )

    print("EL Image Processor initialized successfully")
