/**
 * API configuration and utilities
 */

// Get the base URL for API calls
export const getBaseURL = () => {
  // Get subdomain from the current URL
  const getCurrentSubdomain = () => {
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    
    // If it's localhost with subdomain like acme.localhost:5173
    if (hostname.includes('localhost') && parts.length > 1) {
      if (parts[0] !== 'localhost' && parts[0] !== 'www') {
        return parts[0];
      }
    }
    // For localhost:5173 format, check if we're on a tenant subdomain
    if (hostname.includes('.localhost')) {
      return hostname.split('.')[0];
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
  const token = localStorage.getItem('auth_token');
  const headers = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Add subdomain host header if needed
  const getCurrentSubdomain = () => {
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    
    // If it's localhost with subdomain like acme.localhost:5173
    if (hostname.includes('localhost') && parts.length > 1) {
      if (parts[0] !== 'localhost' && parts[0] !== 'www') {
        return parts[0];
      }
    }
    // For localhost:5173 format, check if we're on a tenant subdomain
    if (hostname.includes('.localhost')) {
      return hostname.split('.')[0];
    }
    return null;
  };

  const subdomain = getCurrentSubdomain();
  if (subdomain) {
    headers['Host'] = `${subdomain}.localhost`;
  }
  
  return headers;
};
