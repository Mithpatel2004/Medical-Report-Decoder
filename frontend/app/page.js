"use client";

import { useState } from "react";
import FileUploader from "./components/FileUploader";
import ReportAnalyzer from "./components/ReportAnalyzer";
import SummarizedReport from "./components/SummarizedReport";
import MedicalGlossary from "./components/MedicalGlossary";
import ServerStatusIndicator from "./components/ServerStatusIndicator";

export default function Home() {
  const [processedData, setProcessedData] = useState(null);
  const [activeTab, setActiveTab] = useState("report");
  
  const handleProcessingComplete = (data) => {
    setProcessedData(data);
  };
  
  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-5xl mx-auto">
        <header className="text-center mb-10">
          <h1 className="text-3xl font-bold text-blue-800 mb-2">
            Medical Report AI Assistant
          </h1>
          <p className="text-gray-600">
            Upload a medical report to get AI-powered explanations and health recommendations
          </p>
        </header>
        
        <FileUploader onProcessingComplete={handleProcessingComplete} />
        
        {processedData && (
          <div className="mt-8 space-y-8">
            <SummarizedReport summary={processedData.summary} />
            
            {/* Tab navigation */}
            <div className="border-b border-gray-200">
              <nav className="flex -mb-px">
                <button
                  onClick={() => setActiveTab("report")}
                  className={`py-3 px-6 font-medium text-sm ${
                    activeTab === "report"
                      ? "border-b-2 border-blue-600 text-blue-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Report Analysis
                </button>
                <button
                  onClick={() => setActiveTab("glossary")}
                  className={`py-3 px-6 font-medium text-sm flex items-center ${
                    activeTab === "glossary"
                      ? "border-b-2 border-blue-600 text-blue-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Medical Glossary
                  <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Reference</span>
                </button>
              </nav>
            </div>
            
            {/* Tab content */}
            {activeTab === "report" ? (
              <ReportAnalyzer 
                reportId={processedData.report_id || "temp-id"} 
                originalText={processedData.original_text} 
              />
            ) : (
              <>
                <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-4 rounded-md">
                  <p className="text-green-700">
                    <strong>Medical Terminology Glossary:</strong> Browse our comprehensive glossary of medical terms and get detailed explanations. 
                    This feature helps you understand common medical terminology in your reports.
                  </p>
                </div>
                <MedicalGlossary />
              </>
            )}
          </div>
        )}
        
        {/* Show the medical glossary even when no report is uploaded */}
        {!processedData && (
          <div className="mt-12">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h2 className="text-xl font-semibold text-blue-800 mb-2">While You're Here...</h2>
              <p className="text-gray-700">
                Want to learn more about medical terminology? Check out our comprehensive glossary of medical terms.
              </p>
              <button
                onClick={() => setActiveTab("glossary")}
                className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition duration-200"
              >
                Explore Medical Glossary
              </button>
            </div>
            
            {activeTab === "glossary" && (
              <>
                <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-4 rounded-md">
                  <p className="text-green-700">
                    <strong>Medical Terminology Glossary:</strong> Browse our comprehensive glossary of medical terms and get detailed explanations. 
                    This feature helps you understand common medical terminology.
                  </p>
                </div>
                <MedicalGlossary />
              </>
            )}
          </div>
        )}
        
        {/* Server Status Indicator */}
        <ServerStatusIndicator />
        
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>© {new Date().getFullYear()} Medical Report AI Assistant - All rights reserved</p>
        </footer>
      </div>
    </div>
  );
}