Medical Report Decoder 🩺📄
A Python-based AI tool that makes medical reports understandable to everyone.Upload your medical documents and get simplified explanations, smart summaries, and personalized health precautions.

🌟 Features
* PDF & Image Processing: Extract text from medical reports in PDF format or from images (prescriptions, lab results).
* Medical Text Simplification: Automatically explains complex medical terminology in plain language.
* Smart Summarization: Get the key points from lengthy medical documents.
* Condition Detection: Identifies medical conditions mentioned in your reports.
* Personalized Precautions: Generates practical health advice based on detected conditions.
* Complex Term Explanation: Click on any term you don't understand for a detailed explanation.
* No Data Storage: Your medical information is processed temporarily and never permanently stored.

🚀 Technology Stack
* FastAPI – High-performance backend API
* Hugging Face Transformers – Text summarization and explanation
* PyTesseract & pdfplumber – Document text extraction
* OpenAI GPT Models – Medical text simplification and deep explanations
* React/Next.js – Frontend interface (separate repository)

💻 Installation

# Create and activate virtual environment
python -m venv env
source env/bin/activate        # On Windows: env\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your OpenAI API key to the .env file

# Start the server
uvicorn app:app --reload

🔧 Requirements
* Python 3.8+
* OpenAI API Key (for advanced medical explanations)
* Tesseract OCR installed on your system (for image processing)

🖥️ Usage
1. Start the server:uvicorn app:app --reload
2. Upload your medical report through the /upload/ API endpoint or use the React frontend.
3. Receive:
    * Simplified explanations
    * Smart summaries
    * Personalized health precautions

📡 API Endpoints
* POST /upload/ — Upload and process a medical report
* POST /explain-term/ — Get detailed explanation for any medical term
* POST /extract-complex-terms/ — Extract complex medical terms from text
* POST /detect-diseases/ — Detect diseases and provide precautions

📷 Screenshots
![alt text](<Screenshot 2025-04-27 at 6.21.27 PM.png>)
![alt text](<Screenshot 2025-04-27 at 6.21.51 PM.png>) ![alt text](<Screenshot 2025-04-27 at 6.22.07 PM.png>) ![alt text](<Screenshot 2025-04-27 at 6.22.15 PM.png>) ![alt text](<Screenshot 2025-04-27 at 6.22.36 PM.png>)

Acknowledgements
* OpenAI — for the amazing language models
* Hugging Face — for open-source transformer models
* PyTesseract, pdfplumber — for document processing
* The Open Source Community — for incredible libraries that made this project possible
