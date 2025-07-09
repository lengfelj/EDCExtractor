import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class OCRHandler:
    """Handles OCR processing for scanned documents"""
    
    def __init__(self):
        # Check if tesseract is installed
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            logger.warning("Tesseract not found. OCR functionality will be limited.")
    
    def extract_text(self, image: Image.Image, preprocess: bool = True) -> str:
        """Extract text from image using OCR"""
        try:
            if preprocess:
                image = self._preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        # Convert PIL to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.medianBlur(thresh, 3)
        
        # Convert back to PIL
        return Image.fromarray(denoised)