from transformers import pipeline
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the summarization pipeline
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    logger.info("Summarization model loaded successfully")
except Exception as e:
    logger.error(f"Error loading summarization model: {e}")
    summarizer = None

def summarize_text(text):
    """Summarize the provided text"""
    if not text or len(text.strip()) < 50:
        return "Text too short for summarization."
    
    if not summarizer:
        return "Summarization model not loaded. Please check server logs."
    
    try:
        # Clean the text
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        # Chunk the text if it's too long
        max_chunk_size = 1024  # Maximum tokens the model can handle
        if len(cleaned_text) > max_chunk_size * 4:  # Rough character to token ratio
            chunks = [cleaned_text[i:i+max_chunk_size*4] for i in range(0, len(cleaned_text), max_chunk_size*4)]
            summaries = []
            
            for chunk in chunks:
                try:
                    summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
                    summaries.append(summary)
                except Exception as e:
                    logger.error(f"Error summarizing chunk: {e}")
                    summaries.append("Error summarizing part of the text.")
            
            result = " ".join(summaries)
            return result
        else:
            summary = summarizer(cleaned_text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
            return summary
    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        return f"Summarization error: {str(e)}"