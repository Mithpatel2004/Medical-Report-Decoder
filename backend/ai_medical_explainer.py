import os
import logging
import re
import json
from typing import Dict, List, Any
import openai
from dotenv import load_dotenv
from openai import OpenAI
from nltk.stem.porter import PorterStemmer

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI API client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cache for term explanations to avoid repeated API calls
term_explanations_cache: Dict[str, str] = {}

# Fallback medical terms dictionary for when OpenAI API is unavailable
MEDICAL_TERMS_FALLBACK = {
    "polycythemia": "A condition where there are too many red blood cells in the blood, making it thicker than normal. This can slow blood flow and cause complications like blood clots.",
    "diagnosis": "The identification of a medical condition or disease through examination of symptoms, medical tests, and patient history.",
    "spondylosis": "Age-related degeneration of the spine, affecting the discs and joints. It can cause stiffness, pain, and reduced flexibility in the neck or back.",
    "hypertension": "High blood pressure that can lead to serious health problems like heart disease and stroke if not properly controlled.",
    "arthritis": "Inflammation of one or more joints, causing pain, stiffness, and reduced movement. Common types include osteoarthritis and rheumatoid arthritis.",
    "diabetes": "A chronic condition that affects how your body processes blood sugar (glucose), potentially leading to too much sugar in your bloodstream.",
    "cholesterol": "A waxy substance found in your blood. High levels can build up in your arteries and increase risk of heart disease.",
    "anemia": "A condition where you don't have enough healthy red blood cells to carry adequate oxygen to your body's tissues.",
    "asthma": "A condition affecting the airways of the lungs, causing them to narrow, swell, and produce extra mucus, making breathing difficult.",
    "hypothyroidism": "A condition where the thyroid gland doesn't produce enough thyroid hormone, slowing down metabolism and affecting many body functions.",
    "gastritis": "Inflammation of the stomach lining that can cause pain, nausea, and a feeling of fullness.",
    "osteoporosis": "A condition that weakens bones, making them fragile and more likely to break.",
    "bronchitis": "Inflammation of the bronchial tubes that carry air to and from your lungs, causing coughing and mucus production.",
    "pneumonia": "An infection that inflames the air sacs in one or both lungs, which may fill with fluid.",
    "hemorrhoids": "Swollen veins in your lower rectum and anus that can cause discomfort, pain, and bleeding.",
    "hyperlipidemia": "Abnormally high levels of fats (lipids) in the blood, which can increase risk of heart disease.",
    "biopsy": "A medical procedure where a small sample of tissue is taken from the body to examine under a microscope for diagnosis.",
    "cardiomyopathy": "Disease of the heart muscle that makes it harder for your heart to pump blood to the rest of your body.",
    "dyspnea": "Difficult or labored breathing, often described as 'shortness of breath'.",
    "fibrosis": "Formation of excess fibrous connective tissue in an organ or tissue, often as a repair response to injury.",
    "hysterectomy": "Surgical removal of the uterus, sometimes including the cervix, ovaries, and fallopian tubes.",
    "ischemia": "Insufficient blood supply to an organ or body part, usually due to blocked arteries.",
    "metastasis": "The spread of cancer cells from the place where they first formed to another part of the body.",
    "nephropathy": "Disease or damage to the kidney, often caused by diabetes or high blood pressure.",
    "neuropathy": "Damage to the nerves that can cause weakness, numbness, and pain, usually in the hands and feet.",
    "tachycardia": "Abnormally rapid heart rate, typically over 100 beats per minute while at rest.",
    "thrombosis": "Formation of a blood clot inside a blood vessel, obstructing the flow of blood.",
    "stenosis": "Abnormal narrowing of a passage in the body, such as a blood vessel or heart valve.",
    "edema": "Swelling caused by excess fluid trapped in your body's tissues.",
    "hematoma": "Collection of blood outside of blood vessels, appearing as a bruise or lump.",
    "embolism": "Blockage of an artery by a foreign substance (like a blood clot) that has traveled through the bloodstream.",
    "encephalopathy": "Disease, damage, or malfunction of the brain, often with altered mental state.",
    "hepatomegaly": "Enlarged liver that may be caused by various conditions including fatty liver disease.",
    "myeloma": "Cancer that forms in plasma cells, which help your body fight infections.",
    "myocardial infarction": "Heart attack; when blood flow to part of the heart is blocked, causing damage to heart muscle.",
    "diverticulitis": "Inflammation or infection in small pouches (diverticula) that can form in your digestive tract.",
    "arrhythmia": "Irregular heartbeat that can be too fast, too slow, or irregular in rhythm.",
    "cirrhosis": "Scarring of the liver tissue that prevents the liver from functioning properly.",
    "copd": "Chronic Obstructive Pulmonary Disease; a group of lung diseases that block airflow and make breathing difficult."
}

# Fallback precautions for common conditions when AI is unavailable
CONDITION_PRECAUTIONS_FALLBACK = {
    "diabetes": [
        "Monitor your blood glucose levels regularly as recommended by your doctor",
        "Take all prescribed medications consistently and at the right times",
        "Follow a balanced diet with controlled carbohydrate intake",
        "Engage in regular physical activity as approved by your healthcare provider",
        "Check your feet daily for cuts, blisters, or signs of infection",
        "Attend regular eye examinations to monitor for diabetic retinopathy",
        "Stay well-hydrated and avoid sugary beverages",
        "Carry identification indicating you have diabetes",
        "Know the symptoms of high and low blood sugar and how to respond",
        "Keep regular appointments with your healthcare team"
    ],
    "hypertension": [
        "Monitor your blood pressure regularly at home if recommended by your doctor",
        "Take blood pressure medications exactly as prescribed",
        "Reduce sodium (salt) intake in your diet",
        "Maintain a healthy weight or lose weight if recommended",
        "Exercise regularly with activities like walking, swimming, or cycling",
        "Limit alcohol consumption",
        "Quit smoking and avoid secondhand smoke",
        "Find healthy ways to manage stress",
        "Eat a diet rich in fruits, vegetables, and low-fat dairy products",
        "Limit caffeine intake"
    ],
    "asthma": [
        "Take controller medications daily as prescribed, even when feeling well",
        "Keep rescue inhalers readily available at all times",
        "Learn to recognize and avoid your asthma triggers",
        "Use a peak flow meter to monitor your lung function if recommended",
        "Follow your written asthma action plan",
        "Get vaccinated against flu and pneumonia",
        "Cover your mouth and nose in cold weather",
        "Exercise regularly as tolerated, but be aware of exercise-induced symptoms",
        "Keep regular follow-up appointments with your healthcare provider",
        "Clean your home regularly to reduce dust, pet dander, and other allergens"
    ],
    "heart disease": [
        "Take all medications as prescribed by your doctor",
        "Follow a heart-healthy diet low in saturated fat, trans fat, and sodium",
        "Exercise regularly according to your doctor's recommendations",
        "Maintain a healthy weight",
        "Monitor your blood pressure and cholesterol levels",
        "Quit smoking and avoid secondhand smoke",
        "Limit alcohol consumption",
        "Manage stress through relaxation techniques or counseling",
        "Know the warning signs of a heart attack and what to do",
        "Keep all follow-up appointments with your healthcare providers"
    ],
    "arthritis": [
        "Take medications as prescribed to manage pain and inflammation",
        "Apply hot or cold packs to painful joints as recommended",
        "Perform gentle stretching and range-of-motion exercises daily",
        "Use assistive devices to protect joints during daily activities",
        "Maintain a healthy weight to reduce pressure on weight-bearing joints",
        "Alternate between activity and rest; avoid overexertion",
        "Practice good posture to reduce stress on joints",
        "Consider physical therapy if recommended by your doctor",
        "Use ergonomic tools and furniture to reduce joint strain",
        "Participate in low-impact exercises like swimming or cycling"
    ],
    "copd": [
        "Take all respiratory medications as prescribed",
        "Use oxygen therapy exactly as directed if prescribed",
        "Avoid smoking and secondhand smoke",
        "Avoid air pollution, dust, and chemical fumes",
        "Get vaccinated against flu, pneumonia, and COVID-19",
        "Participate in pulmonary rehabilitation if recommended",
        "Practice breathing techniques to improve lung efficiency",
        "Conserve energy by pacing activities and using body mechanics",
        "Stay hydrated to keep mucus thin and easier to clear",
        "Learn pursed-lip breathing to help with shortness of breath"
    ],
    "kidney disease": [
        "Take all prescribed medications consistently",
        "Monitor and control your blood pressure and blood sugar",
        "Limit protein intake as advised by your healthcare provider",
        "Restrict sodium, potassium, and phosphorus in your diet as recommended",
        "Drink the amount of fluid recommended by your doctor",
        "Avoid nonsteroidal anti-inflammatory drugs (NSAIDs) unless approved",
        "Attend all scheduled dialysis appointments if applicable",
        "Get regular lab tests to monitor kidney function",
        "Exercise regularly, but gently, as approved by your doctor",
        "Protect your access site if you have dialysis"
    ],
    "liver disease": [
        "Avoid alcohol completely",
        "Take medications only as prescribed by your doctor",
        "Get vaccinated against hepatitis A and B if appropriate",
        "Eat a balanced, nutritious diet as recommended",
        "Avoid raw or undercooked shellfish",
        "Maintain a healthy weight",
        "Avoid exposure to chemicals and toxins",
        "Get regular monitoring of your liver function",
        "Manage other conditions like diabetes and high cholesterol",
        "Contact your doctor if you notice increased jaundice, abdominal swelling, or confusion"
    ],
    "stroke": [
        "Take all prescribed medications, especially blood thinners, as directed",
        "Monitor and control your blood pressure",
        "Follow a low-sodium, healthy diet",
        "Exercise regularly as recommended by your healthcare provider",
        "Quit smoking and avoid secondhand smoke",
        "Limit alcohol consumption",
        "Keep blood sugar under control if you have diabetes",
        "Attend all rehabilitation therapy sessions",
        "Use assistive devices as recommended for safety and mobility",
        "Know the signs of another stroke and act quickly if they occur"
    ],
    "generic": [
        "Take all medications as prescribed by your healthcare provider",
        "Keep all follow-up appointments with your medical team",
        "Maintain a balanced, nutritious diet appropriate for your condition",
        "Stay physically active as appropriate for your health status",
        "Get adequate rest and manage stress in healthy ways",
        "Avoid tobacco products and limit alcohol consumption",
        "Monitor your symptoms and report any changes to your doctor",
        "Follow any specific lifestyle modifications recommended for your condition",
        "Stay up to date with recommended vaccinations",
        "Keep a record of your symptoms, medications, and questions for doctor visits"
    ]
}

def get_term_explanation(term: str) -> str:
    """
    Get a simplified explanation for a medical term using OpenAI
    Falls back to a dictionary if API is unavailable
    """
    term = term.strip().lower()
    
    if not term or len(term) < 2:
        return "Invalid term provided."
    
    # Check if we have a fallback explanation for this term
    if term in MEDICAL_TERMS_FALLBACK:
        return MEDICAL_TERMS_FALLBACK[term]
    
    try:
        # Define the prompt for the OpenAI API
        prompt = f"""Explain the following medical term in simple language that a patient without medical background would understand: "{term}".
        Keep the explanation concise (30-50 words), easy to understand, and avoid using other complex medical terms.
        If it's not a medical term, please indicate that."""
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a less expensive model for simple explanations
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant that explains complex medical terminology in simple terms."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3,  # Lower temperature for more consistent responses
        )
        
        explanation = response.choices[0].message.content.strip()
        # Cache the explanation for future use
        term_explanations_cache[term] = explanation
        return explanation
        
    except Exception as e:
        logger.error(f"Error explaining term with OpenAI: {str(e)}")
        
        # Try to find a partial match in our fallback dictionary
        for key, value in MEDICAL_TERMS_FALLBACK.items():
            if term in key or key in term:
                return f"Similar to {key}: {value}"
        
        # Generate a basic explanation based on common medical prefixes/suffixes
        explanation = generate_basic_explanation(term)
        if explanation:
            return explanation
        
        return f"Term not found in medical dictionary. Please consult with your healthcare provider about this term."

def generate_basic_explanation(term: str) -> str:
    """
    Generate a basic explanation for a medical term without using the API.
    Uses pattern matching and word decomposition to create reasonable fallbacks.
    
    Args:
        term: The medical term to explain
        
    Returns:
        A basic explanation string or None if no explanation could be generated
    """
    term = term.lower()
    
    # Check if it's in our fallback dictionary first
    if term in MEDICAL_TERMS_FALLBACK:
        return MEDICAL_TERMS_FALLBACK[term]
    
    # Common prefixes and their meanings
    prefixes = {
        'cardio': 'heart',
        'neuro': 'nervous system or brain',
        'gastro': 'stomach or digestive system',
        'hepat': 'liver',
        'nephro': 'kidney',
        'dermato': 'skin',
        'osteo': 'bone',
        'arthro': 'joint',
        'pulmon': 'lung',
        'pneumo': 'lung or air',
        'hemo': 'blood',
        'onco': 'cancer or tumor',
        'psych': 'mental health',
        'endo': 'hormone or internal',
        'rheumat': 'joints and connective tissue',
        'ophthalm': 'eye',
        'oto': 'ear',
        'gyn': 'female reproductive system',
        'uro': 'urinary system',
        'derm': 'skin',
        'hyper': 'high or excessive',
        'hypo': 'low or deficient',
        'brady': 'slow',
        'tachy': 'fast',
        'myelo': 'bone marrow or spinal cord',
        'angio': 'blood vessels',
        'cyto': 'cell',
        'adeno': 'gland',
    }
    
    # Common suffixes and their meanings
    suffixes = {
        'itis': 'inflammation',
        'osis': 'condition or disease',
        'oma': 'tumor or growth',
        'algia': 'pain',
        'pathy': 'disease',
        'ectomy': 'surgical removal',
        'otomy': 'surgical cutting',
        'plasty': 'surgical reshaping',
        'scopy': 'examination procedure',
        'gram': 'recording or image',
        'graphy': 'imaging technique',
        'emia': 'blood condition',
        'penia': 'deficiency',
        'megaly': 'enlargement',
        'iasis': 'condition or state',
        'lysis': 'breakdown or destruction',
        'stenosis': 'narrowing',
        'rrhea': 'flow or discharge',
        'rrhage': 'excessive bleeding',
        'phobia': 'fear',
        'sclerosis': 'hardening',
        'trophy': 'growth or development',
        'genic': 'produced by or producing',
    }
    
    # Common medical measurement terms
    measurement_terms = {
        'bpm': 'beats per minute, a measure of heart rate',
        'mmHg': 'millimeters of mercury, a unit for measuring blood pressure',
        'BMI': 'Body Mass Index, a measure of body fat based on height and weight',
        'WBC': 'White Blood Cell count, part of a complete blood count test',
        'RBC': 'Red Blood Cell count, part of a complete blood count test',
        'HbA1c': 'Hemoglobin A1c, a test that measures average blood sugar levels',
        'INR': 'International Normalized Ratio, a measurement of blood clotting time',
        'EKG': 'Electrocardiogram, a test that measures heart electrical activity',
        'ECG': 'Electrocardiogram, a test that measures heart electrical activity',
        'MRI': 'Magnetic Resonance Imaging, a medical imaging technique',
        'CT scan': 'Computerized Tomography scan, a medical imaging technique',
        'EEG': 'Electroencephalogram, a test that measures brain activity',
        'BP': 'Blood Pressure, the pressure of circulating blood against vessel walls',
        'HR': 'Heart Rate, the number of heartbeats per minute',
        'SpO2': 'Oxygen Saturation, the percentage of oxygen in the blood',
        'FEV1': 'Forced Expiratory Volume in 1 second, a lung function measurement',
        'GFR': 'Glomerular Filtration Rate, a test of kidney function',
        'PSA': 'Prostate-Specific Antigen, a blood test for prostate health',
    }
    
    # Common medical conditions and their simplified explanations
    common_conditions = {
        'hypertension': 'High blood pressure, when blood pushes too hard against blood vessel walls.',
        'diabetes': 'A condition where the body cannot properly regulate blood sugar levels.',
        'arrhythmia': 'Irregular heartbeat or heart rhythm disorder.',
        'tachycardia': 'Abnormally fast heart rate.',
        'bradycardia': 'Abnormally slow heart rate.',
        'hyperlipidemia': 'High levels of fats (like cholesterol) in the blood.',
        'asthma': 'A condition that causes breathing difficulties due to narrowed airways.',
        'COPD': 'Chronic Obstructive Pulmonary Disease, a progressive lung disease causing breathing difficulties.',
        'pneumonia': 'An infection causing inflammation in the air sacs of one or both lungs.',
        'bronchitis': 'Inflammation of the bronchial tubes that carry air to the lungs.',
        'arthritis': 'Inflammation of joints causing pain and stiffness.',
        'osteoporosis': 'A condition where bones become weak and brittle.',
        'gastritis': 'Inflammation of the stomach lining.',
        'GERD': 'Gastroesophageal Reflux Disease, when stomach acid frequently flows back into the esophagus.',
        'hepatitis': 'Inflammation of the liver, often caused by a virus.',
        'cirrhosis': 'Severe scarring of the liver tissue.',
        'nephritis': 'Inflammation of the kidneys.',
        'anemia': 'A condition where there aren\'t enough healthy red blood cells to carry oxygen throughout the body.',
        'leukemia': 'Cancer of the blood-forming tissues, including bone marrow.',
        'hypothyroidism': 'Underactive thyroid gland not producing enough thyroid hormones.',
        'hyperthyroidism': 'Overactive thyroid gland producing too much thyroid hormone.',
    }
    
    # Check if this is a common medical term with a known explanation
    if term in common_conditions:
        return common_conditions[term]
    if term in measurement_terms:
        return measurement_terms[term]
    
    # Try to break down the term using prefixes and suffixes
    for prefix, prefix_meaning in prefixes.items():
        if term.startswith(prefix):
            remainder = term[len(prefix):]
            for suffix, suffix_meaning in suffixes.items():
                if remainder.endswith(suffix):
                    return f"A {suffix_meaning} related to the {prefix_meaning}."
            return f"A medical term related to the {prefix_meaning}."
    
    # Check suffixes alone
    for suffix, suffix_meaning in suffixes.items():
        if term.endswith(suffix):
            return f"A {suffix_meaning} or medical condition."
    
    # Handle common test names
    if 'test' in term or 'scan' in term or 'gram' in term or 'graphy' in term:
        return f"A medical test or diagnostic procedure."
    
    # Handle medication-sounding terms
    if term.endswith('in') or term.endswith('ol') or term.endswith('ide') or term.endswith('one') or term.endswith('ine'):
        return f"Likely a medication or drug name."
    
    # When we have no idea, generate a generic response
    words = term.split()
    if len(words) > 1:
        # For multi-word terms, use the last word as a hint
        return f"A medical term that may be related to the {words[-1]}."
    
    # Last resort
    return f"A medical term or condition used in healthcare."

def identify_complex_terms(text: str) -> List[str]:
    """
    Use AI to identify complex medical terms in the text
    Falls back to pattern matching when API is unavailable
    """
    results = []
    
    # Always try pattern matching first for reliability
    try:
        # Extract terms based on common medical patterns
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
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if match not in results and len(match) > 5:  # Avoid short terms
                    results.append(match)
        
        # Check for known medical terms
        for term in MEDICAL_TERMS_FALLBACK.keys():
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text.lower()):
                if term not in results:
                    results.append(term)
    except Exception as e:
        logger.warning(f"Error in pattern matching: {e}")
    
    # Try AI if we have fewer than 5 terms from pattern matching
    if len(results) < 5:
        try:
            if not text or len(text) < 20:
                return results
            
            # For very long texts, we need to truncate
            if len(text) > 8000:
                text = text[:8000] + "..."
            
            # Define the prompt for the OpenAI API
            prompt = f"""Analyze the following medical text and extract a list of complex medical terms that a typical patient would find difficult to understand:

Text: {text}

Extract only complex medical terminology. Return the list as a JSON array of strings containing just the medical terms.
Limit to the 15 most significant terms. Format should be ["term1", "term2", etc.].
Do not include common words that laypeople would understand."""
            
            # Make the API call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical terminology expert system that extracts complex medical terms from text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.2,  # Low temperature for consistent formatting
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract the JSON array from the response
            try:
                # Try to find a JSON array in the response
                match = re.search(r'\[\s*"[^"]*"(?:\s*,\s*"[^"]*")*\s*\]', result)
                if match:
                    json_array = match.group(0)
                    terms = json.loads(json_array)
                    for term in terms:
                        if term not in results:
                            results.append(term)
                else:
                    # If no proper JSON array is found, try to parse the whole response
                    terms = json.loads(result)
                    if isinstance(terms, list):
                        for term in terms:
                            if term not in results:
                                results.append(term)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract terms with regex
                terms = re.findall(r'"([^"]+)"', result)
                for term in terms:
                    if term not in results and term not in ["term1", "term2", "etc"]:
                        results.append(term)
                
        except Exception as e:
            logger.error(f"Error identifying complex terms with AI: {str(e)}")
            # AI failed, but we still have pattern matching results
            pass
    
    # Limit to reasonable number of terms
    if len(results) > 15:
        results = results[:15]
    
    return results

def identify_medical_conditions(text: str) -> List[str]:
    """
    Use AI to identify medical conditions mentioned in the text
    Falls back to pattern matching when API is unavailable
    """
    conditions = []
    
    # Always do pattern matching first
    try:
        # Common medical conditions to detect in reports
        common_conditions = [
            "diabetes", "hypertension", "asthma", "arthritis", "heart disease", 
            "thyroid disorder", "pneumonia", "covid-19", "high blood pressure",
            "coronary artery disease", "copd", "chronic obstructive pulmonary disease",
            "cancer", "kidney disease", "liver disease", "stroke", "anemia",
            "gastroesophageal reflux disease", "gerd", "depression", "anxiety",
            "alzheimer's", "parkinson's", "multiple sclerosis", "osteoporosis",
            "hypertension", "hyperlipidemia", "obesity", "osteoarthritis", 
            "rheumatoid arthritis", "hypothyroidism", "hyperthyroidism", 
            "chronic kidney disease", "cirrhosis", "hepatitis", "heart failure", 
            "atrial fibrillation", "coronary artery disease", "peripheral artery disease", 
            "chronic venous insufficiency", "deep vein thrombosis", "pulmonary embolism",
            "sleep apnea", "chronic bronchitis", "emphysema", "asthma", "pneumonia",
            "tuberculosis", "migraine", "epilepsy", "parkinson's disease", "dementia",
            "glaucoma", "cataracts", "macular degeneration", "hearing loss", "meniere's disease", 
            "gastritis", "peptic ulcer disease", "crohn's disease", "ulcerative colitis", 
            "irritable bowel syndrome", "diverticulosis", "diverticulitis", "hemorrhoids",
            "gallstones", "urinary incontinence", "benign prostatic hyperplasia", 
            "erectile dysfunction", "osteopenia", "gout", "lupus", "fibromyalgia", 
            "psoriasis", "eczema", "rosacea", "melanoma", "basal cell carcinoma", 
            "breast cancer", "prostate cancer", "colorectal cancer", "lung cancer", 
            "leukemia", "lymphoma", "multiple myeloma", "depression", "anxiety disorder", 
            "bipolar disorder", "post-traumatic stress disorder"
        ]
        
        for condition in common_conditions:
            pattern = r'\b' + re.escape(condition) + r'\b'
            if re.search(pattern, text.lower()):
                if condition not in conditions:
                    conditions.append(condition)
    except Exception as e:
        logger.warning(f"Error in condition pattern matching: {e}")
    
    # Try AI if we have fewer than 3 conditions from pattern matching
    if len(conditions) < 3:
        try:
            if not text or len(text) < 20:
                return conditions
            
            # For very long texts, we need to truncate
            if len(text) > 8000:
                text = text[:8000] + "..."
            
            # Define the prompt for the OpenAI API
            prompt = f"""Read the following medical text and identify any medical conditions, diseases, or diagnoses mentioned:

Text: {text}

Return the list as a JSON array of strings containing just the names of the conditions.
Format should be ["condition1", "condition2", etc.]. 
Focus on actual medical conditions that would require treatment or management.
Do not include symptoms unless they are specifically diagnosed conditions."""
            
            # Make the API call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical diagnosis expert that identifies medical conditions from clinical text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.2,  # Low temperature for consistent formatting
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract the JSON array from the response
            try:
                # Try to find a JSON array in the response
                match = re.search(r'\[\s*"[^"]*"(?:\s*,\s*"[^"]*")*\s*\]', result)
                if match:
                    json_array = match.group(0)
                    ai_conditions = json.loads(json_array)
                    for condition in ai_conditions:
                        if condition not in conditions:
                            conditions.append(condition)
                else:
                    # If no proper JSON array is found, try to parse the whole response
                    ai_conditions = json.loads(result)
                    if isinstance(ai_conditions, list):
                        for condition in ai_conditions:
                            if condition not in conditions:
                                conditions.append(condition)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract terms with regex
                ai_conditions = re.findall(r'"([^"]+)"', result)
                for condition in ai_conditions:
                    if condition not in conditions and condition not in ["condition1", "condition2", "etc"]:
                        conditions.append(condition)
                
        except Exception as e:
            logger.error(f"Error identifying medical conditions with AI: {str(e)}")
            # AI failed, but we still have pattern matching results
    
    return conditions

def generate_ai_precautions(conditions: List[str], context_text: str = "") -> List[str]:
    """
    Generate AI-powered precautions and recommendations for the identified conditions
    Falls back to built-in recommendations when API is unavailable
    """
    # First check if we have fallback precautions for the conditions
    matched_precautions = []
    
    # Try to match each condition with our fallback database
    for condition in conditions:
        condition_lower = condition.lower()
        # Check for exact match
        if condition_lower in CONDITION_PRECAUTIONS_FALLBACK:
            matched_precautions.extend(CONDITION_PRECAUTIONS_FALLBACK[condition_lower])
        else:
            # Check for partial matches
            for key in CONDITION_PRECAUTIONS_FALLBACK:
                if key in condition_lower or condition_lower in key:
                    matched_precautions.extend(CONDITION_PRECAUTIONS_FALLBACK[key])
                    break
    
    # If we found precautions in our fallback database, use those
    if matched_precautions:
        # Remove duplicates while preserving order
        unique_precautions = []
        for item in matched_precautions:
            if item not in unique_precautions:
                unique_precautions.append(item)
        
        # Limit to 10 precautions
        if len(unique_precautions) > 10:
            unique_precautions = unique_precautions[:10]
        
        # If we have enough precautions, return them without calling the API
        if len(unique_precautions) >= 5:
            return unique_precautions
    
    # If we don't have enough fallback precautions, try the AI
    try:
        if not conditions:
            return CONDITION_PRECAUTIONS_FALLBACK["generic"]
        
        # Join the conditions into a comma-separated list
        conditions_text = ", ".join(conditions)
        
        # Truncate context text if needed
        context_snippet = ""
        if context_text and len(context_text) > 100:
            context_snippet = context_text[:2000] + "..."
        
        # Define the prompt for the OpenAI API
        prompt = f"""Based on the following medical condition(s): {conditions_text}
        
        {f"Context from medical report: {context_snippet}" if context_snippet else ""}
        
        Generate a list of 7-10 specific health precautions and recommendations that would be important for a patient with these conditions.
        
        Each recommendation should be:
        1. Clear and actionable
        2. Written in simple language a patient can understand
        3. Medically accurate and evidence-based
        4. Specific to the condition(s) mentioned
        
        Format the response as a JSON array of strings, each containing one recommendation.
        Example format: ["Recommendation 1", "Recommendation 2", ...]"""
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o",  # Using a more capable model for medical recommendations
            messages=[
                {"role": "system", "content": "You are a medical expert providing evidence-based health recommendations for patients."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.4,
        )
        
        result = response.choices[0].message.content.strip()
        
        # Extract the JSON array from the response
        try:
            # Try to find a JSON array in the response
            match = re.search(r'\[\s*"[^"]*"(?:\s*,\s*"[^"]*")*\s*\]', result)
            if match:
                json_array = match.group(0)
                ai_precautions = json.loads(json_array)
                if matched_precautions:
                    # Combine AI precautions with our fallback precautions
                    combined = matched_precautions + [p for p in ai_precautions if p not in matched_precautions]
                    # Return up to 10 precautions
                    return combined[:10]
                return ai_precautions
            else:
                # If no proper JSON array is found, try to parse the whole response
                ai_precautions = json.loads(result)
                if isinstance(ai_precautions, list):
                    if matched_precautions:
                        # Combine AI precautions with our fallback precautions
                        combined = matched_precautions + [p for p in ai_precautions if p not in matched_precautions]
                        # Return up to 10 precautions
                        return combined[:10]
                    return ai_precautions
                
                # If still no valid list, manually extract with regex
                ai_precautions = re.findall(r'"([^"]+)"', result)
                if ai_precautions:
                    if matched_precautions:
                        # Combine AI precautions with our fallback precautions
                        combined = matched_precautions + [p for p in ai_precautions if p not in matched_precautions]
                        # Return up to 10 precautions
                        return combined[:10]
                    return ai_precautions
                
                # Last resort: split by newlines and extract lines that look like recommendations
                lines = result.split('\n')
                recommendations = []
                for line in lines:
                    # Remove numbers, bullets, etc. at the beginning
                    clean_line = re.sub(r'^[\d\.\s\-\*]+', '', line).strip()
                    if clean_line and len(clean_line) > 15:  # Avoid short fragments
                        recommendations.append(clean_line)
                
                if matched_precautions:
                    # Combine with our fallback precautions
                    combined = matched_precautions + [p for p in recommendations if p not in matched_precautions]
                    # Return up to 10 precautions
                    return combined[:10]
                return recommendations
        except json.JSONDecodeError:
            # If not valid JSON, split by newlines and clean up
            lines = result.split('\n')
            recommendations = []
            for line in lines:
                # Remove numbers, bullets, etc. at the beginning
                clean_line = re.sub(r'^[\d\.\s\-\*]+', '', line).strip()
                if clean_line and len(clean_line) > 15:  # Avoid short fragments
                    recommendations.append(clean_line)
            
            if matched_precautions:
                # Combine with our fallback precautions
                combined = matched_precautions + [p for p in recommendations if p not in matched_precautions]
                # Return up to 10 precautions
                return combined[:10]
            return recommendations[:10]  # Limit to 10 recommendations
            
    except Exception as e:
        logger.error(f"Error generating precautions with AI: {str(e)}")
        
        # If we have matched precautions from our fallback database, use those
        if matched_precautions:
            # Remove duplicates while preserving order
            unique_precautions = []
            for item in matched_precautions:
                if item not in unique_precautions:
                    unique_precautions.append(item)
            
            # Limit to 10 precautions
            if len(unique_precautions) > 10:
                unique_precautions = unique_precautions[:10]
            
            return unique_precautions
        
        # Otherwise, return generic precautions
        return CONDITION_PRECAUTIONS_FALLBACK["generic"]

def batch_process_terms(terms: List[str]) -> Dict[str, str]:
    """
    Process multiple terms efficiently, with optimizations to reduce API calls.
    Returns a dictionary mapping terms to their explanations.
    """
    # Initialize results dictionary
    results = {}
    
    # Filter out terms we already have in our fallback dictionary
    known_terms = [term for term in terms if term.lower() in MEDICAL_TERMS_FALLBACK]
    unknown_terms = [term for term in terms if term.lower() not in MEDICAL_TERMS_FALLBACK]
    
    # Add the known terms to results directly from fallback dictionary
    for term in known_terms:
        results[term] = MEDICAL_TERMS_FALLBACK[term.lower()]
    
    # If we don't have any unknown terms, return the results immediately
    if not unknown_terms:
        return results
    
    # Process unknown terms in batches to reduce API calls
    try:
        # Group similar terms together for batch processing
        stemmer = PorterStemmer()
        term_stems = {}
        for term in unknown_terms:
            # Get the stem of the term
            stem = stemmer.stem(term.lower())
            if stem not in term_stems:
                term_stems[stem] = []
            term_stems[stem].append(term)
        
        # Process each group of similar terms
        for stem, similar_terms in term_stems.items():
            if len(similar_terms) == 1:
                # Just one term with this stem, get explanation directly
                term = similar_terms[0]
                try:
                    explanation = get_term_explanation(term)
                    if explanation:
                        results[term] = explanation
                        # Cache this result in our in-memory dictionary
                        MEDICAL_TERMS_FALLBACK[term.lower()] = explanation
                except Exception as e:
                    logger.error(f"Error processing term {term}: {str(e)}")
                    # Try to generate a basic explanation
                    basic_explanation = generate_basic_explanation(term)
                    if basic_explanation:
                        results[term] = basic_explanation
                        MEDICAL_TERMS_FALLBACK[term.lower()] = basic_explanation
            else:
                # Multiple similar terms, batch process them
                try:
                    # Create a prompt that asks for explanations of all terms in this group
                    terms_list = ", ".join(similar_terms)
                    prompt = f"""Define the following medical terms in simple language that a patient would understand: {terms_list}.
                    
                    Format your response as a JSON object where the keys are the medical terms and the values are their explanations.
                    Example format: {{"term1": "explanation1", "term2": "explanation2"}}
                    Each explanation should be 1-2 sentences maximum."""
                    
                    # Call the API
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful medical assistant that explains medical terminology in simple language."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=500,
                    )
                    
                    # Process the response
                    result = response.choices[0].message.content.strip()
                    
                    try:
                        # Try to parse the response as JSON
                        explanations = json.loads(result)
                        
                        # Add explanations to results
                        for term in similar_terms:
                            if term in explanations:
                                explanation = explanations[term]
                                results[term] = explanation
                                # Cache this result
                                MEDICAL_TERMS_FALLBACK[term.lower()] = explanation
                            else:
                                # Try case variations
                                found = False
                                for key in explanations:
                                    if key.lower() == term.lower():
                                        explanation = explanations[key]
                                        results[term] = explanation
                                        MEDICAL_TERMS_FALLBACK[term.lower()] = explanation
                                        found = True
                                        break
                                
                                if not found:
                                    # Generate a basic explanation
                                    basic_explanation = generate_basic_explanation(term)
                                    if basic_explanation:
                                        results[term] = basic_explanation
                                        MEDICAL_TERMS_FALLBACK[term.lower()] = basic_explanation
                    
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract explanations with regex
                        logger.warning(f"Failed to parse batch response as JSON, trying regex: {result}")
                        for term in similar_terms:
                            # Look for patterns like "term: explanation" or "term - explanation"
                            pattern = fr'("{term}"|{term})[\s:,-]+([^"]+?)[,.]\s'
                            matches = re.findall(pattern, result, re.IGNORECASE)
                            if matches:
                                explanation = matches[0][1].strip()
                                results[term] = explanation
                                MEDICAL_TERMS_FALLBACK[term.lower()] = explanation
                            else:
                                # Generate a basic explanation
                                basic_explanation = generate_basic_explanation(term)
                                if basic_explanation:
                                    results[term] = basic_explanation
                                    MEDICAL_TERMS_FALLBACK[term.lower()] = basic_explanation
                
                except Exception as e:
                    logger.error(f"Error batch processing terms {similar_terms}: {str(e)}")
                    # Generate basic explanations for all terms in the batch
                    for term in similar_terms:
                        basic_explanation = generate_basic_explanation(term)
                        if basic_explanation:
                            results[term] = basic_explanation
                            MEDICAL_TERMS_FALLBACK[term.lower()] = basic_explanation
    
    except Exception as e:
        logger.error(f"Error in batch_process_terms: {str(e)}")
        # Fall back to individual processing with basic explanations
        for term in unknown_terms:
            if term not in results:
                basic_explanation = generate_basic_explanation(term)
                if basic_explanation:
                    results[term] = basic_explanation
                    MEDICAL_TERMS_FALLBACK[term.lower()] = basic_explanation
    
    # If any terms are still missing, generate basic explanations
    for term in terms:
        if term not in results:
            basic_explanation = generate_basic_explanation(term)
            if basic_explanation:
                results[term] = basic_explanation
                # Cache this result
                MEDICAL_TERMS_FALLBACK[term.lower()] = basic_explanation
            else:
                # Last resort fallback
                results[term] = f"A medical term related to {term.split()[-1] if ' ' in term else term}."
    
    return results

# Function to analyze symptoms and suggest severity levels
def analyze_symptoms(text: str) -> Dict[str, Any]:
    """
    Analyze symptoms mentioned in the medical report and assess potential severity
    """
    try:
        if not openai.api_key:
            logger.warning("OpenAI API key not set")
            return {"error": "AI service not configured"}
        
        prompt = f"""
        You are a medical AI assistant analyzing a medical report.
        Based on the following excerpt from a medical report, identify:
        1. Key symptoms mentioned
        2. The apparent severity of each symptom (mild, moderate, severe)
        3. Any potential red flags that might need immediate attention
        
        Medical report excerpt:
        {text[:4000]}  # Limit text length to avoid exceeding token limits
        
        Format your response as JSON with the following structure:
        {{
            "symptoms": [
                {{"name": "symptom name", "severity": "mild/moderate/severe", "description": "brief explanation"}},
                ...
            ],
            "red_flags": ["urgent concern 1", "urgent concern 2", ...],
            "general_assessment": "brief overall assessment"
        }}
        """
        
        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical AI assistant analyzing medical reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Extract the JSON response
        analysis = response.choices[0].message['content'].strip()
        import json
        result = json.loads(analysis)
        
        return result
    
    except Exception as e:
        logger.error(f"Error analyzing symptoms: {e}")
        return {"error": f"Could not analyze symptoms due to technical issues: {str(e)}"}