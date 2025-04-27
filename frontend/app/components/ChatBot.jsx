"use client";

import { useState, useRef, useEffect } from "react";
import { sendChatMessage, updateApiKey } from "../services/api";
import SpeechToText from "./SpeechToText";
import ChatExport from "./ChatExport";

const ChatBot = ({ reportId, originalText }) => {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm your medical AI assistant. How can I help you understand your medical report today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState("unknown"); // Can be 'unknown', 'online', or 'offline'
  const [showApiModal, setShowApiModal] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [apiUpdateStatus, setApiUpdateStatus] = useState({ type: "", message: "" });
  const messagesEndRef = useRef(null);
  const [showExportPanel, setShowExportPanel] = useState(false);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  
  // Check API connection status based on message content
  useEffect(() => {
    // Check the last assistant message for offline mode indicators
    const assistantMessages = messages.filter(msg => msg.role === "assistant");
    if (assistantMessages.length > 0) {
      const lastMessage = assistantMessages[assistantMessages.length - 1].content;
      if (lastMessage.includes("OFFLINE MODE") || lastMessage.includes("offline mode")) {
        setApiStatus("offline");
      } else if (apiStatus === "unknown" || apiStatus === "offline") {
        // If not explicitly offline and we haven't determined it's online yet
        setApiStatus("online");
      }
    }
  }, [messages, apiStatus]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    
    // Clear input
    setInput("");
    
    // Set loading state
    setIsLoading(true);
    
    try {
      // Convert the messages to the format expected by the API
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      // Send message to API
      const response = await sendChatMessage(input, reportId, chatHistory);
      
      // Add AI response to chat
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.response },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      // Add error message
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I'm having trouble connecting to the server. Please try again later.",
        },
      ]);
      // Set status to offline on connection errors
      setApiStatus("offline");
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle API key update
  const handleApiKeyUpdate = async (e) => {
    e.preventDefault();
    
    if (!apiKey.trim()) {
      setApiUpdateStatus({
        type: "error",
        message: "API key cannot be empty"
      });
      return;
    }
    
    try {
      setApiUpdateStatus({
        type: "loading",
        message: "Updating API key..."
      });
      
      // Call the API to update the key
      const response = await updateApiKey(apiKey);
      
      setApiUpdateStatus({
        type: "success",
        message: "API key updated successfully! You're now connected to OpenAI."
      });
      
      // Reset API status to trigger recheck
      setApiStatus("unknown");
      
      // Close the modal after a delay
      setTimeout(() => {
        setShowApiModal(false);
        setApiKey("");
        setApiUpdateStatus({ type: "", message: "" });
      }, 2000);
      
    } catch (error) {
      console.error("Error updating API key:", error);
      setApiUpdateStatus({
        type: "error",
        message: error.response?.data?.detail || "Failed to update API key. Please try again."
      });
    }
  };

  // Function to highlight medical terms in the text
  const highlightMedicalTerms = (text) => {
    // Common medical terms to highlight
    const medicalTerms = [
      "hypertension", "diabetes", "arthritis", "osteoarthritis", 
      "thrombocytopenia", "anemia", "asthma", "copd", "cancer", 
      "thyroid", "heart disease", "stroke", "kidney", "liver",
      "medication", "treatment", "diagnosis", "prognosis", "symptoms"
    ];
    
    // Split the text into parts to highlight
    let parts = [text];
    
    // For each medical term, check and highlight
    medicalTerms.forEach(term => {
      parts = parts.flatMap(part => {
        if (typeof part !== 'string') return [part];
        
        const termRegex = new RegExp(`\\b${term}\\b`, 'gi');
        const splitParts = part.split(termRegex);
        
        if (splitParts.length === 1) return [part];
        
        const result = [];
        for (let i = 0; i < splitParts.length; i++) {
          if (i > 0) {
            // This is the matched term - wrap it in a highlighted span
            result.push(
              <span key={`term-${i}`} className="font-medium text-blue-800 bg-blue-100 px-1 rounded">
                {part.match(termRegex)[i-1]}
              </span>
            );
          }
          if (splitParts[i]) {
            result.push(splitParts[i]);
          }
        }
        return result;
      });
    });
    
    return parts;
  };

  // Function to format message content with enhanced styling
  const formatMessageContent = (content) => {
    // Check if the message contains a warning notice
    if (content.includes('⚠️') || content.includes('offline mode') || content.includes('OFFLINE MODE')) {
      // Split the content by the warning pattern
      const parts = content.split(/(\n\n⚠️.+)/g);
      
      return (
        <>
          {parts.map((part, index) => {
            if (part.includes('⚠️') || part.includes('offline mode') || part.includes('OFFLINE MODE')) {
              // Render warning notice with prominent styling
              return (
                <div key={`warning-${index}`} className="mt-3 p-2 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                  <p className="text-yellow-800 font-medium">{part.trim()}</p>
                </div>
              );
            } else if (part.trim()) {
              // Render normal content with medical terms highlighted
              return part.split('\n').map((line, i) => (
                <p key={`line-${index}-${i}`} className={i > 0 ? "mt-1" : ""}>
                  {highlightMedicalTerms(line)}
                </p>
              ));
            }
            return null;
          })}
        </>
      );
    }
    
    // For messages without warnings, just highlight medical terms
    return content.split('\n').map((line, i) => (
      <p key={i} className={i > 0 ? "mt-1" : ""}>
        {highlightMedicalTerms(line)}
      </p>
    ));
  };

  // Function to handle speech recognition result
  const handleSpeechInput = (transcript) => {
    setInput(transcript);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden mt-8">
      <div className="p-4 bg-blue-800 text-white">
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-lg font-semibold">Medical AI Chat Assistant</h3>
          
          {/* API Status Indicator */}
          <div className="flex items-center">
            <div className={`w-2 h-2 rounded-full mr-1 ${
              apiStatus === "online" 
                ? "bg-green-400 animate-pulse" 
                : apiStatus === "offline" 
                  ? "bg-red-400" 
                  : "bg-gray-400"
            }`}></div>
            <span className="text-xs">
              {apiStatus === "online" 
                ? "Online AI" 
                : apiStatus === "offline" 
                  ? "Offline Mode" 
                  : "Connecting..."}
            </span>
          </div>
        </div>
        
        <p className="text-sm text-blue-100 flex items-center justify-between">
          <span>Ask questions about your medical report, conditions, or terminology</span>
          <div className="flex items-center">
            <button 
              className="text-xs bg-blue-700 hover:bg-blue-600 py-1 px-2 rounded mr-2"
              onClick={() => setShowApiModal(true)}
            >
              Set API Key
            </button>
            <button 
              className="text-xs bg-blue-700 hover:bg-blue-600 py-1 px-2 rounded mr-2"
              onClick={() => setShowExportPanel(!showExportPanel)}
            >
              {showExportPanel ? "Hide Export" : "Export Chat"}
            </button>
            <button 
              className="text-xs bg-blue-700 hover:bg-blue-600 py-1 px-2 rounded"
              onClick={() => window.alert("If you're experiencing connectivity issues with the AI, please check:\n\n1. You have a valid OpenAI API key in your .env file\n2. Your API key has sufficient quota\n3. The backend server is running properly")}
            >
              Help ⓘ
            </button>
          </div>
        </p>
      </div>
      
      {/* Export Panel - Conditional Rendering */}
      {showExportPanel && (
        <div className="p-4 bg-gray-50 border-b">
          <ChatExport messages={messages} />
        </div>
      )}
      
      {/* Offline mode warning banner - shown when API is offline */}
      {apiStatus === "offline" && (
        <div className="bg-yellow-50 border-b border-yellow-200 p-2">
          <p className="text-sm text-yellow-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <strong>Offline Mode:</strong>&nbsp;Operating with limited knowledge. Responses may be less detailed.
            <button 
              className="ml-2 text-xs bg-yellow-600 hover:bg-yellow-700 text-white py-0.5 px-2 rounded"
              onClick={() => setShowApiModal(true)}
            >
              Add API Key
            </button>
          </p>
        </div>
      )}
      
      {/* Chat messages */}
      <div className="h-96 overflow-y-auto p-4 bg-gray-50">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 ${
              message.role === "user" ? "text-right" : "text-left"
            }`}
          >
            <div
              className={`inline-block p-3 rounded-lg max-w-[80%] ${
                message.role === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-white border border-gray-200 text-gray-800 rounded-bl-none shadow-sm"
              }`}
            >
              {message.role === "user" ? (
                // User messages are displayed as is
                message.content.split('\n').map((line, i) => (
                  <p key={i} className={i > 0 ? "mt-1" : ""}>
                    {line}
                  </p>
                ))
              ) : (
                // Assistant messages get enhanced styling with warnings highlighted
                formatMessageContent(message.content)
              )}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {message.role === "user" ? "You" : (
                <span className="font-medium text-blue-700">Medical AI Assistant</span>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="text-left mb-4">
            <div className="inline-block p-3 rounded-lg bg-white border border-gray-200 rounded-bl-none shadow-sm">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input area */}
      <form onSubmit={handleSendMessage} className="p-4 border-t">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Ask about your medical report or any medical term..."
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <SpeechToText 
            onTranscript={handleSpeechInput} 
            disabled={isLoading} 
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-blue-700 text-white rounded-full px-4 py-2 font-medium hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Send
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500 text-center">
          Examples: <span className="text-blue-600">"What does hypertension mean?"</span>, <span className="text-blue-600">"What should I know about my condition?"</span>, <span className="text-blue-600">"Explain the medical terms in my report"</span>
        </div>
      </form>
      
      {/* API Key Update Modal */}
      {showApiModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold mb-4">Update OpenAI API Key</h3>
            <p className="text-sm text-gray-600 mb-4">
              Enter your OpenAI API key to enable AI features. Your key is stored securely on the server and is not shared.
            </p>
            
            <form onSubmit={handleApiKeyUpdate}>
              <div className="mb-4">
                <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
                  API Key
                </label>
                <input
                  type="password"
                  id="apiKey"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              {apiUpdateStatus.message && (
                <div className={`p-2 mb-4 rounded ${
                  apiUpdateStatus.type === "error" 
                    ? "bg-red-50 text-red-700 border border-red-100" 
                    : apiUpdateStatus.type === "success"
                      ? "bg-green-50 text-green-700 border border-green-100"
                      : "bg-blue-50 text-blue-700 border border-blue-100"
                }`}>
                  {apiUpdateStatus.type === "loading" && (
                    <div className="flex items-center">
                      <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full mr-2"></div>
                      {apiUpdateStatus.message}
                    </div>
                  )}
                  {apiUpdateStatus.type !== "loading" && apiUpdateStatus.message}
                </div>
              )}
              
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowApiModal(false);
                    setApiKey("");
                    setApiUpdateStatus({ type: "", message: "" });
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={apiUpdateStatus.type === "loading"}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {apiUpdateStatus.type === "loading" ? "Updating..." : "Update Key"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBot; 