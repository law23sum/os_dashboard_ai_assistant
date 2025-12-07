"""
Image Processing Integration

Handles image processing, analysis, and manipulation
"""

import os
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging
import base64
import io

try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

from config.logging_config import setup_logger

logger = setup_logger(__name__)


class ImageIntegration:
    """Image processing and analysis integration"""

    def __init__(self):
        self.logger = setup_logger("ImageIntegration")

    def is_available(self) -> Dict[str, bool]:
        """Check which image libraries are available"""
        return {
            "pil": PIL_AVAILABLE,
            "opencv": OPENCV_AVAILABLE
        }

    # Image Loading and Processing

    def load_image(self, image_path: str) -> Optional[Any]:
        """Load image from file"""
        try:
            if not PIL_AVAILABLE:
                return None

            return Image.open(image_path)

        except Exception as e:
            self.logger.error(f"Image loading failed: {e}")
            return None

    def load_image_from_bytes(self, image_bytes: bytes) -> Optional[Any]:
        """Load image from bytes"""
        try:
            if not PIL_AVAILABLE:
                return None

            return Image.open(io.BytesIO(image_bytes))

        except Exception as e:
            self.logger.error(f"Image loading from bytes failed: {e}")
            return None

    def save_image(self, image: Any, output_path: str,
                  format: Optional[str] = None, quality: int = 85) -> bool:
        """Save image to file"""
        try:
            if not PIL_AVAILABLE:
                return False

            # Determine format from extension if not specified
            if not format:
                ext = Path(output_path).suffix.lower()
                format_map = {
                    '.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG',
                    '.bmp': 'BMP', '.tiff': 'TIFF', '.gif': 'GIF'
                }
                format = format_map.get(ext, 'PNG')

            # Save with appropriate settings
            if format.upper() == 'JPEG':
                image.save(output_path, format, quality=quality, optimize=True)
            else:
                image.save(output_path, format)

            return True

        except Exception as e:
            self.logger.error(f"Image saving failed: {e}")
            return False

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """Get image metadata and information"""
        try:
            if not PIL_AVAILABLE:
                return {"error": "PIL not available"}

            with Image.open(image_path) as img:
                info = {
                    "filename": Path(image_path).name,
                    "format": img.format,
                    "size": img.size,  # (width, height)
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "aspect_ratio": img.width / img.height if img.height > 0 else 0,
                    "file_size": os.path.getsize(image_path),
                    "has_transparency": 'A' in img.mode or img.mode == 'P'
                }

                # Add EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    info["exif"] = {
                        "camera": exif_data.get(271),  # Make
                        "model": exif_data.get(272),   # Model
                        "datetime": exif_data.get(306)  # DateTime
                    }

                return info

        except Exception as e:
            self.logger.error(f"Image info extraction failed: {e}")
            return {"error": str(e)}

    # Image Manipulation

    def resize_image(self, image: Any, width: int, height: int,
                    maintain_aspect: bool = True) -> Any:
        """Resize image"""
        try:
            if not PIL_AVAILABLE:
                return image

            if maintain_aspect:
                # Calculate new dimensions maintaining aspect ratio
                img_width, img_height = image.size
                aspect_ratio = img_width / img_height

                if width / height > aspect_ratio:
                    # Height is the limiting factor
                    new_width = int(height * aspect_ratio)
                    new_height = height
                else:
                    # Width is the limiting factor
                    new_width = width
                    new_height = int(width / aspect_ratio)

                return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                return image.resize((width, height), Image.Resampling.LANCZOS)

        except Exception as e:
            self.logger.error(f"Image resize failed: {e}")
            return image

    def crop_image(self, image: Any, left: int, top: int,
                  right: int, bottom: int) -> Any:
        """Crop image"""
        try:
            if not PIL_AVAILABLE:
                return image

            return image.crop((left, top, right, bottom))

        except Exception as e:
            self.logger.error(f"Image crop failed: {e}")
            return image

    def rotate_image(self, image: Any, angle: float, expand: bool = True) -> Any:
        """Rotate image"""
        try:
            if not PIL_AVAILABLE:
                return image

            return image.rotate(angle, expand=expand)

        except Exception as e:
            self.logger.error(f"Image rotation failed: {e}")
            return image

    def adjust_brightness(self, image: Any, factor: float) -> Any:
        """Adjust image brightness"""
        try:
            if not PIL_AVAILABLE:
                return image

            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(factor)

        except Exception as e:
            self.logger.error(f"Brightness adjustment failed: {e}")
            return image

    def adjust_contrast(self, image: Any, factor: float) -> Any:
        """Adjust image contrast"""
        try:
            if not PIL_AVAILABLE:
                return image

            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)

        except Exception as e:
            self.logger.error(f"Contrast adjustment failed: {e}")
            return image

    def convert_to_grayscale(self, image: Any) -> Any:
        """Convert image to grayscale"""
        try:
            if not PIL_AVAILABLE:
                return image

            return image.convert('L')

        except Exception as e:
            self.logger.error(f"Grayscale conversion failed: {e}")
            return image

    def apply_filter(self, image: Any, filter_type: str) -> Any:
        """Apply filter to image"""
        try:
            if not PIL_AVAILABLE:
                return image

            filters = {
                'blur': ImageFilter.BLUR,
                'sharpen': ImageFilter.UnsharpMask,
                'smooth': ImageFilter.SMOOTH,
                'edge_enhance': ImageFilter.EDGE_ENHANCE
            }

            if filter_type in filters:
                return image.filter(filters[filter_type])

            return image

        except Exception as e:
            self.logger.error(f"Filter application failed: {e}")
            return image

    # Image Analysis

    def analyze_image_colors(self, image: Any, num_colors: int = 10) -> Dict[str, Any]:
        """Analyze dominant colors in image"""
        try:
            if not PIL_AVAILABLE:
                return {"error": "PIL not available"}

            # Resize for faster processing
            small_img = image.resize((100, 100), Image.Resampling.LANCZOS)

            # Get color palette
            colors = small_img.getcolors(100 * 100)
            if not colors:
                return {"error": "Could not extract colors"}

            # Sort by frequency
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)

            dominant_colors = []
            for count, color in sorted_colors[:num_colors]:
                percentage = (count / (100 * 100)) * 100
                dominant_colors.append({
                    "color": color,
                    "count": count,
                    "percentage": round(percentage, 2)
                })

            return {
                "dominant_colors": dominant_colors,
                "total_pixels": 100 * 100
            }

        except Exception as e:
            self.logger.error(f"Color analysis failed: {e}")
            return {"error": str(e)}

    def detect_image_quality(self, image: Any) -> Dict[str, Any]:
        """Detect image quality metrics"""
        try:
            if not PIL_AVAILABLE:
                return {"error": "PIL not available"}

            quality = {
                "resolution": image.size,
                "file_size": getattr(image, 'filename', None),
                "mode": image.mode,
                "sharpness": 0.0,
                "brightness": 0.0,
                "contrast": 0.0
            }

            # Calculate basic quality metrics
            if image.mode == 'RGB':
                # Convert to grayscale for analysis
                gray_img = image.convert('L')
                pixels = list(gray_img.getdata())

                # Brightness (average pixel value)
                quality["brightness"] = sum(pixels) / len(pixels) / 255.0

                # Contrast (standard deviation)
                mean = sum(pixels) / len(pixels)
                variance = sum((pixel - mean) ** 2 for pixel in pixels) / len(pixels)
                quality["contrast"] = (variance ** 0.5) / 128.0  # Normalized

                # Simple sharpness measure (edge detection)
                edges = 0
                width, height = gray_img.size
                for y in range(1, height - 1):
                    for x in range(1, width - 1):
                        # Simple edge detection
                        center = gray_img.getpixel((x, y))
                        neighbors = [
                            gray_img.getpixel((x-1, y)),
                            gray_img.getpixel((x+1, y)),
                            gray_img.getpixel((x, y-1)),
                            gray_img.getpixel((x, y+1))
                        ]
                        if any(abs(center - neighbor) > 20 for neighbor in neighbors):
                            edges += 1

                quality["sharpness"] = edges / (width * height)

            # Overall quality score
            quality["overall_score"] = (
                quality["brightness"] * 0.3 +
                min(quality["contrast"], 1.0) * 0.3 +
                quality["sharpness"] * 0.4
            )

            return quality

        except Exception as e:
            self.logger.error(f"Quality detection failed: {e}")
            return {"error": str(e)}

    def extract_text_from_image(self, image: Any) -> str:
        """Extract text from image using OCR (if available)"""
        try:
            # This would use Tesseract OCR if available
            # For now, return empty string as OCR requires additional setup
            self.logger.info("OCR not configured - text extraction requires Tesseract")
            return ""
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return ""

    # OpenCV-based Operations

    def detect_edges_cv2(self, image_path: str, output_path: str) -> bool:
        """Detect edges using OpenCV"""
        try:
            if not OPENCV_AVAILABLE:
                return False

            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return False

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)

            # Detect edges using Canny
            edges = cv2.Canny(blurred, 50, 150)

            # Save result
            cv2.imwrite(output_path, edges)
            return True

        except Exception as e:
            self.logger.error(f"Edge detection failed: {e}")
            return False

    def detect_faces_cv2(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect faces using OpenCV"""
        try:
            if not OPENCV_AVAILABLE:
                return []

            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return []

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Load face cascade
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            face_data = []
            for (x, y, w, h) in faces:
                face_data.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "confidence": 0.8
                })

            return face_data

        except Exception as e:
            self.logger.error(f"Face detection failed: {e}")
            return []

    # Batch Operations

    def batch_resize(self, image_paths: List[str], output_dir: str,
                    width: int, height: int, maintain_aspect: bool = True) -> List[str]:
        """Batch resize images"""
        try:
            if not PIL_AVAILABLE:
                return []

            output_paths = []

            for img_path in image_paths:
                try:
                    img = self.load_image(img_path)
                    if img:
                        resized = self.resize_image(img, width, height, maintain_aspect)

                        filename = Path(img_path).name
                        output_path = os.path.join(output_dir, f"resized_{filename}")
                        self.save_image(resized, output_path)

                        output_paths.append(output_path)

                except Exception as e:
                    self.logger.error(f"Failed to resize {img_path}: {e}")

            return output_paths

        except Exception as e:
            self.logger.error(f"Batch resize failed: {e}")
            return []

    def create_image_montage(self, image_paths: List[str], output_path: str,
                            cols: int = 3, padding: int = 10) -> bool:
        """Create image montage"""
        try:
            if not PIL_AVAILABLE or not image_paths:
                return False

            # Load all images
            images = []
            max_width = 0
            max_height = 0

            for img_path in image_paths:
                img = self.load_image(img_path)
                if img:
                    images.append(img)
                    max_width = max(max_width, img.width)
                    max_height = max(max_height, img.height)

            if not images:
                return False

            # Calculate montage dimensions
            rows = (len(images) + cols - 1) // cols
            montage_width = cols * (max_width + padding) - padding
            montage_height = rows * (max_height + padding) - padding

            # Create montage
            montage = Image.new('RGB', (montage_width, montage_height), 'white')

            for idx, img in enumerate(images):
                row = idx // cols
                col = idx % cols

                x = col * (max_width + padding)
                y = row * (max_height + padding)

                # Resize image if needed
                if img.size != (max_width, max_height):
                    img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)

                montage.paste(img, (x, y))

            montage.save(output_path)
            return True

        except Exception as e:
            self.logger.error(f"Montage creation failed: {e}")
            return False

    # Utility Methods

    def convert_image_format(self, input_path: str, output_path: str,
                           output_format: str = "PNG") -> bool:
        """Convert image format"""
        try:
            if not PIL_AVAILABLE:
                return False

            img = self.load_image(input_path)
            if img:
                img.save(output_path, output_format)
                return True
            return False

        except Exception as e:
            self.logger.error(f"Format conversion failed: {e}")
            return False

    def get_supported_formats(self) -> List[str]:
        """Get supported image formats"""
        if PIL_AVAILABLE:
            return ['JPEG', 'PNG', 'BMP', 'TIFF', 'GIF', 'WEBP']
        return []

    def validate_image(self, image_path: str) -> Dict[str, Any]:
        """Validate image file"""
        try:
            validation = {
                "is_valid": False,
                "errors": [],
                "warnings": []
            }

            if not os.path.exists(image_path):
                validation["errors"].append("File does not exist")
                return validation

            if not PIL_AVAILABLE:
                validation["errors"].append("PIL not available")
                return validation

            try:
                with Image.open(image_path) as img:
                    img.verify()  # Check if image is corrupted
                    validation["is_valid"] = True

                    # Check image properties
                    if img.size[0] * img.size[1] < 100:
                        validation["warnings"].append("Image is very small")

                    if img.size[0] > 10000 or img.size[1] > 10000:
                        validation["warnings"].append("Image is very large")

            except Exception as e:
                validation["errors"].append(f"Image validation failed: {str(e)}")

            return validation

        except Exception as e:
            return {
                "is_valid": False,
                "errors": [str(e)],
                "warnings": []
            }
