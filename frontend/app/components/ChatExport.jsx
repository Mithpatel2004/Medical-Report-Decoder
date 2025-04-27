"use client";

import { useState } from "react";

const ChatExport = ({ messages }) => {
  const [exportFormat, setExportFormat] = useState("text");
  const [loading, setLoading] = useState(false);
  
  // Format the messages for export
  const formatMessagesForText = () => {
    return messages.map(msg => {
      const sender = msg.role === "user" ? "You" : "Medical AI Assistant";
      return `${sender}:\n${msg.content}\n\n`;
    }).join("");
  };
  
  // Generate file name with date
  const generateFileName = () => {
    const now = new Date();
    const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    return `medical-ai-chat-${dateStr}`;
  };
  
  // Handle the export action
  const handleExport = async () => {
    setLoading(true);
    
    try {
      if (exportFormat === "text") {
        // Generate text content
        const textContent = formatMessagesForText();
        
        // Create and download the text file
        const blob = new Blob([textContent], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${generateFileName()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else if (exportFormat === "pdf") {
        // For client-side PDF generation, we'll use html-to-pdf conversion
        // This is a simplified approach, in a real app you might use a library like jsPDF
        
        // Create HTML content
        let htmlContent = `
          <html>
            <head>
              <title>Medical AI Chat Export</title>
              <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #2563eb; }
                .chat { margin-top: 20px; }
                .message { margin-bottom: 15px; }
                .user { text-align: right; }
                .assistant { text-align: left; }
                .content { padding: 10px; border-radius: 8px; display: inline-block; max-width: 80%; }
                .user .content { background-color: #2563eb; color: white; }
                .assistant .content { background-color: #f3f4f6; border: 1px solid #e5e7eb; }
                .sender { font-size: 0.8em; color: #6b7280; margin-top: 4px; }
              </style>
            </head>
            <body>
              <h1>Medical AI Assistant Chat Export</h1>
              <p>Generated on ${new Date().toLocaleString()}</p>
              <div class="chat">
        `;
        
        // Add each message
        messages.forEach(msg => {
          const role = msg.role;
          const sender = role === "user" ? "You" : "Medical AI Assistant";
          
          htmlContent += `
            <div class="message ${role}">
              <div class="content">${msg.content.replace(/\n/g, '<br>')}</div>
              <div class="sender">${sender}</div>
            </div>
          `;
        });
        
        // Close HTML tags
        htmlContent += `
              </div>
            </body>
          </html>
        `;
        
        // For browsers that support it, we can use the print dialog to save as PDF
        const printWindow = window.open('', '_blank');
        printWindow.document.write(htmlContent);
        printWindow.document.close();
        printWindow.focus();
        
        // Small delay to ensure the content is loaded
        setTimeout(() => {
          printWindow.print();
          printWindow.close();
        }, 500);
      }
    } catch (error) {
      console.error("Error exporting chat:", error);
      alert("Failed to export chat. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  // Disable the export button if there are no messages
  const hasMessages = messages.length > 1; // More than just the welcome message
  
  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-white">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">Export Conversation</h3>
      
      <div className="flex flex-col space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Export Format</label>
          <div className="flex space-x-4">
            <label className="inline-flex items-center">
              <input
                type="radio"
                className="form-radio text-blue-600"
                name="exportFormat"
                value="text"
                checked={exportFormat === "text"}
                onChange={() => setExportFormat("text")}
              />
              <span className="ml-2">Text File (.txt)</span>
            </label>
            
            <label className="inline-flex items-center">
              <input
                type="radio"
                className="form-radio text-blue-600"
                name="exportFormat"
                value="pdf"
                checked={exportFormat === "pdf"}
                onChange={() => setExportFormat("pdf")}
              />
              <span className="ml-2">PDF Document (.pdf)</span>
            </label>
          </div>
        </div>
        
        <button
          onClick={handleExport}
          disabled={loading || !hasMessages}
          className={`px-4 py-2 rounded flex items-center justify-center ${
            hasMessages
              ? "bg-blue-600 hover:bg-blue-700 text-white"
              : "bg-gray-300 text-gray-500 cursor-not-allowed"
          }`}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Exporting...
            </>
          ) : (
            <>
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export Chat
            </>
          )}
        </button>
        
        {!hasMessages && (
          <p className="text-sm text-gray-500 italic">Start a conversation to enable export.</p>
        )}
      </div>
    </div>
  );
};

export default ChatExport; 