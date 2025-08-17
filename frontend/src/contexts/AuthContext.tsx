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

  const fetchUserInfo = useCallback(async (authToken: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me/`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
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
      const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        const { access_token, user: userData } = data;
        setToken(access_token);
        setUser(userData);
        localStorage.setItem('auth_token', access_token);
        setIsLoading(false);
        return { success: true };
      } else {
        setIsLoading(false);
        return { success: false, error: data.message || 'Login failed' };
      }
    } catch {
      setIsLoading(false);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setIsLoading(false);
    localStorage.removeItem('auth_token');
  };

  const refreshToken = async (): Promise<boolean> => {
    const storedToken = localStorage.getItem('auth_token');
    if (!storedToken) return false;

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/refresh/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${storedToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        localStorage.setItem('auth_token', data.access_token);
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
