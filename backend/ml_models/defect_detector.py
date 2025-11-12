"""
AI/ML Defect Detection Framework
Unified framework for loading and running defect detection models
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """ML model types"""
    OBJECT_DETECTION = "object_detection"
    SEMANTIC_SEGMENTATION = "semantic_segmentation"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class Framework(Enum):
    """ML frameworks"""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    SCIKIT_LEARN = "scikit_learn"


@dataclass
class ModelConfig:
    """Model configuration"""
    model_id: str
    model_type: ModelType
    framework: Framework
    model_path: str
    input_size: Tuple[int, int]
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.45
    output_classes: List[str] = None
    preprocessing: Dict = None


@dataclass
class Detection:
    """Object detection result"""
    class_name: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, w, h
    mask: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None


@dataclass
class PredictionResult:
    """Model prediction result"""
    model_id: str
    model_type: ModelType
    detections: List[Detection] = None
    segmentation_mask: Optional[np.ndarray] = None
    classification: Optional[str] = None
    classification_confidence: Optional[float] = None
    regression_output: Optional[float] = None
    processing_time: float = 0.0


class ModelLoader:
    """Load ML models from various frameworks"""

    @staticmethod
    def load_model(config: ModelConfig) -> Any:
        """
        Load model based on framework

        Args:
            config: Model configuration

        Returns:
            Loaded model
        """
        logger.info(f"Loading model: {config.model_id} ({config.framework.value})")

        if config.framework == Framework.PYTORCH:
            return ModelLoader._load_pytorch_model(config)
        elif config.framework == Framework.TENSORFLOW:
            return ModelLoader._load_tensorflow_model(config)
        elif config.framework == Framework.ONNX:
            return ModelLoader._load_onnx_model(config)
        elif config.framework == Framework.SCIKIT_LEARN:
            return ModelLoader._load_sklearn_model(config)
        else:
            raise ValueError(f"Unsupported framework: {config.framework}")

    @staticmethod
    def _load_pytorch_model(config: ModelConfig) -> Any:
        """Load PyTorch model"""
        try:
            import torch
            model = torch.load(config.model_path)
            model.eval()
            return model
        except ImportError:
            logger.error("PyTorch not installed")
            return None

    @staticmethod
    def _load_tensorflow_model(config: ModelConfig) -> Any:
        """Load TensorFlow model"""
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(config.model_path)
            return model
        except ImportError:
            logger.error("TensorFlow not installed")
            return None

    @staticmethod
    def _load_onnx_model(config: ModelConfig) -> Any:
        """Load ONNX model"""
        try:
            import onnxruntime as ort
            model = ort.InferenceSession(config.model_path)
            return model
        except ImportError:
            logger.error("ONNX Runtime not installed")
            return None

    @staticmethod
    def _load_sklearn_model(config: ModelConfig) -> Any:
        """Load scikit-learn model"""
        try:
            import joblib
            model = joblib.load(config.model_path)
            return model
        except ImportError:
            logger.error("scikit-learn not installed")
            return None


class DefectDetector:
    """Unified defect detection interface"""

    def __init__(self, config: ModelConfig):
        """
        Initialize defect detector

        Args:
            config: Model configuration
        """
        self.config = config
        self.model = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def load(self) -> bool:
        """
        Load model

        Returns:
            Success status
        """
        try:
            self.model = ModelLoader.load_model(self.config)
            return self.model is not None
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input

        Args:
            image: Input image

        Returns:
            Preprocessed image
        """
        # Resize to model input size
        h, w = self.config.input_size
        resized = cv2.resize(image, (w, h))

        # Apply preprocessing from config
        if self.config.preprocessing:
            if self.config.preprocessing.get('normalize'):
                resized = resized.astype(np.float32) / 255.0

            if self.config.preprocessing.get('standardize'):
                mean = self.config.preprocessing.get('mean', [0.5, 0.5, 0.5])
                std = self.config.preprocessing.get('std', [0.5, 0.5, 0.5])
                resized = (resized - mean) / std

        return resized

    def predict(self, image: np.ndarray) -> PredictionResult:
        """
        Run inference on image

        Args:
            image: Input image

        Returns:
            Prediction result
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        import time
        start_time = time.time()

        # Preprocess
        preprocessed = self.preprocess(image)

        # Run inference based on model type
        if self.config.model_type == ModelType.OBJECT_DETECTION:
            result = self._predict_object_detection(preprocessed, image.shape)
        elif self.config.model_type == ModelType.SEMANTIC_SEGMENTATION:
            result = self._predict_segmentation(preprocessed, image.shape)
        elif self.config.model_type == ModelType.CLASSIFICATION:
            result = self._predict_classification(preprocessed)
        elif self.config.model_type == ModelType.REGRESSION:
            result = self._predict_regression(preprocessed)
        else:
            raise ValueError(f"Unsupported model type: {self.config.model_type}")

        result.processing_time = time.time() - start_time
        return result

    def _predict_object_detection(self, image: np.ndarray,
                                  original_shape: Tuple) -> PredictionResult:
        """Run object detection inference"""
        # Placeholder for actual inference
        # In production, this would call the loaded model
        detections = []

        # Example: Parse model output and create Detection objects
        # boxes, scores, class_ids = self.model(image)
        # for box, score, class_id in zip(boxes, scores, class_ids):
        #     if score > self.config.confidence_threshold:
        #         detection = Detection(
        #             class_name=self.config.output_classes[class_id],
        #             confidence=float(score),
        #             bounding_box=tuple(box)
        #         )
        #         detections.append(detection)

        return PredictionResult(
            model_id=self.config.model_id,
            model_type=self.config.model_type,
            detections=detections
        )

    def _predict_segmentation(self, image: np.ndarray,
                             original_shape: Tuple) -> PredictionResult:
        """Run semantic segmentation inference"""
        # Placeholder for actual inference
        # mask = self.model(image)

        return PredictionResult(
            model_id=self.config.model_id,
            model_type=self.config.model_type,
            segmentation_mask=None  # Would be actual mask
        )

    def _predict_classification(self, image: np.ndarray) -> PredictionResult:
        """Run classification inference"""
        # Placeholder for actual inference
        # probabilities = self.model(image)
        # class_id = np.argmax(probabilities)
        # confidence = probabilities[class_id]

        return PredictionResult(
            model_id=self.config.model_id,
            model_type=self.config.model_type,
            classification=None,  # Would be actual class
            classification_confidence=0.0
        )

    def _predict_regression(self, image: np.ndarray) -> PredictionResult:
        """Run regression inference"""
        # Placeholder for actual inference
        # output = self.model(image)

        return PredictionResult(
            model_id=self.config.model_id,
            model_type=self.config.model_type,
            regression_output=0.0  # Would be actual output
        )


class EnsembleDetector:
    """Ensemble multiple models for improved accuracy"""

    def __init__(self, detectors: List[DefectDetector],
                 weights: Optional[List[float]] = None):
        """
        Initialize ensemble detector

        Args:
            detectors: List of defect detectors
            weights: Optional weights for each detector
        """
        self.detectors = detectors
        self.weights = weights if weights else [1.0] * len(detectors)
        self.logger = logging.getLogger(self.__class__.__name__)

    def predict(self, image: np.ndarray,
               method: str = 'weighted_voting') -> PredictionResult:
        """
        Run ensemble prediction

        Args:
            image: Input image
            method: Ensemble method ('weighted_voting', 'max_confidence', 'union')

        Returns:
            Combined prediction result
        """
        # Get predictions from all models
        predictions = [detector.predict(image) for detector in self.detectors]

        if method == 'weighted_voting':
            return self._weighted_voting(predictions)
        elif method == 'max_confidence':
            return self._max_confidence(predictions)
        elif method == 'union':
            return self._union(predictions)
        else:
            raise ValueError(f"Unknown ensemble method: {method}")

    def _weighted_voting(self, predictions: List[PredictionResult]) -> PredictionResult:
        """Combine predictions using weighted voting"""
        # Placeholder implementation
        # In production, properly combine detection results
        return predictions[0] if predictions else None

    def _max_confidence(self, predictions: List[PredictionResult]) -> PredictionResult:
        """Select prediction with maximum confidence"""
        if not predictions:
            return None

        # Find prediction with highest confidence
        max_pred = max(predictions,
                      key=lambda p: max([d.confidence for d in (p.detections or [])],
                                      default=0.0))
        return max_pred

    def _union(self, predictions: List[PredictionResult]) -> PredictionResult:
        """Combine all detections (union)"""
        # Combine all detections from all models
        all_detections = []
        for pred in predictions:
            if pred.detections:
                all_detections.extend(pred.detections)

        # Apply NMS to remove duplicates
        # filtered_detections = self._apply_nms(all_detections)

        return PredictionResult(
            model_id="ensemble",
            model_type=ModelType.OBJECT_DETECTION,
            detections=all_detections
        )


class ModelRegistry:
    """Registry for managing multiple models"""

    def __init__(self):
        self.models: Dict[str, DefectDetector] = {}
        self.configs: Dict[str, ModelConfig] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_model(self, config: ModelConfig) -> bool:
        """
        Register a model

        Args:
            config: Model configuration

        Returns:
            Success status
        """
        try:
            detector = DefectDetector(config)
            if detector.load():
                self.models[config.model_id] = detector
                self.configs[config.model_id] = config
                self.logger.info(f"Registered model: {config.model_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to register model {config.model_id}: {e}")
            return False

    def get_detector(self, model_id: str) -> Optional[DefectDetector]:
        """Get detector by ID"""
        return self.models.get(model_id)

    def list_models(self) -> List[str]:
        """List all registered model IDs"""
        return list(self.models.keys())

    def load_from_config_file(self, config_path: str) -> int:
        """
        Load multiple models from JSON config file

        Args:
            config_path: Path to JSON configuration

        Returns:
            Number of models loaded
        """
        with open(config_path, 'r') as f:
            config_data = json.load(f)

        count = 0
        for model_cfg in config_data.get('models', []):
            config = ModelConfig(
                model_id=model_cfg['model_id'],
                model_type=ModelType(model_cfg['type']),
                framework=Framework(model_cfg['framework']),
                model_path=model_cfg['model_path'],
                input_size=tuple(model_cfg['input_size']),
                confidence_threshold=model_cfg.get('confidence_threshold', 0.5),
                output_classes=model_cfg.get('output_classes', []),
                preprocessing=model_cfg.get('preprocessing', {})
            )
            if self.register_model(config):
                count += 1

        self.logger.info(f"Loaded {count} models from config file")
        return count


# Global registry instance
model_registry = ModelRegistry()


if __name__ == "__main__":
    print("AI/ML Defect Detection Framework initialized")
    print(f"Available model types: {[t.value for t in ModelType]}")
    print(f"Supported frameworks: {[f.value for f in Framework]}")
