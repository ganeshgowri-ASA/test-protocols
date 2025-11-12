"""
Shared Image Processing Backend Library
Common image processing functions for all imaging protocols
"""

import numpy as np
import cv2
from typing import Tuple, Optional, Dict, List
from pathlib import Path
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ImageMetadata:
    """Image metadata container"""
    width: int
    height: int
    channels: int
    dtype: str
    bit_depth: int
    format: str
    timestamp: str
    camera_settings: Dict = None


class ImageProcessor:
    """Base image processor with common operations"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_image(self, path: str, mode: str = 'auto') -> Tuple[np.ndarray, ImageMetadata]:
        """
        Load image with automatic format detection

        Args:
            path: Image file path
            mode: Loading mode ('auto', 'grayscale', 'color', 'unchanged')

        Returns:
            Image array and metadata
        """
        self.logger.info(f"Loading image: {path}")

        if mode == 'grayscale':
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        elif mode == 'color':
            img = cv2.imread(path, cv2.IMREAD_COLOR)
        elif mode == 'unchanged':
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        else:  # auto
            img = cv2.imread(path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)

        if img is None:
            raise FileNotFoundError(f"Failed to load image: {path}")

        # Extract metadata
        metadata = ImageMetadata(
            width=img.shape[1],
            height=img.shape[0],
            channels=1 if len(img.shape) == 2 else img.shape[2],
            dtype=str(img.dtype),
            bit_depth=img.dtype.itemsize * 8,
            format=Path(path).suffix,
            timestamp=""
        )

        return img, metadata

    def save_image(self, image: np.ndarray, path: str,
                   compression: Optional[Dict] = None) -> bool:
        """
        Save image with optional compression

        Args:
            image: Image array
            path: Output path
            compression: Compression parameters

        Returns:
            Success status
        """
        self.logger.info(f"Saving image: {path}")

        if compression is None:
            compression = {}

        # Set default compression based on format
        ext = Path(path).suffix.lower()
        if ext == '.png' and 'PNG_COMPRESSION' not in compression:
            compression = [cv2.IMWRITE_PNG_COMPRESSION, 3]
        elif ext == '.jpg' and 'JPEG_QUALITY' not in compression:
            compression = [cv2.IMWRITE_JPEG_QUALITY, 95]
        elif ext == '.tiff':
            compression = []

        success = cv2.imwrite(path, image, compression)
        return success

    def normalize_image(self, image: np.ndarray,
                       method: str = 'minmax',
                       target_range: Tuple[float, float] = (0.0, 1.0)) -> np.ndarray:
        """
        Normalize image intensity

        Args:
            image: Input image
            method: Normalization method ('minmax', 'zscore', 'percentile')
            target_range: Target intensity range

        Returns:
            Normalized image
        """
        if method == 'minmax':
            imin, imax = np.min(image), np.max(image)
            if imin == imax:
                return np.full_like(image, target_range[0], dtype=np.float32)
            normalized = (image - imin) / (imax - imin)
            normalized = normalized * (target_range[1] - target_range[0]) + target_range[0]

        elif method == 'zscore':
            mean, std = np.mean(image), np.std(image)
            normalized = (image - mean) / (std + 1e-7)

        elif method == 'percentile':
            p1, p99 = np.percentile(image, [1, 99])
            normalized = np.clip((image - p1) / (p99 - p1 + 1e-7), 0, 1)
            normalized = normalized * (target_range[1] - target_range[0]) + target_range[0]

        else:
            raise ValueError(f"Unknown normalization method: {method}")

        return normalized.astype(np.float32)

    def apply_clahe(self, image: np.ndarray,
                   clip_limit: float = 2.0,
                   tile_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
        """
        Apply Contrast Limited Adaptive Histogram Equalization

        Args:
            image: Input image
            clip_limit: Contrast clipping threshold
            tile_size: Size of tiles for local equalization

        Returns:
            Enhanced image
        """
        # Convert to uint8 if needed
        if image.dtype != np.uint8:
            img_8bit = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        else:
            img_8bit = image

        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)

        if len(img_8bit.shape) == 2:
            enhanced = clahe.apply(img_8bit)
        else:
            # Apply to each channel
            channels = cv2.split(img_8bit)
            enhanced_channels = [clahe.apply(ch) for ch in channels]
            enhanced = cv2.merge(enhanced_channels)

        return enhanced

    def denoise(self, image: np.ndarray,
               method: str = 'bilateral',
               **kwargs) -> np.ndarray:
        """
        Apply denoising filter

        Args:
            image: Input image
            method: Denoising method ('bilateral', 'gaussian', 'median', 'nlm')
            **kwargs: Method-specific parameters

        Returns:
            Denoised image
        """
        if method == 'bilateral':
            d = kwargs.get('d', 9)
            sigma_color = kwargs.get('sigma_color', 75)
            sigma_space = kwargs.get('sigma_space', 75)
            return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

        elif method == 'gaussian':
            ksize = kwargs.get('ksize', (5, 5))
            sigma = kwargs.get('sigma', 0)
            return cv2.GaussianBlur(image, ksize, sigma)

        elif method == 'median':
            ksize = kwargs.get('ksize', 5)
            return cv2.medianBlur(image, ksize)

        elif method == 'nlm':
            h = kwargs.get('h', 10)
            template_window_size = kwargs.get('template_window_size', 7)
            search_window_size = kwargs.get('search_window_size', 21)
            return cv2.fastNlMeansDenoising(image, None, h,
                                           template_window_size,
                                           search_window_size)

        else:
            raise ValueError(f"Unknown denoising method: {method}")

    def detect_edges(self, image: np.ndarray,
                    method: str = 'canny',
                    **kwargs) -> np.ndarray:
        """
        Detect edges in image

        Args:
            image: Input image
            method: Edge detection method ('canny', 'sobel', 'laplacian')
            **kwargs: Method-specific parameters

        Returns:
            Edge map
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        if method == 'canny':
            threshold1 = kwargs.get('threshold1', 50)
            threshold2 = kwargs.get('threshold2', 150)
            return cv2.Canny(gray, threshold1, threshold2)

        elif method == 'sobel':
            ksize = kwargs.get('ksize', 3)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        elif method == 'laplacian':
            ksize = kwargs.get('ksize', 3)
            return cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize)

        else:
            raise ValueError(f"Unknown edge detection method: {method}")

    def register_images(self, reference: np.ndarray,
                       target: np.ndarray,
                       method: str = 'feature') -> Tuple[np.ndarray, np.ndarray]:
        """
        Align target image to reference image

        Args:
            reference: Reference image
            target: Image to align
            method: Registration method ('feature', 'ecc', 'phase')

        Returns:
            Aligned image and transformation matrix
        """
        if method == 'feature':
            return self._register_feature_based(reference, target)
        elif method == 'ecc':
            return self._register_ecc(reference, target)
        else:
            raise ValueError(f"Unknown registration method: {method}")

    def _register_feature_based(self, ref: np.ndarray,
                                target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Feature-based image registration using ORB"""
        # Convert to grayscale
        ref_gray = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY) if len(ref.shape) == 3 else ref
        tgt_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY) if len(target.shape) == 3 else target

        # Detect ORB features
        orb = cv2.ORB_create(5000)
        kp1, des1 = orb.detectAndCompute(ref_gray, None)
        kp2, des2 = orb.detectAndCompute(tgt_gray, None)

        # Match features
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        # Extract points
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches[:100]]).reshape(-1, 1, 2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches[:100]]).reshape(-1, 1, 2)

        # Find homography
        H, mask = cv2.findHomography(pts2, pts1, cv2.RANSAC, 5.0)

        # Warp target image
        h, w = ref.shape[:2]
        aligned = cv2.warpPerspective(target, H, (w, h))

        return aligned, H

    def _register_ecc(self, ref: np.ndarray,
                     target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """ECC-based image registration"""
        # Convert to grayscale
        ref_gray = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY) if len(ref.shape) == 3 else ref
        tgt_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY) if len(target.shape) == 3 else target

        # Define motion model (affine)
        warp_matrix = np.eye(2, 3, dtype=np.float32)

        # Define termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 5000, 1e-6)

        # Run ECC algorithm
        try:
            cc, warp_matrix = cv2.findTransformECC(ref_gray, tgt_gray, warp_matrix,
                                                   cv2.MOTION_AFFINE, criteria)

            # Warp target image
            h, w = ref.shape[:2]
            aligned = cv2.warpAffine(target, warp_matrix, (w, h),
                                    flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

            return aligned, warp_matrix

        except cv2.error as e:
            self.logger.warning(f"ECC registration failed: {e}")
            return target, np.eye(2, 3, dtype=np.float32)

    def calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate Structural Similarity Index

        Args:
            img1: First image
            img2: Second image

        Returns:
            SSIM value (0-1)
        """
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2

        # Convert to float
        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)

        # Calculate means
        mu1 = cv2.GaussianBlur(img1, (11, 11), 1.5)
        mu2 = cv2.GaussianBlur(img2, (11, 11), 1.5)

        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2

        # Calculate variances and covariance
        sigma1_sq = cv2.GaussianBlur(img1 ** 2, (11, 11), 1.5) - mu1_sq
        sigma2_sq = cv2.GaussianBlur(img2 ** 2, (11, 11), 1.5) - mu2_sq
        sigma12 = cv2.GaussianBlur(img1 * img2, (11, 11), 1.5) - mu1_mu2

        # Calculate SSIM
        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
                   ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))

        return float(np.mean(ssim_map))

    def morphological_operation(self, image: np.ndarray,
                               operation: str,
                               kernel_size: Tuple[int, int] = (5, 5),
                               kernel_shape: str = 'rect',
                               iterations: int = 1) -> np.ndarray:
        """
        Apply morphological operation

        Args:
            image: Input binary or grayscale image
            operation: Operation type ('erode', 'dilate', 'open', 'close', 'gradient')
            kernel_size: Kernel size
            kernel_shape: Kernel shape ('rect', 'ellipse', 'cross')
            iterations: Number of iterations

        Returns:
            Processed image
        """
        # Create kernel
        if kernel_shape == 'rect':
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        elif kernel_shape == 'ellipse':
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)
        elif kernel_shape == 'cross':
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, kernel_size)
        else:
            raise ValueError(f"Unknown kernel shape: {kernel_shape}")

        # Apply operation
        if operation == 'erode':
            return cv2.erode(image, kernel, iterations=iterations)
        elif operation == 'dilate':
            return cv2.dilate(image, kernel, iterations=iterations)
        elif operation == 'open':
            return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
        elif operation == 'close':
            return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        elif operation == 'gradient':
            return cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)
        else:
            raise ValueError(f"Unknown morphological operation: {operation}")


# Convenience functions
def load_image(path: str, mode: str = 'auto') -> np.ndarray:
    """Quick image loading"""
    processor = ImageProcessor()
    img, _ = processor.load_image(path, mode)
    return img


def save_image(image: np.ndarray, path: str) -> bool:
    """Quick image saving"""
    processor = ImageProcessor()
    return processor.save_image(image, path)


if __name__ == "__main__":
    print("Image Processing Library initialized")
    processor = ImageProcessor()
    print(f"Available methods: {[m for m in dir(processor) if not m.startswith('_')]}")
