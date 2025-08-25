// frontend/src/api/client.ts (Fixed to use your auth pattern)
import axios from 'axios';
import { getAuthHeader, getBaseURL } from './config';

const API_BASE_URL = getBaseURL() || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth headers to requests using your existing pattern
apiClient.interceptors.request.use((config) => {
  // Use your existing getAuthHeader function which handles auth_token and subdomain
  const authHeaders = getAuthHeader();
  config.headers = {
    ...config.headers,
    ...authHeaders,
  };
  
  console.log('🔑 Request headers:', config.headers);
  console.log('🌐 Request URL:', config.url);
  
  return config;
});

// Handle responses and errors
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Success: ${response.status} ${response.config.url}`);
    return response;
  },
  async (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`);
    console.error('❌ Error details:', error.response?.data);
    
    if (error.response?.status === 401) {
      console.warn('⚠️ Unauthorized - redirecting to login');
      // Clear any stored tokens
      localStorage.removeItem('auth_token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Redirect to login
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);