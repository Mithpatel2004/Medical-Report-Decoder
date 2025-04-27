from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pdf_extractor import extract_pdf_text
from ocr_extractor import extract_image_text
from summarizer import summarize_text
from simplifier import simplify_text, generate_precautions
from pydantic import BaseModel
import io
import uuid
import os
import logging
import re
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify API key at startup
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("🚨 OPENAI_API_KEY is not set in .env file! The application will run in offline mode.")
else:
    logger.info("✅ OPENAI_API_KEY found in environment variables.")
    # Check if it's a valid format (without actually testing the API)
    if not api_key.startswith(('sk-', 'sk-proj-')):
        logger.warning("⚠️ OPENAI_API_KEY does not appear to be in the correct format. Check your .env file.")
        
app = FastAPI()

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for processed reports
report_storage = {}

# Additional common medical conditions to detect in reports
# (will be used as fallback if simplifier.py doesn't detect any conditions)
MEDICAL_CONDITIONS = [
    "diabetes", "hypertension", "asthma", "arthritis", "heart disease", 
    "thyroid disorder", "pneumonia", "covid-19", "high blood pressure",
    "coronary artery disease", "copd", "chronic obstructive pulmonary disease",
    "cancer", "kidney disease", "liver disease", "stroke", "anemia",
    "gastroesophageal reflux disease", "gerd", "depression", "anxiety",
    "alzheimer's", "parkinson's", "multiple sclerosis", "osteoporosis"
]

# Common complex medical terms for extraction
COMPLEX_MEDICAL_TERMS = [
    "hypertension", "hyperlipidemia", "dyspnea", "myocardial infarction", 
    "cerebrovascular accident", "atherosclerosis", "arrhythmia", "tachycardia", 
    "bradycardia", "nephropathy", "neuropathy", "retinopathy", "gastroparesis",
    "arthralgia", "myalgia", "edema", "syncope", "vertigo", "pruritus",
    "dysphagia", "hemoptysis", "hematuria", "jaundice", "cirrhosis", "hepatomegaly",
    "splenomegaly", "thrombocytopenia", "anemia", "leukocytosis", "neutropenia",
    "hyperglycemia", "hypoglycemia", "hypercholesterolemia", "hyperkalemia", "hyponatremia",
    "hypernatremia", "azotemia", "uremia", "encephalopathy", "cerebral infarction",
    "transient ischemic attack", "paresthesia", "dysarthria", "dyslexia", "aphasia",
    "ataxia", "dyskinesia", "hyperreflexia", "hyporeflexia", "nystagmus"
]

def detect_medical_conditions(text):
    """
    Fallback detection of medical conditions mentioned in the text
    Returns the most likely condition found
    """
    text = text.lower()
    found_conditions = []
    
    for condition in MEDICAL_CONDITIONS:
        # Look for the condition as a whole word
        pattern = r'\b' + re.escape(condition) + r'\b'
        if re.search(pattern, text):
            found_conditions.append(condition)
    
    # Simple heuristic - return the condition that appears most frequently
    if found_conditions:
        condition_counts = {}
        for condition in found_conditions:
            pattern = r'\b' + re.escape(condition) + r'\b'
            condition_counts[condition] = len(re.findall(pattern, text))
        
        # Return the condition with the highest count
        return max(condition_counts, key=condition_counts.get)
    
    return None

# Complex terms extraction endpoint
class TextRequest(BaseModel):
    text: str
    report_id: str = None

@app.post("/extract-complex-terms/")
async def extract_complex_terms(request: TextRequest):
    """Extract complex medical terms from the provided text"""
    try:
        text = request.text.lower()
        extracted_terms = []
        
        # Method 1: Use regex to find complex terms from our predefined list
        for term in COMPLEX_MEDICAL_TERMS:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text):
                if term not in extracted_terms:
                    extracted_terms.append(term)
        
        # Method 2: Use regex patterns to find additional medical terminology
        # Pattern for medical terms with prefixes/suffixes common in medicine
        patterns = [
            r'\b\w+itis\b',  # inflammation
            r'\b\w+emia\b',   # blood condition
            r'\b\w+pathy\b',  # disease
            r'\b\w+ectomy\b', # surgical removal
            r'\b\w+plasty\b', # surgical repair
            r'\b\w+scopy\b',  # visual examination
            r'\b\w+tomy\b',   # surgical incision
            r'\b\w+gram\b',   # diagnostic image
            r'\b\w+megaly\b', # enlargement
            r'\b\w+trophy\b', # growth/development
            r'\b\w+osis\b',   # condition/disease
            r'\b\w+algia\b',  # pain
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match not in extracted_terms and len(match) > 5:  # Avoid short terms
                    extracted_terms.append(match)
        
        # Method 3: Use AI explainer to identify additional complex terms
        from ai_medical_explainer import identify_complex_terms
        ai_terms = identify_complex_terms(text)
        for term in ai_terms:
            if term not in extracted_terms:
                extracted_terms.append(term)
        
        # Limit to reasonable number of terms
        if len(extracted_terms) > 15:
            extracted_terms = extracted_terms[:15]
        
        return {
            "complex_terms": extracted_terms
        }
    except Exception as e:
        logger.error(f"Error extracting complex terms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting complex terms: {str(e)}")

# Disease detection and AI precautions endpoint
@app.post("/detect-diseases/")
async def detect_diseases(request: TextRequest):
    """Detect diseases in the text and provide AI-generated precautions"""
    try:
        text = request.text
        
        # Method 1: Use regex to find diseases from our predefined list
        detected_diseases = []
        for condition in MEDICAL_CONDITIONS:
            pattern = r'\b' + re.escape(condition) + r'\b'
            if re.search(pattern, text.lower()):
                if condition not in detected_diseases:
                    detected_diseases.append(condition)
        
        # Method 2: Use simplifier.py's function if available
        try:
            from simplifier import extract_conditions_from_text
            additional_conditions = extract_conditions_from_text(text)
            for condition in additional_conditions:
                if condition not in detected_diseases:
                    detected_diseases.append(condition)
        except Exception as e:
            logger.warning(f"Error using simplifier's extract_conditions: {e}")
        
        # Method 3: Use AI medical explainer to identify conditions
        try:
            from ai_medical_explainer import identify_medical_conditions
            ai_conditions = identify_medical_conditions(text)
            for condition in ai_conditions:
                if condition not in detected_diseases:
                    detected_diseases.append(condition)
        except Exception as e:
            logger.warning(f"Error using AI condition identification: {e}")
        
        # Generate AI-powered precautions
        precautions = []
        if detected_diseases:
            try:
                from ai_medical_explainer import generate_ai_precautions
                precautions = generate_ai_precautions(detected_diseases, text)
            except Exception as e:
                logger.warning(f"Error generating AI precautions: {e}")
                
                # Fallback to simplifier.py precautions if available
                try:
                    from simplifier import generate_precautions
                    prec_list, risks, condition = generate_precautions(text)
                    precautions = prec_list
                except Exception as inner_e:
                    logger.warning(f"Error using simplifier precautions: {inner_e}")
                    
                    # Ultimate fallback - generic precautions
                    precautions = [
                        "Follow your doctor's recommendations and treatment plan",
                        "Take all medications as prescribed by your healthcare provider",
                        "Attend all scheduled follow-up appointments",
                        "Maintain a balanced, nutritious diet appropriate for your condition",
                        "Stay physically active as appropriate for your condition",
                        "Get adequate rest and sleep to support recovery",
                        "Monitor your symptoms and report any changes to your doctor"
                    ]
        
        return {
            "detected_diseases": detected_diseases,
            "precautions": precautions
        }
    except Exception as e:
        logger.error(f"Error detecting diseases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error detecting diseases: {str(e)}")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Process uploaded medical reports (PDF or image)"""
    try:
        # Generate unique ID for this report
        report_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        
        # Process based on file type
        if file.filename.lower().endswith(".pdf"):
            logger.info(f"Processing PDF file: {file.filename}")
            text = extract_pdf_text(content)
        elif file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            logger.info(f"Processing image file: {file.filename}")
            text = extract_image_text(content)
        else:
            logger.warning(f"Unsupported file format: {file.filename}")
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or image files.")
        
        if not text or text.startswith("Error"):
            logger.error(f"Text extraction failed: {text}")
            raise HTTPException(status_code=500, detail="Failed to extract text from the file.")
        
        # Process the extracted text
        logger.info("Generating summary...")
        summary = summarize_text(text)
        
        logger.info("Simplifying text...")
        simplified_text, unknown_terms = simplify_text(text)
        
        logger.info("Generating precautions and detecting conditions...")
        precautions_list, risks, detected_condition = generate_precautions(text)
        
        # If no condition detected from primary method, try fallback
        if not detected_condition:
            detected_condition = detect_medical_conditions(text)
        
        # Convert precautions list to string for easier display
        precautions = "\n".join(precautions_list) if precautions_list else "Follow your doctor's recommendations."
        risks_text = ", ".join(risks.keys()) if risks else "No specific risk factors identified."
        
        # Store the processed text
        report_storage[report_id] = {
            "text": text,
            "summary": summary,
            "simplified": simplified_text,
            "unknown_terms": unknown_terms,
            "precautions": precautions,
            "risks": risks_text,
            "detected_condition": detected_condition
        }
        
        # Return processed data
        return {
            "report_id": report_id,
            "original_text": text[:1000] + "..." if len(text) > 1000 else text,  # Preview of original text
            "summary": summary,
            "simplified": simplified_text,
            "precautions": precautions,
            "risks": risks_text,
            "unknown_terms": unknown_terms,
            "detected_condition": detected_condition
        }
    except Exception as e:
        logger.error(f"Upload processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# Get more information about an unknown medical term
class TermRequest(BaseModel):
    term: str

@app.post("/explain-term/")
async def explain_term(request: TermRequest):
    """Get AI-generated explanation for an unknown medical term"""
    try:
        term = request.term
        logger.info(f"Requesting explanation for term: {term}")
        
        from ai_medical_explainer import get_term_explanation
        
        explanation = get_term_explanation(term)
        
        return {
            "term": term,
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Error explaining term: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error explaining term: {str(e)}")

# New ChatRequest class for the chatbot
class ChatRequest(BaseModel):
    question: str
    report_id: str = None
    chat_history: list = []

@app.post("/chat/")
async def chat_with_report(request: ChatRequest):
    """Chat with the AI about medical reports, conditions, and terms"""
    try:
        question = request.question
        report_id = request.report_id
        chat_history = request.chat_history
        
        # Get the report text if report_id is provided
        report_text = ""
        if report_id and report_id in report_storage:
            report_text = report_storage[report_id].get("original_text", "")
        
        # Use AI medical explainer to generate response
        try:
            from ai_medical_explainer import generate_chat_response
            response = generate_chat_response(question, report_text, chat_history)
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            # Fallback response if AI fails
            response = "I'm having trouble processing your question. Please try asking something about medical terms, conditions, or the content of your medical report."
        
        return {
            "response": response,
            "report_id": report_id
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Medical Report AI Assistant API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Report summary endpoint
@app.get("/report/{report_id}")
async def get_report(report_id: str):
    """Get a processed report by ID"""
    if report_id not in report_storage:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report_storage[report_id]

# Add middleware to handle CORS preflight requests
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    response = {
        "detail": "Preflight request handled successfully"
    }
    return response

# Add an endpoint to update the API key
class APIKeyRequest(BaseModel):
    api_key: str

@app.post("/update-api-key/")
async def update_api_key(request: APIKeyRequest):
    """Update the OpenAI API key"""
    try:
        api_key = request.api_key.strip()
        
        # Basic validation
        if not api_key:
            raise HTTPException(status_code=400, detail="API key cannot be empty")
        
        if not api_key.startswith(('sk-', 'sk-proj-')):
            raise HTTPException(status_code=400, detail="Invalid API key format. OpenAI keys start with 'sk-' or 'sk-proj-'")
        
        # Update the API key in memory
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Also update the key in the OpenAI client
        try:
            from ai_medical_explainer import client
            client.api_key = api_key
            # Also update the global api_key
            import openai
            openai.api_key = api_key
        except Exception as e:
            logger.error(f"Error updating API client key: {str(e)}")
        
        # Optionally, update the .env file (this will overwrite the file)
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        try:
            with open(env_path, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}")
            logger.info("Updated API key in .env file")
        except Exception as e:
            logger.error(f"Failed to update .env file: {str(e)}")
            # Not fatal, continue
        
        # Test the API key with a simple request
        try:
            from ai_medical_explainer import client
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Test connection"}
                ],
                max_tokens=5
            )
            logger.info("API key test successful")
            return {"status": "success", "message": "API key updated successfully and verified working"}
        except Exception as e:
            logger.error(f"API key test failed: {str(e)}")
            error_msg = str(e)
            if "quota" in error_msg.lower() or "exceeded" in error_msg.lower() or "429" in error_msg:
                raise HTTPException(status_code=400, detail="API key accepted, but your quota has been exceeded. Please check your OpenAI account.")
            else:
                raise HTTPException(status_code=400, detail=f"API key update failed: {error_msg}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating API key: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating API key: {str(e)}")