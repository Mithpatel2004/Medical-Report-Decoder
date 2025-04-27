"use client";

import { useState } from "react";
import { explainTerm } from "../services/api";

export default function SimplifiedWords({ text }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [additionalTerm, setAdditionalTerm] = useState("");
  const [explanations, setExplanations] = useState([]);

  if (!text) return null;
  
  // Enhanced function to extract medical terms with their explanations
  const extractMedicalTerms = (text) => {
    // Look for pattern like "term (meaning: explanation)"
    const regex = /([A-Za-z\-]+)( \(meaning: [^)]+\))/g;
    const matches = [...text.matchAll(regex)];
    
    // Also look for pattern like "medical term [explanation]" often used in reports
    const altRegex = /([A-Za-z\-]+) \[([^\]]+)\]/g;
    const altMatches = [...text.matchAll(altRegex)];
    
    const results = [];
    
    // Process primary regex matches
    matches.forEach(match => {
      const term = match[1];
      const explanation = match[2].replace(" (meaning: ", "").replace(")", "");
      
      // Avoid duplicates
      if (!results.some(item => item.term.toLowerCase() === term.toLowerCase())) {
        results.push({ term, explanation });
      }
    });
    
    // Process alternative regex matches
    altMatches.forEach(match => {
      const term = match[1];
      const explanation = match[2];
      
      // Avoid duplicates
      if (!results.some(item => item.term.toLowerCase() === term.toLowerCase())) {
        results.push({ term, explanation });
      }
    });
    
    // Sort alphabetically
    results.sort((a, b) => a.term.localeCompare(b.term));
    
    if (results.length === 0) {
      return [];
    }
    
    return results;
  };

  // Add a function to request explanation for additional terms
  const handleExplainTerm = async () => {
    if (!additionalTerm.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await explainTerm(additionalTerm.trim());
      
      if (response && response.explanation) {
        // Add the new explanation to our list
        setExplanations([
          ...explanations,
          {
            term: additionalTerm.trim(),
            explanation: response.explanation
          }
        ]);
        
        // Reset input
        setAdditionalTerm("");
      } else {
        setError("Could not get an explanation for this term.");
      }
    } catch (err) {
      console.error("Error explaining term:", err);
      setError("Failed to get explanation. The server might be offline.");
    } finally {
      setLoading(false);
    }
  };

  // Get initial medical terms
  const medicalTerms = extractMedicalTerms(text);
  
  // Combine extracted terms with any additional explanations requested
  const allTerms = [
    ...medicalTerms,
    ...explanations.filter(exp => !medicalTerms.some(mt => mt.term.toLowerCase() === exp.term.toLowerCase()))
  ].sort((a, b) => a.term.localeCompare(b.term));

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg mt-6 border border-gray-200">
      <h2 className="text-xl font-bold mb-4 text-blue-700">Medical Terms Explained</h2>
      
      {/* Search for additional terms */}
      <div className="mb-6">
        <label htmlFor="additionalTerm" className="block text-sm font-medium text-gray-700 mb-1">
          Need explanation for another medical term?
        </label>
        <div className="flex">
          <input
            id="additionalTerm"
            type="text"
            value={additionalTerm}
            onChange={(e) => setAdditionalTerm(e.target.value)}
            placeholder="Enter medical term..."
            className="flex-1 border border-gray-300 rounded-l-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => e.key === "Enter" && handleExplainTerm()}
          />
          <button
            onClick={handleExplainTerm}
            disabled={loading || !additionalTerm.trim()}
            className={`px-4 py-2 rounded-r-lg ${
              loading || !additionalTerm.trim()
                ? "bg-gray-300 text-gray-500 cursor-not-allowed" 
                : "bg-blue-600 text-white hover:bg-blue-700"
            }`}
          >
            {loading ? "..." : "Explain"}
          </button>
        </div>
        {error && (
          <p className="text-red-600 text-sm mt-1">{error}</p>
        )}
      </div>
      
      <div className="prose">
        {allTerms.length > 0 ? (
          <div>
            <p className="text-gray-600 mb-3 text-sm">Found {allTerms.length} medical terms:</p>
            <ul className="space-y-3 list-none p-0 max-h-96 overflow-y-auto pr-2">
              {allTerms.map((item, index) => (
                <li key={index} className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500 shadow-sm">
                  <span className="font-bold text-blue-800 text-lg block mb-1">{item.term}</span>
                  {item.explanation && (
                    <div className="text-gray-800 mt-1 pl-2 border-l-2 border-gray-300">
                      <span className="text-sm text-gray-500">Meaning:</span>
                      <p className="font-medium">{item.explanation}</p>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200 text-yellow-800">
            <p>No medical terms were found for automatic explanation.</p>
            <p className="mt-2 text-sm">You can enter specific terms above to get explanations.</p>
          </div>
        )}
      </div>
    </div>
  );
}