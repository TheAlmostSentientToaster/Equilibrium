import pytest
import numpy as np
import cv2
from unittest.mock import patch, MagicMock

from domain.domain_services.image_processing_service import ImageProcessingService


class TestImageProcessingService:

    def test_service_initialization(self):
        """Test that service is properly initialized"""
        service = ImageProcessingService()
        assert service is not None
        assert hasattr(service, 'preprocess')

    def test_preprocess_with_valid_image_bytes(self):
        """Test preprocessing with valid image bytes"""
        # Create a simple test image (3x3 RGB)
        test_image = np.array([
            [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
            [[255, 255, 0], [255, 0, 255], [0, 255, 255]],
            [[128, 128, 128], [64, 64, 64], [32, 32, 32]]
        ], dtype=np.uint8)
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', test_image)
        image_bytes = buffer.tobytes()
        
        service = ImageProcessingService()
        result = service.preprocess(image_bytes)
        
        # Verify result is a numpy array
        assert isinstance(result, np.ndarray)
        # Verify result is 2D (grayscale)
        assert len(result.shape) == 2
        # Verify result contains values in expected range (0 or 255 for thresholded)
        unique_values = np.unique(result)
        assert len(unique_values) <= 2
        assert all(val in [0, 255] for val in unique_values)

    def test_preprocess_with_png_image_bytes(self):
        """Test preprocessing with PNG image bytes"""
        # Create a simple test image
        test_image = np.array([
            [[100, 150, 200], [50, 75, 100]],
            [[25, 50, 75], [200, 150, 100]]
        ], dtype=np.uint8)
        
        # Convert to PNG bytes
        _, buffer = cv2.imencode('.png', test_image)
        image_bytes = buffer.tobytes()
        
        service = ImageProcessingService()
        result = service.preprocess(image_bytes)
        
        # Verify result properties
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2

    def test_preprocess_with_grayscale_image(self):
        """Test preprocessing with already grayscale image"""
        # Create a grayscale test image
        test_image = np.array([
            [100, 150, 200],
            [50, 75, 100],
            [25, 50, 75]
        ], dtype=np.uint8)
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', test_image)
        image_bytes = buffer.tobytes()
        
        service = ImageProcessingService()
        result = service.preprocess(image_bytes)
        
        # Verify result is thresholded
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2
        unique_values = np.unique(result)
        assert len(unique_values) <= 2

    def test_preprocess_with_large_image(self):
        """Test preprocessing with a larger image"""
        # Create a larger test image (100x100)
        test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', test_image)
        image_bytes = buffer.tobytes()
        
        service = ImageProcessingService()
        result = service.preprocess(image_bytes)
        
        # Verify result dimensions
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2
        assert result.shape == (100, 100)

    def test_preprocess_with_uniform_image(self):
        """Test preprocessing with uniform color image"""
        # Create a uniform gray image
        test_image = np.full((50, 50, 3), [128, 128, 128], dtype=np.uint8)
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', test_image)
        image_bytes = buffer.tobytes()
        
        service = ImageProcessingService()
        result = service.preprocess(image_bytes)
        
        # Verify result
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2

    def test_preprocess_with_empty_bytes(self):
        """Test preprocessing with empty bytes"""
        service = ImageProcessingService()
        
        with pytest.raises((ValueError, cv2.error)):
            service.preprocess(b'')

    def test_preprocess_pipeline_steps(self):
        """Test that the preprocessing pipeline works correctly"""
        # Create a test image with clear features
        test_image = np.array([
            [[255, 255, 255], [0, 0, 0], [255, 255, 255]],
            [[0, 0, 0], [128, 128, 128], [0, 0, 0]],
            [[255, 255, 255], [0, 0, 0], [255, 255, 255]]
        ], dtype=np.uint8)
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', test_image)
        image_bytes = buffer.tobytes()
        
        service = ImageProcessingService()
        result = service.preprocess(image_bytes)
        
        # The result should be a thresholded binary image
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2
        # Should contain only 0 and 255 values after adaptive threshold
        unique_values = np.unique(result)
        assert set(unique_values).issubset({0, 255})

    def test_preprocess_output_consistency(self):
        """Test that preprocess produces consistent results"""
        # Create a test image
        test_image = np.random.randint(0, 256, (30, 30, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', test_image)
        image_bytes = buffer.tobytes()
        
        service = ImageProcessingService()
        
        # Process the same image multiple times
        result1 = service.preprocess(image_bytes)
        result2 = service.preprocess(image_bytes)
        
        # Results should be identical
        assert np.array_equal(result1, result2)

    def test_preprocess_different_image_formats(self):
        """Test preprocessing with different image formats"""
        # Create test image
        test_image = np.array([
            [[100, 150, 200], [50, 75, 100]],
            [[25, 50, 75], [200, 150, 100]]
        ], dtype=np.uint8)
        
        service = ImageProcessingService()
        
        # Test JPEG
        _, jpeg_buffer = cv2.imencode('.jpg', test_image)
        jpeg_result = service.preprocess(jpeg_buffer.tobytes())
        
        # Test PNG
        _, png_buffer = cv2.imencode('.png', test_image)
        png_result = service.preprocess(png_buffer.tobytes())
        
        # Both should produce valid results
        assert isinstance(jpeg_result, np.ndarray)
        assert isinstance(png_result, np.ndarray)
        assert len(jpeg_result.shape) == 2
        assert len(png_result.shape) == 2

    def test_preprocess_with_high_contrast_image(self):
        """Test preprocessing with high contrast image"""
        # Create high contrast image
        test_image = np.array([
            [[0, 0, 0], [255, 255, 255]],
            [[255, 255, 255], [0, 0, 0]]
        ], dtype=np.uint8)
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', test_image)
        image_bytes = buffer.tobytes()
        
        service = ImageProcessingService()
        result = service.preprocess(image_bytes)
        
        # Verify result
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2
        unique_values = np.unique(result)
        assert set(unique_values).issubset({0, 255})
