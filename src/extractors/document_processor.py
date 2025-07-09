import base64
from pathlib import Path
from typing import Union, Optional, Tuple
from PIL import Image
import PyPDF2
import pdf2image
import io
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles various document formats and prepares them for AI processing"""
    
    SUPPORTED_FORMATS = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    
    def __init__(self):
        self.max_image_size = (2048, 2048)  # Max size for AI processing
    
    def process_document(self, file_path: Union[str, Path]) -> Tuple[str, str]:
        """
        Process a document and return base64 encoded image and format
        
        Returns:
            Tuple of (base64_image, format)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {file_path.suffix}")
        
        if file_path.suffix.lower() == '.pdf':
            return self._process_pdf(file_path)
        else:
            return self._process_image(file_path)
    
    def _process_pdf(self, pdf_path: Path) -> Tuple[str, str]:
        """Convert PDF to image and return base64"""
        try:
            # Convert first page of PDF to image
            images = pdf2image.convert_from_path(pdf_path, first_page=1, last_page=1)
            if not images:
                raise ValueError("Could not convert PDF to image")
            
            # Process the first page
            image = images[0]
            return self._image_to_base64(image)
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def _process_image(self, image_path: Path) -> Tuple[str, str]:
        """Process image file and return base64"""
        try:
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return self._image_to_base64(image)
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def _image_to_base64(self, image: Image.Image) -> Tuple[str, str]:
        """Convert PIL Image to base64 string"""
        # Resize if too large
        if image.size[0] > self.max_image_size[0] or image.size[1] > self.max_image_size[1]:
            image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return image_base64, 'image/png'
    
    def process_screenshot(self, screenshot_bytes: bytes) -> Tuple[str, str]:
        """Process screenshot bytes directly"""
        try:
            image = Image.open(io.BytesIO(screenshot_bytes))
            return self._image_to_base64(image)
        except Exception as e:
            logger.error(f"Error processing screenshot: {e}")
            raise