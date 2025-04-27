import pdfplumber
from io import BytesIO
import logging

# Configure logging
logger = logging.getLogger(__name__)

def extract_pdf_text(file_bytes):
    """Extract text content from a PDF file"""
    text = ""
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n\n"
        result = text.strip()
        return result if result else "No text content found in the PDF."
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return f"Error extracting text: {str(e)}"