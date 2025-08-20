'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  tenant?: {
    id: string;
    name: string;
    domain: string;
  };
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isLoading: boolean;
  refreshToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // API base URL - in production this would come from environment variables
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Get current tenant subdomain
  const getCurrentSubdomain = () => {
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      const parts = hostname.split('.');
      if (parts.length > 1 && parts[0] !== 'www' && parts[0] !== 'localhost') {
        return parts[0];
      } else if (hostname.includes('localhost') && parts.length > 1) {
        return parts[0];
      }
    }
    return null;
  };

  // Make API request with proper tenant headers
  const makeApiRequest = async (url: string, options: RequestInit = {}) => {
    const subdomain = getCurrentSubdomain();
    const headers = {
      'Content-Type': 'application/json',
      ...(subdomain && { 'Host': `${subdomain}.localhost` }),
      ...options.headers,
    };

    return fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
    });
  };

  const fetchUserInfo = useCallback(async (authToken: string): Promise<boolean> => {
    try {
      const subdomain = getCurrentSubdomain();
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me/`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
          ...(subdomain && { 'Host': `${subdomain}.localhost` }),
        },
      });

      if (response.ok) {
        const result = await response.json();
        // Handle Django's response format
        const userData = result.data || result;
        setUser(userData);
        setIsLoading(false);
        return true;
      } else {
        // Token is invalid
        logout();
        return false;
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
      logout();
      return false;
    }
  }, [API_BASE_URL]);

  useEffect(() => {
    // Check for existing token on page load
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
      // Verify token is still valid by fetching user info
      fetchUserInfo(storedToken);
    } else {
      setIsLoading(false);
    }
  }, [fetchUserInfo]);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      setIsLoading(true);
      
      const subdomain = getCurrentSubdomain();
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(subdomain && { 'Host': `${subdomain}.localhost` }),
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Django returns 'access' not 'access_token'
        const { access, refresh } = data;
        setToken(access);
        localStorage.setItem('auth_token', access);
        localStorage.setItem('refresh_token', refresh);
        
        // Fetch user info with the new token
        await fetchUserInfo(access);
        
        setIsLoading(false);
        return { success: true };
      } else {
        setIsLoading(false);
        return { success: false, error: data.detail || data.message || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      setIsLoading(false);
      return { success: false, error: 'Network error. Please check if the backend server is running.' };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setIsLoading(false);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
  };

  const refreshToken = async (): Promise<boolean> => {
    const storedRefreshToken = localStorage.getItem('refresh_token');
    if (!storedRefreshToken) return false;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: storedRefreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access);
        localStorage.setItem('auth_token', data.access);
        return true;
      } else {
        logout();
        return false;
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      logout();
      return false;
    }
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isLoading,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
