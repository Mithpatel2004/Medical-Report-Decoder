"use client";

import { useState, useEffect } from "react";
import { extractComplexTerms, explainTerm, detectDiseases } from "../services/api";

export default function ReportAnalyzer({ reportId, originalText }) {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [complexTerms, setComplexTerms] = useState([]);
  const [detectedDiseases, setDetectedDiseases] = useState([]);
  const [precautions, setPrecautions] = useState([]);
  
  useEffect(() => {
    if (reportId && originalText) {
      analyzeReport();
    }
  }, [reportId, originalText]);
  
  const analyzeReport = async () => {
    setAnalyzing(true);
    setError(null);
    
    try {
      // Step 1: Extract complex medical terms from the report
      await extractComplexMedicalTerms();
      
      // Step 2: Detect diseases mentioned in the report
      await detectMedicalConditions();
      
    } catch (err) {
      console.error("Error analyzing report:", err);
      setError("Failed to analyze the medical report. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };
  
  const extractComplexMedicalTerms = async () => {
    try {
      setLoading(true);
      
      // Use the API service to identify complex medical terms
      const response = await extractComplexTerms(originalText, reportId);
      
      if (response && response.complex_terms) {
        // Get explanations for each complex term
        const termsWithExplanations = [];
        
        for (const term of response.complex_terms) {
          try {
            const explanationResponse = await explainTerm(term);
            
            if (explanationResponse && explanationResponse.explanation) {
              termsWithExplanations.push({
                term: term,
                explanation: explanationResponse.explanation
              });
            }
          } catch (err) {
            console.error(`Error getting explanation for ${term}:`, err);
            // Add the term with a fallback explanation
            termsWithExplanations.push({
              term: term,
              explanation: "Detailed explanation unavailable. This is a medical term mentioned in your report."
            });
          }
        }
        
        setComplexTerms(termsWithExplanations);
      }
    } catch (err) {
      console.error("Error extracting complex terms:", err);
      // Don't set error state here, as it will break the UI flow
      // Instead, show an inline error message in the UI
    } finally {
      setLoading(false);
    }
  };
  
  const detectMedicalConditions = async () => {
    try {
      setLoading(true);
      
      // Use the API service to detect diseases and get precautions
      const response = await detectDiseases(originalText, reportId);
      
      if (response) {
        if (response.detected_diseases) {
          setDetectedDiseases(response.detected_diseases);
        }
        
        if (response.precautions) {
          setPrecautions(response.precautions);
        }
      }
    } catch (err) {
      console.error("Error detecting diseases:", err);
      // Don't set error state here, as it will break the UI flow
      // The UI will handle empty results gracefully
    } finally {
      setLoading(false);
    }
  };
  
  const renderLoadingState = () => (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="animate-spin h-10 w-10 border-4 border-blue-500 rounded-full border-t-transparent mb-4"></div>
      <p className="text-gray-600">Analyzing your medical report...</p>
    </div>
  );
  
  const renderErrorState = (message) => (
    <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">
      <p className="font-medium">{message}</p>
      <p className="text-sm mt-2">Try refreshing the page or check if the server is running.</p>
    </div>
  );
  
  return (
    <div className="space-y-8 mt-8">
      {/* Complex Medical Terms Section */}
      <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4 text-blue-700">Medical Terms in Your Report</h2>
        
        {analyzing ? (
          renderLoadingState()
        ) : error ? (
          renderErrorState(error)
        ) : complexTerms.length > 0 ? (
          <div>
            <p className="text-gray-600 mb-4">We found the following medical terms in your report and simplified them for you:</p>
            
            <ul className="space-y-4 max-h-96 overflow-y-auto pr-2">
              {complexTerms.map((item, index) => (
                <li key={index} className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500 shadow-sm">
                  <span className="font-bold text-blue-800 text-lg block mb-1">{item.term}</span>
                  <div className="text-gray-800 mt-1 pl-3 border-l-2 border-gray-300">
                    <span className="text-sm text-gray-500">Simple explanation:</span>
                    <p className="font-medium">{item.explanation}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="text-gray-500 italic">No complex medical terms were found in your report.</p>
        )}
      </div>
      
      {/* Detected Diseases and Precautions Section */}
      <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4 text-blue-700">Conditions & Health Recommendations</h2>
        
        {analyzing ? (
          <div className="flex justify-center p-4">
            <div className="animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent"></div>
          </div>
        ) : error ? (
          renderErrorState(error)
        ) : detectedDiseases.length > 0 ? (
          <div>
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Conditions Mentioned in Your Report:</h3>
              <ul className="list-disc pl-5 space-y-1">
                {detectedDiseases.map((disease, index) => (
                  <li key={index} className="text-gray-700">
                    <span className="font-medium text-blue-700">{disease}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Health Recommendations:</h3>
              {precautions.length > 0 ? (
                <ul className="space-y-2 max-h-96 overflow-y-auto pr-2">
                  {precautions.map((item, index) => (
                    <li key={index} className="flex items-start">
                      <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 mr-2 flex-shrink-0 mt-0.5">
                        {index + 1}
                      </span>
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 italic">No specific recommendations available.</p>
              )}
            </div>
            
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <p className="text-sm text-yellow-800">
                <strong>Important:</strong> These recommendations are generated by AI based on your report. Always consult with your healthcare provider for personalized advice.
              </p>
            </div>
          </div>
        ) : (
          <p className="text-gray-500 italic">No specific health conditions were detected in your report.</p>
        )}
      </div>
    </div>
  );
} 