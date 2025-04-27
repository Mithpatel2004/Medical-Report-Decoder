"use client";

import { useState, useEffect } from "react";
import { explainTerm } from "../services/api";

const MedicalGlossary = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTerm, setSelectedTerm] = useState(null);
  const [termDetails, setTermDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  
  // Common medical terms shown in the glossary
  const commonMedicalTerms = [
    { id: 1, term: "Hypertension", description: "High blood pressure" },
    { id: 2, term: "Diabetes mellitus", description: "A group of metabolic disorders characterized by high blood sugar" },
    { id: 3, term: "Myocardial infarction", description: "Heart attack" },
    { id: 4, term: "Arthritis", description: "Inflammation of joints" },
    { id: 5, term: "Asthma", description: "Chronic lung condition that affects the airways" },
    { id: 6, term: "Osteoporosis", description: "Bone disease where bone density is reduced" },
    { id: 7, term: "Pneumonia", description: "Infection that inflames air sacs in lungs" },
    { id: 8, term: "COPD", description: "Chronic Obstructive Pulmonary Disease" },
    { id: 9, term: "Hyperlipidemia", description: "High levels of fat particles in the blood" },
    { id: 10, term: "Hypothyroidism", description: "Underactive thyroid gland" },
    { id: 11, term: "Anemia", description: "Lack of healthy red blood cells to carry oxygen" },
    { id: 12, term: "Gastritis", description: "Inflammation of the stomach lining" },
    { id: 13, term: "Bronchitis", description: "Inflammation of the bronchial tubes" },
    { id: 14, term: "Hepatitis", description: "Inflammation of the liver" },
    { id: 15, term: "Nephritis", description: "Inflammation of the kidneys" },
    { id: 16, term: "Thrombocytopenia", description: "Low platelet count" },
    { id: 17, term: "Leukocytosis", description: "Increased white blood cell count" },
    { id: 18, term: "Hypoglycemia", description: "Low blood sugar" },
    { id: 19, term: "Hyperglycemia", description: "High blood sugar" },
    { id: 20, term: "Arrhythmia", description: "Irregular heartbeat" }
  ];
  
  // Filter terms based on search
  const filteredTerms = searchTerm.trim() === "" 
    ? commonMedicalTerms 
    : commonMedicalTerms.filter(term => 
        term.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
        term.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
      
  // Get detailed explanation for a term
  const getTermDetails = async (term) => {
    setIsLoading(true);
    setErrorMessage("");
    setSelectedTerm(term);
    
    try {
      const result = await explainTerm(term.term);
      setTermDetails(result.explanation);
    } catch (error) {
      console.error("Error fetching term details:", error);
      setErrorMessage("Failed to get term details. The server might be in offline mode.");
      // Fallback explanation from our basic description
      setTermDetails(term.description);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Alphabetical sections for term browsing
  const alphabetSections = {};
  commonMedicalTerms.forEach(term => {
    const firstLetter = term.term[0].toUpperCase();
    if (!alphabetSections[firstLetter]) {
      alphabetSections[firstLetter] = [];
    }
    alphabetSections[firstLetter].push(term);
  });
  
  // Sort alphabetically
  const sortedLetters = Object.keys(alphabetSections).sort();
  
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden mt-8">
      <div className="p-4 bg-blue-800 text-white">
        <h3 className="text-lg font-semibold">Medical Terminology Glossary</h3>
        <p className="text-sm text-blue-100">Browse common medical terms and get detailed explanations</p>
      </div>
      
      {/* Search bar */}
      <div className="p-4 border-b">
        <div className="relative">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search medical terms..."
            className="w-full px-4 py-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm("")}
              className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          )}
        </div>
      </div>
      
      <div className="flex flex-col md:flex-row">
        {/* Term list */}
        <div className="md:w-1/3 border-r overflow-y-auto h-96 p-2">
          {searchTerm.trim() !== "" ? (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-800 px-2">Search Results</h4>
              <div className="mt-1">
                {filteredTerms.length > 0 ? (
                  filteredTerms.map(term => (
                    <button
                      key={term.id}
                      onClick={() => getTermDetails(term)}
                      className={`block w-full text-left px-3 py-2 rounded text-sm ${
                        selectedTerm?.id === term.id
                          ? "bg-blue-100 text-blue-900 font-medium"
                          : "hover:bg-gray-100 text-gray-900"
                      }`}
                    >
                      {term.term}
                    </button>
                  ))
                ) : (
                  <p className="text-gray-700 text-sm p-3">No terms found for "{searchTerm}"</p>
                )}
              </div>
            </div>
          ) : (
            sortedLetters.map(letter => (
              <div key={letter} className="mb-4">
                <h4 className="text-sm font-medium text-gray-800 px-2">{letter}</h4>
                <div className="mt-1">
                  {alphabetSections[letter].map(term => (
                    <button
                      key={term.id}
                      onClick={() => getTermDetails(term)}
                      className={`block w-full text-left px-3 py-2 rounded text-sm ${
                        selectedTerm?.id === term.id
                          ? "bg-blue-100 text-blue-900 font-medium"
                          : "hover:bg-gray-100 text-gray-900"
                      }`}
                    >
                      {term.term}
                    </button>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
        
        {/* Term details */}
        <div className="md:w-2/3 p-4">
          {selectedTerm ? (
            <div>
              <h3 className="text-xl font-bold text-gray-900">{selectedTerm.term}</h3>
              
              <div className="mt-4">
                {isLoading ? (
                  <div className="flex justify-center items-center h-40">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-700"></div>
                  </div>
                ) : errorMessage ? (
                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
                    <p className="text-yellow-800 font-medium">{errorMessage}</p>
                    <p className="mt-2 text-gray-800">{termDetails}</p>
                  </div>
                ) : (
                  <div className="prose prose-blue max-w-none">
                    <p className="text-gray-900">{termDetails}</p>
                  </div>
                )}
              </div>
              
              {/* Quick navigation for related terms */}
              {!isLoading && (
                <div className="mt-6">
                  <h4 className="text-sm font-medium text-gray-800">Related Terms</h4>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {commonMedicalTerms
                      .filter(term => 
                        term.id !== selectedTerm.id && 
                        (term.description.toLowerCase().includes(selectedTerm.term.toLowerCase()) || 
                         selectedTerm.description.toLowerCase().includes(term.term.toLowerCase())))
                      .slice(0, 5)
                      .map(term => (
                        <button
                          key={term.id}
                          onClick={() => getTermDetails(term)}
                          className="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-900 font-medium hover:bg-gray-200"
                        >
                          {term.term}
                        </button>
                      ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-gray-600">
              <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <p className="mt-4 text-gray-700 font-medium">Select a term to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MedicalGlossary; 