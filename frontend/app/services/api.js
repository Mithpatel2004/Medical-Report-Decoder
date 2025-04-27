import axios from "axios";

// Create axios instance with base URL
const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000", // Backend URL
});

// API functions
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const response = await API.post("/upload/", formData);
    return response.data;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
};

// Creating or updating the API service file with chat function

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const extractComplexTerms = async (text, reportId = null) => {
  try {
    const response = await API.post("/extract-complex-terms/", {
      text,
      report_id: reportId,
    });
    return response.data;
  } catch (error) {
    console.error("Error extracting complex terms:", error);
    throw error;
  }
};

export const explainTerm = async (term) => {
  try {
    const response = await API.post("/explain-term/", {
      term,
    });
    return response.data;
  } catch (error) {
    console.error("Error explaining term:", error);
    throw error;
  }
};

export const detectDiseases = async (text, reportId = null) => {
  try {
    const response = await API.post("/detect-diseases/", {
      text,
      report_id: reportId,
    });
    return response.data;
  } catch (error) {
    console.error("Error detecting diseases:", error);
    throw error;
  }
};

export const getReport = async (reportId) => {
  try {
    const response = await API.get(`/report/${reportId}`);
    return response.data;
  } catch (error) {
    console.error("Error getting report:", error);
    throw error;
  }
};

// Adding the chat API function
export const sendChatMessage = async (question, reportId = null, chatHistory = []) => {
  try {
    const response = await API.post("/chat/", {
      question,
      report_id: reportId,
      chat_history: chatHistory,
    });
    return response.data;
  } catch (error) {
    console.error("Error sending chat message:", error);
    throw error;
  }
};

// Update OpenAI API key
export const updateApiKey = async (apiKey) => {
  try {
    const response = await API.post("/update-api-key/", {
      api_key: apiKey,
    });
    return response.data;
  } catch (error) {
    console.error("Error updating API key:", error);
    throw error;
  }
};