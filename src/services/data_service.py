import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
import io
from utils.logger import get_logger

class ImageService:
    def __init__(self):
        self.logger = get_logger('ImageService')
        self.target_size = (640, 640)
        self.max_size = 1024
        self.quality = 85

    def preprocess_image_from_file(self, file_object):
        """
        Preprocess image from file-like object (used in Flask uploads)
        Args:
            file_object: file-like object (e.g., io.BytesIO)
        Returns:
            PIL.Image: Preprocessed image
        """
        try:
            image = Image.open(file_object)
            image = self._preprocess_pil_image(image)
            return image
        except Exception as e:
            self.logger.error(f"[preprocess_image_from_file] {e}")
            raise

    def preprocess_image(self, image_path):
        """
        Preprocess image from disk path
        Args:
            image_path (str): Path to image
        Returns:
            PIL.Image: Preprocessed image
        """
        try:
            image = Image.open(image_path)
            image = self._preprocess_pil_image(image)
            return image
        except Exception as e:
            self.logger.error(f"[preprocess_image] {e}")
            raise

    def _preprocess_pil_image(self, image):
        """
        Apply core preprocessing steps
        Args:
            image (PIL.Image): Original image
        Returns:
            PIL.Image: Processed image
        """
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')

            image = ImageOps.exif_transpose(image)

            if max(image.size) > self.max_size:
                image.thumbnail((self.max_size, self.max_size), Image.Resampling.LANCZOS)

            image = self._enhance_image(image)
            return image
        except Exception as e:
            self.logger.error(f"[preprocess_pil_image] {e}")
            raise

    def _enhance_image(self, image):
        """
        Enhance contrast, sharpness, and color
        """
        try:
            image = ImageEnhance.Contrast(image).enhance(1.1)
            image = ImageEnhance.Sharpness(image).enhance(1.1)
            image = ImageEnhance.Color(image).enhance(1.05)
            return image
        except Exception as e:
            self.logger.error(f"[enhance_image] {e}")
            return image

    def resize_image(self, image, target_size=None):
        """
        Resize image to target size with black padding
        """
        try:
            if target_size is None:
                target_size = self.target_size

            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            new_image = Image.new('RGB', target_size, (0, 0, 0))
            x = (target_size[0] - image.size[0]) // 2
            y = (target_size[1] - image.size[1]) // 2
            new_image.paste(image, (x, y))
            return new_image
        except Exception as e:
            self.logger.error(f"[resize_image] {e}")
            raise

    def normalize_image(self, image):
        """
        Normalize image to [0, 1] range
        """
        try:
            img_array = np.array(image, dtype=np.float32) / 255.0
            return img_array
        except Exception as e:
            self.logger.error(f"[normalize_image] {e}")
            raise

    def apply_filters(self, image, filters=None):
        """
        Apply optional OpenCV filters
        """
        try:
            if filters is None:
                filters = {'denoise': True, 'sharpen': True, 'contrast': True}

            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            if filters.get('denoise'):
                cv_image = cv2.fastNlMeansDenoisingColored(cv_image, None, 10, 10, 7, 21)

            if filters.get('sharpen'):
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
                cv_image = cv2.filter2D(cv_image, -1, kernel)

            if filters.get('contrast'):
                cv_image = cv2.convertScaleAbs(cv_image, alpha=1.1, beta=10)

            return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
        except Exception as e:
            self.logger.error(f"[apply_filters] {e}")
            return image

    def validate_image(self, image_path):
        """
        Validate image file size and format
        """
        try:
            result = {'is_valid': False, 'format': None, 'size': None, 'error': None}
            with Image.open(image_path) as img:
                result.update({
                    'is_valid': True,
                    'format': img.format,
                    'size': img.size
                })

                if min(img.size) < 32:
                    result['is_valid'] = False
                    result['error'] = 'Image too small'
                elif max(img.size) > 4096:
                    result['is_valid'] = False
                    result['error'] = 'Image too large'

            return result
        except Exception as e:
            return {'is_valid': False, 'format': None, 'size': None, 'error': str(e)}

    def get_image_info(self, image):
        """
        Return metadata about image
        """
        try:
            return {
                'size': image.size,
                'mode': image.mode,
                'format': getattr(image, 'format', 'Unknown'),
                'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
            }
        except Exception as e:
            self.logger.error(f"[get_image_info] {e}")
            return {}
