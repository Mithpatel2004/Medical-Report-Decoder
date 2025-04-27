import pytesseract
from PIL import Image
from io import BytesIO
import logging

# Configure logging
logger = logging.getLogger(__name__)

def extract_image_text(file_bytes):
    """Extract text from images using OCR"""
    try:
        image = Image.open(BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip() if text else "No text detected in the image."
    except Exception as e:
        logger.error(f"Error in OCR extraction: {e}")
        return f"OCR extraction error: {str(e)}"