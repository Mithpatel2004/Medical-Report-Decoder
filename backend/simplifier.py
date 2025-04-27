import re
import logging
import os
from typing import Tuple, List, Dict, Set

# Configure logging
logger = logging.getLogger(__name__)

# Comprehensive dictionary of medical terms with their simplified explanations
# This is the same dictionary from the original simplifier.py
medical_dictionary = {
    # Common medical conditions
    "hypertension": "high blood pressure",
    "hypotension": "low blood pressure",
    "tachycardia": "fast heart rate",
    "bradycardia": "slow heart rate",
    "myocardial infarction": "heart attack",
    "cerebrovascular accident": "stroke",
    "thrombocytopenia": "low platelet count",
    "leukocytosis": "high white blood cell count",
    "leukopenia": "low white blood cell count",
    "anemia": "low red blood cell count",
    "hyperglycemia": "high blood sugar",
    "hypoglycemia": "low blood sugar",
    "hepatomegaly": "enlarged liver",
    "splenomegaly": "enlarged spleen",
    "nephropathy": "kidney disease",
    "neuropathy": "nerve damage",
    "dyspnea": "difficulty breathing",
    "edema": "swelling",
    "pruritus": "itching",
    "pyrexia": "fever",
    "erythema": "redness of the skin",
    "syncope": "fainting",
    "vertigo": "dizziness",
    "dysuria": "painful urination",
    "hematuria": "blood in urine",
    "proteinuria": "protein in urine",
    "glycosuria": "sugar in urine",
    "dysphasia": "difficulty speaking",
    "dysphagia": "difficulty swallowing",
    "aphasia": "inability to speak or understand speech",
    "paresthesia": "tingling or numbness sensation",
    "hemiparesis": "weakness on one side of the body",
    "paraplegia": "paralysis of the lower body",
    "tetraplegia": "paralysis of all four limbs",
    "quadriplegia": "paralysis of all four limbs",
    "hemiplegia": "paralysis on one side of the body",
    
    # Common lab values and tests
    "hgb": "hemoglobin, which measures the amount of oxygen-carrying protein in your blood",
    "hct": "hematocrit, which measures the percentage of red blood cells in your blood",
    "wbc": "white blood cell count, which helps assess your body's ability to fight infection",
    "plt": "platelet count, which helps your blood clot",
    "creatinine": "a waste product filtered by your kidneys, used to check kidney function",
    "bun": "blood urea nitrogen, another measure of kidney function",
    "egfr": "estimated glomerular filtration rate, a measure of kidney function",
    "ast": "a liver enzyme that can indicate liver damage when elevated",
    "alt": "a liver enzyme that can indicate liver damage when elevated",
    "ldl": "low-density lipoprotein, often called 'bad cholesterol'",
    "hdl": "high-density lipoprotein, often called 'good cholesterol'",
    "inr": "international normalized ratio, which measures how quickly your blood clot",
    "a1c": "a measure of your average blood sugar over the past 2-3 months",
    "tsh": "thyroid stimulating hormone, used to check thyroid function",
    "t3": "triiodothyronine, a thyroid hormone",
    "t4": "thyroxine, a thyroid hormone",
    "mch": "mean corpuscular hemoglobin, the average amount of hemoglobin in red blood cells",
    "mchc": "mean corpuscular hemoglobin concentration, the average concentration of hemoglobin in red blood cells",
    "mcv": "mean corpuscular volume, the average size of red blood cells",
    "bmp": "basic metabolic panel, a blood test that measures several compounds in your blood",
    "cbc": "complete blood count, a blood test that evaluates overall health and detects disorders",
    "cmp": "comprehensive metabolic panel, a blood test that provides information about your body's chemical balance",
    "esr": "erythrocyte sedimentation rate, a blood test that can reveal inflammation in the body",
    "crp": "c-reactive protein, a blood test marker for inflammation in the body",
    "ana": "antinuclear antibody test, used to help diagnose autoimmune disorders",
    "psa": "prostate-specific antigen, a blood test used primarily to screen for prostate cancer",
    "troponin": "a protein found in heart muscle cells, used to detect heart attacks",
    "ck": "creatine kinase, an enzyme found in the heart, brain, skeletal muscle, used to detect damage",
    "bmp": "basic metabolic panel, a group of blood tests that measure different chemicals in the blood",
    "afib": "atrial fibrillation, an irregular heart rhythm",
    "afp": "alpha-fetoprotein, a protein produced by the liver, used as a tumor marker",
    
    # Common medications and medication types
    "nsaid": "non-steroidal anti-inflammatory drug, a type of pain reliever",
    "ppi": "proton pump inhibitor, used to reduce stomach acid",
    "acei": "angiotensin-converting enzyme inhibitor, used to treat high blood pressure",
    "arb": "angiotensin receptor blocker, used to treat high blood pressure",
    "statin": "medication used to lower cholesterol",
    "anticoagulant": "medication that prevents blood clotting",
    "antiplatelet": "medication that prevents platelets from sticking together",
    "antiarrhythmic": "medication that treats irregular heart rhythms",
    "bronchodilator": "medication that opens airways in the lungs",
    "diuretic": "medication that increases urine production to remove excess fluid",
    "antipyretic": "medication that reduces fever",
    "analgesic": "medication that relieves pain",
    "antihypertensive": "medication that lowers blood pressure",
    "antidepressant": "medication used to treat depression",
    "anxiolytic": "medication used to treat anxiety",
    "hypnotic": "medication that helps with sleep",
    "antiemetic": "medication that prevents or stops nausea and vomiting",
    "antihistamine": "medication that treats allergy symptoms",
    "laxative": "medication that helps with bowel movements",
    "antacid": "medication that neutralizes stomach acid",
    "corticosteroid": "medication that reduces inflammation",
    
    # Common procedures
    "mri": "magnetic resonance imaging, a type of scan that uses magnetic fields",
    "ct scan": "computed tomography scan, a type of X-ray that shows detailed images",
    "ekg": "electrocardiogram, which records your heart's electrical signals",
    "ecg": "electrocardiogram, which records your heart's electrical signals",
    "echo": "echocardiogram, an ultrasound of your heart",
    "pet scan": "positron emission tomography scan, which shows how tissues are functioning",
    "biopsy": "procedure to remove a small tissue sample for testing",
    "endoscopy": "procedure to look inside the body using a flexible tube with a camera",
    "colonoscopy": "procedure to examine the large intestine",
    "bronchoscopy": "procedure to examine the airways in the lungs",
    "lp": "lumbar puncture (spinal tap), procedure to collect cerebrospinal fluid",
    "thoracentesis": "procedure to remove fluid from around the lungs",
    "paracentesis": "procedure to remove fluid from the abdomen",
    
    # Common medical terminology
    "acute": "sudden or severe onset",
    "chronic": "long-lasting or recurring",
    "idiopathic": "of unknown cause",
    "benign": "not cancerous",
    "malignant": "cancerous",
    "remission": "decrease or disappearance of symptoms",
    "exacerbation": "worsening of symptoms",
    "proximal": "closer to the center of the body",
    "distal": "farther from the center of the body",
    "lesion": "area of damaged tissue",
    "nodule": "small lump or growth",
    "bilateral": "affecting both sides",
    "unilateral": "affecting only one side",
    "asymptomatic": "without symptoms",
    "symptomatic": "showing symptoms",
    "prognosis": "predicted outcome of a disease",
    "etiology": "cause of a disease",
    "pathogenesis": "development of a disease",
    "comorbidity": "presence of additional conditions",
    "contraindication": "reason not to use a particular treatment",
    "idiopathy": "disease with unknown cause",
    "congenital": "present from birth",
    "prodromal": "early symptoms before full disease onset",
    "sequela": "condition that results from a previous disease",
    "syndrome": "group of symptoms that together are characteristic of a specific disorder",
    "differential diagnosis": "process of distinguishing between conditions with similar symptoms",
    "iatrogenic": "caused by medical treatment",
    "nosocomial": "hospital-acquired infection",
    "palliative": "relieving symptoms without curing",
    "prophylactic": "preventive treatment",
    "hyperemia": "increased blood flow",
    "ischemia": "reduced blood supply",
    "necrosis": "death of body tissue",
    "atrophy": "wasting away or decrease in size",
    "hypertrophy": "increase in size",
    "stenosis": "abnormal narrowing in a blood vessel or other structure",
    "occlusion": "blockage",
    "perforation": "hole or tear",
    "dehiscence": "reopening of a wound",
    "metastasis": "spread of cancer from one part of the body to another",
}

# Dictionary mapping conditions to precautions
condition_precautions = {
    "hypertension": [
        "Monitor blood pressure regularly", 
        "Limit salt intake", 
        "Maintain a healthy weight", 
        "Exercise regularly", 
        "Take medications as prescribed"
    ],
    "diabetes": [
        "Monitor blood sugar levels regularly", 
        "Follow a balanced diet", 
        "Exercise regularly", 
        "Take medications as prescribed", 
        "Check feet daily for injuries"
    ],
    "asthma": [
        "Avoid known triggers", 
        "Take medications as prescribed", 
        "Use a peak flow meter to monitor symptoms", 
        "Have an action plan for flare-ups", 
        "Get vaccinated against flu and pneumonia"
    ],
    "heart disease": [
        "Take medications as prescribed", 
        "Follow a heart-healthy diet", 
        "Exercise regularly", 
        "Manage stress", 
        "Attend all follow-up appointments"
    ],
    "stroke": [
        "Take all medications as prescribed", 
        "Follow a low-sodium diet", 
        "Quit smoking", 
        "Limit alcohol consumption", 
        "Control blood pressure and cholesterol"
    ],
    "kidney disease": [
        "Follow a diet low in sodium, phosphorus, and protein", 
        "Take medications as prescribed", 
        "Monitor blood pressure", 
        "Avoid NSAIDs (like ibuprofen)", 
        "Stay hydrated appropriately"
    ],
    "cancer": [
        "Attend all follow-up appointments", 
        "Report new symptoms promptly", 
        "Follow nutritional guidelines from your doctor", 
        "Consider joining a support group", 
        "Practice good hygiene to prevent infections"
    ],
    "copd": [
        "Quit smoking", 
        "Avoid air pollutants", 
        "Get vaccinated against flu and pneumonia", 
        "Use oxygen as prescribed", 
        "Participate in pulmonary rehabilitation"
    ],
    "liver disease": [
        "Avoid alcohol", 
        "Take medications as prescribed", 
        "Follow dietary restrictions", 
        "Get vaccinated against hepatitis A and B", 
        "Avoid medications that can harm the liver"
    ],
    "depression": [
        "Take medications as prescribed", 
        "Attend therapy sessions", 
        "Maintain social connections", 
        "Exercise regularly", 
        "Follow a regular sleep schedule"
    ],
    "anxiety": [
        "Practice relaxation techniques", 
        "Take medications as prescribed", 
        "Attend therapy sessions", 
        "Maintain a healthy lifestyle", 
        "Identify and avoid triggers"
    ],
    "arthritis": [
        "Protect joints during activities", 
        "Maintain a healthy weight", 
        "Stay physically active", 
        "Apply heat or cold for pain relief", 
        "Take medications as prescribed"
    ],
    "osteoporosis": [
        "Get adequate calcium and vitamin D", 
        "Exercise regularly", 
        "Prevent falls by improving home safety", 
        "Take medications as prescribed", 
        "Avoid smoking and excessive alcohol"
    ]
}

# Common risk factors that might appear in medical reports
risk_patterns = {
    "smoking": [r"smok(er|ing|es)", r"tobacco use", r"pack[- ]years"],
    "alcohol": [r"alcohol (use|consumption|abuse)", r"drinks per (day|week)", r"alcoholic", r"etoh"],
    "obesity": [r"obesity", r"obese", r"high BMI", r"body mass index", r"overweight"],
    "hypertension": [r"hypertension", r"high blood pressure", r"elevated bp", r"htn"],
    "diabetes": [r"diabetes", r"diabetic", r"high blood sugar", r"hyperglycemia", r"a1c"],
    "high cholesterol": [r"hyperlipidemia", r"high cholesterol", r"elevated lipids", r"dyslipidemia"],
    "heart disease": [r"coronary (artery|heart) disease", r"chd", r"cad", r"heart attack", r"myocardial infarction"],
    "family history": [r"family history", r"genetic predisposition", r"hereditary"],
    "sedentary lifestyle": [r"sedentary", r"physical inactivity", r"lack of exercise"],
    "stress": [r"stress", r"anxiety", r"psychological stress"],
    "poor diet": [r"poor diet", r"unhealthy eating", r"high sodium diet", r"high fat diet"]
}

def find_potential_medical_terms(text: str) -> Set[str]:
    """
    Use enhanced patterns to identify potential medical terms not in our dictionary
    """
    try:
        # Enhanced patterns for medical terms
        patterns = [
            r'\b[a-z]+(itis|osis|emia|opathy|ectomy|otomy|ostomy|plasty|scopy|gram|graphy)\b',  # Common medical suffixes
            r'\b[a-z]{7,}\b',  # Long words (potential medical terms)
            r'\b[A-Z][a-z]+-(induced|associated|related|positive|negative)\b',  # Compound medical terms
            r'\b[A-Z][a-z]+/(anti-)?[A-Z][a-z]+\b',  # Medical ratios or relationships
            r'\b[A-Z][a-z]+\s+[a-z]+(itis|osis|emia|opathy|ectomy|otomy|scopy)\b',  # Multi-word medical terms
            r'\b[A-Z][a-z]+\s+[sS]yndrome\b',  # Named syndromes
            r'\b[A-Z][a-z]+\'s\s+[dD]isease\b',  # Eponymous diseases
            r'\b[A-Z][a-z]+\s+[dD]isease\b',  # Named diseases
            r'\b[A-Z][a-z]+\s+[dD]eficiency\b',  # Deficiency conditions
            r'\b[a-z]+[0-9]+\s+[dD]eficiency\b',  # Vitamin/factor deficiencies
            r'\b[sS]tage\s+[IV]+\s+[a-zA-Z]+\b',  # Staged conditions
            r'\b[gG]rade\s+[1-4]\s+[a-zA-Z]+\b',  # Graded conditions
            r'\b[tT]ype\s+[1-4]\s+[a-zA-Z]+\b',  # Typed conditions
            r'\b[a-z]+-[a-z]+\s+[sS]yndrome\b',  # Hyphenated syndromes
        ]
        
        potential_terms = set()
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                term = match.group(0).lower()
                if term not in medical_dictionary and len(term) > 5:
                    potential_terms.add(term)
        
        return potential_terms
    except Exception as e:
        logger.error(f"Error finding potential medical terms: {e}")
        return set()

def provide_general_explanation(term: str) -> str:
    """Provide a generic explanation for terms not in our dictionary"""
    try:
        # Check for common medical suffixes to give more specific explanations
        if term.endswith('itis'):
            return "a medical term indicating inflammation"
        elif term.endswith('emia'):
            return "a medical term related to blood condition"
        elif term.endswith('osis'):
            return "a medical term usually indicating a condition, disease, or abnormal process"
        elif term.endswith('opathy'):
            return "a disease or abnormal condition"
        elif term.endswith('ectomy'):
            return "a surgical removal procedure"
        elif term.endswith('otomy'):
            return "a surgical cutting procedure"
        elif term.endswith('ostomy'):
            return "a surgical procedure creating an opening"
        elif term.endswith('plasty'):
            return "a surgical repair procedure"
        elif term.endswith('scopy'):
            return "a procedure for visual examination"
        elif term.endswith('gram') or term.endswith('graphy'):
            return "a type of imaging or recording test"
        else:
            return "a medical term - click for more information"
    except Exception as e:
        logger.error(f"Error providing general explanation: {e}")
        return "a medical term"

def extract_conditions_from_text(text: str) -> List[str]:
    """
    Extract medical conditions from the text that we can provide precautions for
    """
    found_conditions = []
    for condition in condition_precautions.keys():
        # Search for the condition in the text
        if re.search(r'\b' + re.escape(condition) + r'\b', text, re.IGNORECASE):
            found_conditions.append(condition)
    
    return found_conditions

def identify_risk_factors(text: str) -> Dict[str, bool]:
    """
    Identify risk factors mentioned in the medical report
    """
    risk_factors = {}
    
    for risk_name, patterns in risk_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                risk_factors[risk_name] = True
                break
    
    return risk_factors

def simplify_text(text: str) -> Tuple[str, List[str]]:
    """
    Replace medical terms with simplified explanations and return a list of unknown terms
    """
    if not text:
        return "No text provided for simplification.", []
    
    try:
        simplified = text
        explained_terms = set()  # Track terms we've already explained
        unknown_terms = []  # Track terms that need AI explanation
        
        # First pass: Handle terms in our dictionary
        # Process longer terms first to avoid partial matches
        sorted_terms = sorted(medical_dictionary.keys(), key=len, reverse=True)
        
        for term in sorted_terms:
            try:
                # Case insensitive search with word boundaries
                pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                matches = list(pattern.finditer(simplified))
                
                # Process matches in reverse order to avoid offset issues
                for match in reversed(matches):
                    matched_term = match.group(0)
                    if matched_term.lower() not in explained_terms:
                        # First occurrence - add explanation
                        simple = medical_dictionary[term]
                        replacement = f"{matched_term} (meaning: {simple})"
                        simplified = simplified[:match.start()] + replacement + simplified[match.end():]
                        explained_terms.add(matched_term.lower())
            except Exception as term_error:
                logger.error(f"Error processing term '{term}': {term_error}")
                continue
        
        # Second pass: Try to identify other potential medical terms
        try:
            potential_terms = find_potential_medical_terms(text)
            for term in potential_terms:
                if term.lower() not in explained_terms and len(term) > 5:
                    pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                    matches = list(pattern.finditer(simplified))
                    
                    # Process matches in reverse order
                    for match in reversed(matches):
                        matched_term = match.group(0)
                        if matched_term.lower() not in explained_terms:
                            explanation = provide_general_explanation(term)
                            replacement = f"{matched_term} (possibly {explanation})"
                            simplified = simplified[:match.start()] + replacement + simplified[match.end():]
                            explained_terms.add(matched_term.lower())
                            
                            # Add to unknown terms for potential AI explanation
                            unknown_terms.append(matched_term)
        except Exception as e:
            logger.error(f"Error identifying additional terms: {e}")
        
        # Create a glossary of terms at the end
        if explained_terms:
            glossary = "\n\n--- MEDICAL TERMS GLOSSARY ---\n"
            for term_lower in sorted(explained_terms):
                try:
                    # Find the original cased version if possible
                    original_term = None
                    for match in re.finditer(r'\b\w+\b', text, re.IGNORECASE):
                        if match.group(0).lower() == term_lower:
                            original_term = match.group(0)
                            break
                    
                    term_to_use = original_term or term_lower.capitalize()
                    simple = medical_dictionary.get(term_lower.lower())
                    if not simple:
                        simple = provide_general_explanation(term_lower)
                        
                        # Mark as needing AI explanation if it's not definitive
                        if simple == "a medical term - click for more information":
                            if term_to_use not in unknown_terms:
                                unknown_terms.append(term_to_use)
                    
                    glossary += f"\n{term_to_use}: {simple}"
                except Exception as glossary_error:
                    logger.error(f"Error adding term to glossary: {glossary_error}")
                    continue
            
            simplified += glossary

        return simplified, list(set(unknown_terms))
    except Exception as e:
        logger.error(f"Error in simplify_text: {e}")
        return text + "\n\nNote: There was an error simplifying this text. Some medical terms may not be explained.", []

def generate_precautions(text: str) -> Tuple[List[str], Dict[str, bool], str]:
    """
    Generate precautions based on identified conditions and risk factors.
    Returns:
        - List of precautions
        - Dictionary of risk factors
        - Primary detected condition (or None if none detected)
    """
    try:
        # Extract conditions
        conditions = extract_conditions_from_text(text)
        
        # Identify risk factors
        risks = identify_risk_factors(text)
        
        # Generate precautions
        all_precautions = []
        
        # Add condition-specific precautions
        primary_condition = None
        if conditions:
            # Use the first condition as the primary one
            primary_condition = conditions[0]
            
        for condition in conditions:
            if condition in condition_precautions:
                all_precautions.extend(condition_precautions[condition])
        
        # Add general precautions based on risk factors
        if "smoking" in risks:
            all_precautions.append("Quit smoking and avoid secondhand smoke")
        
        if "alcohol" in risks:
            all_precautions.append("Limit alcohol consumption or avoid it completely")
        
        if "obesity" in risks:
            all_precautions.append("Work with healthcare provider on a weight management plan")
        
        if "sedentary lifestyle" in risks:
            all_precautions.append("Increase physical activity as recommended by your healthcare provider")
        
        if "stress" in risks:
            all_precautions.append("Practice stress management techniques like meditation or deep breathing")
        
        if "poor diet" in risks:
            all_precautions.append("Follow a balanced diet as recommended by your healthcare provider")
            
        # Add general precautions for everyone
        general_precautions = [
            "Take all medications exactly as prescribed",
            "Keep all follow-up appointments with healthcare providers",
            "Report new or worsening symptoms promptly",
            "Maintain a healthy lifestyle with regular exercise and balanced diet",
            "Get adequate sleep and manage stress"
        ]
        
        all_precautions.extend(general_precautions)
        
        # Remove duplicates while preserving order
        unique_precautions = []
        for p in all_precautions:
            if p not in unique_precautions:
                unique_precautions.append(p)
        
        return unique_precautions, risks, primary_condition
    
    except Exception as e:
        logger.error(f"Error generating precautions: {e}")
        return ["Error generating precautions. Please consult your healthcare provider."], {}, None