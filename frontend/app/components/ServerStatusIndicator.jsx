"use client";

import { useState, useEffect } from 'react';

const ServerStatusIndicator = () => {
  const [isServerRunning, setIsServerRunning] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        setIsChecking(true);
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        setIsServerRunning(data.status === 'healthy');
      } catch (error) {
        console.error('Server status check failed:', error);
        setIsServerRunning(false);
      } finally {
        setIsChecking(false);
      }
    };
    
    // Check immediately on load
    checkServerStatus();
    
    // Set up interval to check every 30 seconds
    const intervalId = setInterval(checkServerStatus, 30000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);
  
  if (isChecking) {
    return (
      <div className="fixed bottom-4 right-4 bg-gray-800 text-white py-1 px-3 rounded-full text-sm shadow-lg flex items-center">
        <div className="animate-pulse mr-2 h-2 w-2 bg-gray-400 rounded-full"></div>
        Checking server...
      </div>
    );
  }
  
  if (!isServerRunning) {
    return (
      <div className="fixed bottom-4 right-4 bg-red-600 text-white py-2 px-4 rounded-full text-sm shadow-lg flex items-center">
        <div className="mr-2 h-2 w-2 bg-white rounded-full"></div>
        <div>
          <p className="font-medium">Server Offline</p>
          <p className="text-xs opacity-80">Backend API not running. Some features will be unavailable.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="fixed bottom-4 right-4 bg-green-600 text-white py-1 px-3 rounded-full text-sm shadow-lg flex items-center">
      <div className="animate-pulse mr-2 h-2 w-2 bg-white rounded-full"></div>
      Server Online
    </div>
  );
};

export default ServerStatusIndicator; 