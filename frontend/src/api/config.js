/**
 * API configuration and utilities
 */

// Get the base URL for API calls
export const getBaseURL = () => {
  // Get subdomain from the current URL
  const getCurrentSubdomain = () => {
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    
    // If it's localhost or has a subdomain
    if (hostname === 'localhost' || parts.length > 2) {
      if (parts[0] !== 'localhost' && parts[0] !== 'www') {
        return parts[0];
      }
    }
    return null;
  };

  const subdomain = getCurrentSubdomain();
  if (subdomain) {
    return `http://${subdomain}.localhost:8000`;
  }
  return 'http://localhost:8000';
};

// Get authentication headers
export const getAuthHeader = () => {
  const token = localStorage.getItem('authToken');
  const headers = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Add subdomain host header if needed
  const getCurrentSubdomain = () => {
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    
    if (hostname === 'localhost' || parts.length > 2) {
      if (parts[0] !== 'localhost' && parts[0] !== 'www') {
        return parts[0];
      }
    }
    return null;
  };

  const subdomain = getCurrentSubdomain();
  if (subdomain) {
    headers['Host'] = `${subdomain}.localhost`;
  }
  
  return headers;
};
