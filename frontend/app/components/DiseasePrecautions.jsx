"use client";

import { useState, useEffect } from "react";

export default function DiseasePrecautions({ disease }) {
  const [precautions, setPrecautions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Enhanced disease precautions database with more detailed recommendations
  const precautionsDatabase = {
    "diabetes": [
      "Monitor blood glucose levels regularly according to your doctor's recommendations",
      "Follow a balanced, low-sugar diet with controlled carbohydrate intake",
      "Exercise regularly as recommended by your doctor (at least 150 minutes per week)",
      "Take all diabetes medications as prescribed without skipping doses",
      "Attend regular check-ups with healthcare providers for diabetes management",
      "Check feet daily for cuts, blisters, or swelling to prevent complications",
      "Maintain good dental hygiene to prevent gum disease",
      "Wear a medical ID bracelet indicating you have diabetes",
      "Know the symptoms of high and low blood sugar and how to treat them",
      "Keep regular appointments with eye doctors to check for diabetic retinopathy",
      "Monitor kidney function through regular urine and blood tests",
      "Manage stress levels as stress can affect blood glucose levels"
    ],
    "hypertension": [
      "Monitor blood pressure regularly at home with a validated blood pressure device",
      "Reduce sodium (salt) intake to less than 2,300mg per day",
      "Maintain a healthy weight through diet and exercise",
      "Exercise regularly (at least 150 minutes per week of moderate activity)",
      "Limit alcohol consumption to one drink per day for women and two for men",
      "Avoid smoking and secondhand smoke exposure",
      "Manage stress through relaxation techniques like meditation or deep breathing",
      "Follow the DASH diet (Dietary Approaches to Stop Hypertension)",
      "Take blood pressure medications as prescribed at the same time each day",
      "Limit caffeine consumption as it can temporarily raise blood pressure",
      "Get adequate sleep (7-8 hours) as poor sleep can affect blood pressure",
      "Monitor for side effects of medications and report them to your doctor"
    ],
    "asthma": [
      "Identify and avoid asthma triggers such as allergens, smoke, and pollution",
      "Take controller medications daily as prescribed even when feeling well",
      "Use rescue inhalers correctly when needed for symptom relief",
      "Follow your personalized asthma action plan developed with your doctor",
      "Get vaccinated against influenza and pneumonia to prevent respiratory infections",
      "Keep regular follow-up appointments with your pulmonologist",
      "Monitor your breathing with a peak flow meter if recommended by your doctor",
      "Clean your home regularly to reduce dust mites and other allergens",
      "Use allergen-proof covers on pillows and mattresses if allergic",
      "Consider using an air purifier in your bedroom",
      "Learn proper breathing techniques to help manage symptoms",
      "Always carry your rescue inhaler with you"
    ],
    "arthritis": [
      "Follow a gentle exercise routine to maintain joint mobility and muscle strength",
      "Apply heat therapy for stiff joints and cold therapy for acute pain and swelling",
      "Maintain a healthy weight to reduce stress on weight-bearing joints",
      "Use assistive devices like jar openers, ergonomic utensils, or a cane if needed",
      "Take pain medications and anti-inflammatories as prescribed",
      "Practice proper body mechanics when lifting or carrying objects",
      "Get adequate rest when joints are inflamed and painful",
      "Consider physical therapy for tailored exercise programs",
      "Use joint protection techniques during daily activities",
      "Try complementary therapies like acupuncture or massage with doctor approval",
      "Wear supportive footwear with good arch support",
      "Use braces or splints as recommended to support affected joints"
    ],
    "heart disease": [
      "Follow a heart-healthy diet low in saturated fats, trans fats, and cholesterol",
      "Exercise regularly as recommended by your cardiologist",
      "Take cardiac medications exactly as prescribed without missing doses",
      "Manage stress levels through relaxation techniques and counseling if needed",
      "Quit smoking and avoid all tobacco products and secondhand smoke",
      "Monitor blood pressure and cholesterol levels regularly",
      "Attend all follow-up appointments with your cardiologist",
      "Limit alcohol consumption to moderate levels",
      "Maintain a healthy weight through diet and exercise",
      "Know the warning signs of heart attack and stroke",
      "Complete cardiac rehabilitation if recommended after a cardiac event",
      "Get adequate sleep as poor sleep is linked to heart problems",
      "Manage other conditions like diabetes that affect heart health"
    ],
    "thyroid disorders": [
      "Take thyroid medications consistently at the same time daily on an empty stomach",
      "Have regular blood tests to monitor thyroid hormone levels",
      "Inform all healthcare providers about your thyroid condition",
      "Be aware of medication interactions with thyroid hormones",
      "Consider wearing a medical alert bracelet",
      "Maintain a balanced diet with appropriate iodine intake",
      "Attend regular check-ups with your endocrinologist",
      "Report any new or worsening symptoms to your doctor",
      "If you have hypothyroidism, be aware of symptoms of medication underdosing",
      "If you have hyperthyroidism, avoid excessive iodine intake",
      "Women should consult with doctors about pregnancy planning",
      "Manage stress as it can affect thyroid function"
    ],
    "pneumonia": [
      "Complete the full course of prescribed antibiotics even if feeling better",
      "Get plenty of rest to help your body recover and fight the infection",
      "Stay hydrated by drinking plenty of fluids to loosen mucus",
      "Take fever reducers and pain relievers as recommended by your doctor",
      "Use a humidifier to add moisture to the air and ease breathing",
      "Don't smoke and avoid secondhand smoke which can irritate lungs",
      "Follow up with your doctor as directed to ensure complete recovery",
      "Practice deep breathing exercises to help clear lungs",
      "Avoid alcohol which can interfere with antibiotic effectiveness",
      "Get vaccinated against pneumococcal pneumonia as recommended",
      "Wash hands frequently to prevent spreading infection to others",
      "Gradually increase activity as you recover and as recommended by your doctor"
    ],
    "covid-19": [
      "Follow isolation protocols as directed by healthcare providers",
      "Monitor oxygen levels with a pulse oximeter if recommended",
      "Rest and stay hydrated to support your immune system",
      "Take medications as prescribed for symptom management",
      "Maintain good ventilation in your living space",
      "Practice respiratory hygiene (cover coughs and sneezes)",
      "Follow up with healthcare providers about potential long-term effects",
      "Monitor for worsening symptoms that may require medical attention",
      "Consider post-COVID rehabilitation if experiencing lingering symptoms",
      "Get vaccinated and boosted as recommended after recovery",
      "Practice gentle physical activity as tolerated during recovery",
      "Monitor for mental health effects and seek support if needed"
    ],
    "copd": [
      "Take all prescribed medications including inhalers as directed",
      "Participate in pulmonary rehabilitation programs",
      "Quit smoking and avoid secondhand smoke and air pollutants",
      "Get vaccinated against influenza, pneumonia, and COVID-19",
      "Use oxygen therapy as prescribed if needed",
      "Practice breathing techniques like pursed lip breathing",
      "Conserve energy through activity pacing and energy conservation techniques",
      "Maintain a healthy weight - neither too heavy nor too thin",
      "Stay hydrated to keep mucus thin and easier to clear",
      "Avoid extreme temperatures and high altitudes when possible",
      "Learn proper inhaler technique from your healthcare provider",
      "Have an action plan for COPD flare-ups or exacerbations"
    ],
    "kidney disease": [
      "Monitor and control blood pressure as directed by your doctor",
      "Follow a kidney-friendly diet low in sodium, phosphorus, and potassium as needed",
      "Take medications as prescribed to protect kidney function",
      "Avoid non-steroidal anti-inflammatory drugs (NSAIDs) unless approved by your nephrologist",
      "Monitor fluid intake according to your doctor's recommendations",
      "Check kidney function regularly through blood and urine tests",
      "Control blood sugar if you have diabetes",
      "Maintain a healthy weight through appropriate diet and exercise",
      "Attend all scheduled appointments with your nephrologist",
      "Be aware of medication dosing changes needed due to reduced kidney function",
      "Report any new symptoms like swelling, changes in urination, or fatigue",
      "Consider a medical ID bracelet that indicates kidney disease"
    ],
    "liver disease": [
      "Avoid alcohol completely to prevent further liver damage",
      "Take all medications as prescribed by your hepatologist",
      "Avoid medications that can damage the liver, including some over-the-counter drugs",
      "Follow a liver-friendly diet as recommended by your healthcare team",
      "Get vaccinated against hepatitis A and B if not already immune",
      "Maintain a healthy weight as obesity can worsen liver disease",
      "Monitor for signs of liver problems like jaundice, abdominal swelling, or confusion",
      "Attend all follow-up appointments and liver function tests",
      "Manage other conditions like diabetes that can affect liver health",
      "Avoid raw or undercooked shellfish if you have advanced liver disease",
      "Be cautious with herbal supplements as many can affect the liver",
      "Discuss all new medications with your doctor before taking them"
    ],
    "stroke": [
      "Take blood-thinning medications exactly as prescribed",
      "Control high blood pressure through medication and lifestyle changes",
      "Monitor and manage cholesterol levels with diet and medications if needed",
      "Follow a Mediterranean or DASH diet low in salt and saturated fats",
      "Exercise regularly as recommended by your healthcare provider",
      "Quit smoking and avoid secondhand smoke exposure",
      "Limit alcohol consumption or avoid it completely",
      "Manage diabetes with proper blood sugar control if applicable",
      "Participate in stroke rehabilitation programs as recommended",
      "Use assistive devices like canes or walkers if needed for safety",
      "Make home modifications to prevent falls and support independence",
      "Attend all follow-up appointments with neurologists and therapists"
    ]
  };

  // Enhanced generic precautions for any disease
  const genericPrecautions = [
    "Follow your doctor's recommendations and complete treatment plan precisely",
    "Take all medications as prescribed without skipping doses",
    "Attend all scheduled follow-up appointments with healthcare providers",
    "Maintain a balanced, nutritious diet appropriate for your condition",
    "Stay physically active as appropriate for your condition and as advised by your doctor",
    "Get adequate rest and prioritize quality sleep (7-8 hours nightly)",
    "Manage stress through relaxation techniques, meditation, or counseling",
    "Stay up to date with all recommended vaccinations for your condition",
    "Avoid smoking and limit alcohol consumption as recommended",
    "Practice good hygiene to prevent infections",
    "Keep a record of symptoms and medication effects to discuss with your doctor",
    "Learn about your condition from reliable medical sources",
    "Consider joining a support group for your specific health condition",
    "Have emergency contacts and a plan ready if symptoms worsen",
    "Organize medications using pill organizers or reminder apps"
  ];

  useEffect(() => {
    if (disease) {
      setLoading(true);
      
      // Enhanced matching algorithm
      const normalizedDisease = disease.toLowerCase().trim();
      let matchedDisease = null;
      let matchScore = 0;
      
      // Check for exact matches first
      if (precautionsDatabase[normalizedDisease]) {
        matchedDisease = normalizedDisease;
      } else {
        // Check for partial matches with scoring
        for (const key of Object.keys(precautionsDatabase)) {
          if (normalizedDisease.includes(key) || key.includes(normalizedDisease)) {
            // Calculate match score based on length of overlap
            const newScore = key.length;
            if (newScore > matchScore) {
              matchScore = newScore;
              matchedDisease = key;
            }
          }
        }
        
        // Check for specific condition patterns
        if (!matchedDisease) {
          if (normalizedDisease.includes("blood pressure") || normalizedDisease.includes("hypertens")) {
            matchedDisease = "hypertension";
          } else if (normalizedDisease.includes("heart") || normalizedDisease.includes("cardiac") || normalizedDisease.includes("coronary")) {
            matchedDisease = "heart disease";
          } else if (normalizedDisease.includes("lung") || normalizedDisease.includes("pulmonary") || normalizedDisease.includes("respiratory")) {
            matchedDisease = "copd";
          } else if (normalizedDisease.includes("kidney") || normalizedDisease.includes("renal")) {
            matchedDisease = "kidney disease";
          }
        }
      }
      
      if (matchedDisease) {
        setPrecautions({
          disease: matchedDisease,
          list: precautionsDatabase[matchedDisease]
        });
      } else {
        // Use generic precautions if no specific match
        setPrecautions({
          disease: "general health",
          list: genericPrecautions
        });
      }
      
      setLoading(false);
    }
  }, [disease]);

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg mt-6 border border-gray-200">
      <h2 className="text-xl font-bold mb-4 text-blue-700">Recommended Precautions</h2>
      
      {loading ? (
        <div className="flex justify-center p-4">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent"></div>
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg">
          {error}
        </div>
      ) : precautions ? (
        <div>
          <p className="text-lg font-medium mb-3 text-gray-700 capitalize">
            {precautions.disease === "general health" 
              ? "General Health Recommendations" 
              : `${precautions.disease.charAt(0).toUpperCase() + precautions.disease.slice(1)} Precautions`}
          </p>
          
          <ul className="space-y-2 max-h-96 overflow-y-auto pr-2">
            {precautions.list.map((item, index) => (
              <li key={index} className="flex items-start">
                <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 mr-2 flex-shrink-0 mt-0.5">
                  {index + 1}
                </span>
                <span className="text-gray-700">{item}</span>
              </li>
            ))}
          </ul>
          
          <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <p className="text-sm text-yellow-800">
              <strong>Important:</strong> These are general recommendations. Always consult with your healthcare provider for personalized advice.
            </p>
          </div>
        </div>
      ) : (
        <p className="text-gray-500 italic">No disease information available</p>
      )}
    </div>
  );
} 