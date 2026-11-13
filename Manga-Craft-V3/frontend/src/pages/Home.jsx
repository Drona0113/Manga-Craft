import { useState, useEffect } from 'react';
import api from '../services/api';

function Home() {
  const [apiStatus, setApiStatus] = useState('Checking...');

  useEffect(() => {
    checkApi();
  }, []);

  const checkApi = async () => {
    try {
      const response = await api.get('/health');
      setApiStatus(response.data.status || 'Connected');
    } catch (error) {
      setApiStatus('Disconnected');
    }
  };

  return (
    <div className="text-center py-12">
      <h2 className="text-4xl font-bold text-white mb-4">Welcome to MangaCraft V3</h2>
      <p className="text-xl text-gray-400 mb-8">AI-Powered Manga Creation Workspace</p>
      <div className="mb-8">
        <span className="text-gray-400">API Status: </span>
        <span className={apiStatus === 'healthy' ? 'text-green-400' : 'text-red-400'}>
          {apiStatus}
        </span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        <div className="bg-[#2a2a2a] rounded-xl p-6 border border-[#3a3a3a]">
          <h3 className="text-xl font-semibold text-white mb-2">Projects</h3>
          <p className="text-gray-400">Manage your manga projects</p>
        </div>
        <div className="bg-[#2a2a2a] rounded-xl p-6 border border-[#3a3a3a]">
          <h3 className="text-xl font-semibold text-white mb-2">AI Chat</h3>
          <p className="text-gray-400">Interact with AI for assistance</p>
        </div>
        <div className="bg-[#2a2a2a] rounded-xl p-6 border border-[#3a3a3a]">
          <h3 className="text-xl font-semibold text-white mb-2">Panels</h3>
          <p className="text-gray-400">Upload and analyze manga panels</p>
        </div>
      </div>
    </div>
  );
}

export default Home;
