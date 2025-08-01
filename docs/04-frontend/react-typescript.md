# ⚛️ React TypeScript Integration

Complete guide for building a modern React TypeScript frontend that integrates seamlessly with the ClientIQ API.

## 🚀 Quick Setup

### Prerequisites

- **Node.js 18+**
- **TypeScript 5+**  
- **React 18+**
- Basic knowledge of React hooks and TypeScript

### 1. Create React TypeScript Project

```bash
# Create new Next.js project with TypeScript
npx create-next-app@latest clientiq-frontend --typescript --tailwind --app

# Or create React app with Vite
npm create vite@latest clientiq-frontend -- --template react-ts

cd clientiq-frontend
npm install
```

### 2. Install Essential Dependencies

```bash
# HTTP client and state management
npm install axios @tanstack/react-query

# Form handling
npm install react-hook-form @hookform/resolvers zod

# UI components (optional but recommended)
npm install @headlessui/react @heroicons/react

# Date handling
npm install date-fns

# Development dependencies
npm install -D @types/node
```

## 🔧 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Basic UI elements
│   ├── forms/          # Form components
│   └── layout/         # Layout components
├── hooks/              # Custom React hooks
├── lib/                # Utility libraries
│   ├── api/           # API client and types
│   ├── auth/          # Authentication logic
│   └── utils/         # Helper functions
├── pages/              # Next.js pages (or routes/)
├── stores/             # Global state management
├── types/              # TypeScript type definitions
└── styles/             # Global styles
```

## 🌐 API Client Setup

### Base API Configuration

Create `lib/api/client.ts`:

```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

// API Response types
export interface APIResponse<T = any> {
  success: boolean;
  data: T;
  meta?: {
    timestamp: string;
    pagination?: {
      page: number;
      per_page: number;
      total: number;
      total_pages: number;
    };
  };
}

export interface APIError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
  meta: {
    timestamp: string;
  };
}

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          await this.handleTokenRefresh();
          // Retry original request
          return this.client.request(error.config);
        }
        return Promise.reject(error);
      }
    );
  }

  private getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private async handleTokenRefresh() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      this.redirectToLogin();
      return;
    }

    try {
      const response = await axios.post('/auth/refresh/', {
        refresh_token: refreshToken,
      });
      
      const { access_token } = response.data.data;
      localStorage.setItem('access_token', access_token);
    } catch (error) {
      this.redirectToLogin();
    }
  }

  private redirectToLogin() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }

  // Generic request method
  async request<T = any>(config: AxiosRequestConfig): Promise<APIResponse<T>> {
    const response = await this.client.request(config);
    return response.data;
  }

  // Convenience methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    return this.request<T>({ ...config, method: 'GET', url });
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    return this.request<T>({ ...config, method: 'POST', url, data });
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    return this.request<T>({ ...config, method: 'PUT', url, data });
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    return this.request<T>({ ...config, method: 'PATCH', url, data });
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    return this.request<T>({ ...config, method: 'DELETE', url });
  }
}

export const apiClient = new APIClient();
```

### TypeScript Types

Create `types/api.ts`:

```typescript
// User types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_tenant_admin: boolean;
  user_type: 'admin' | 'manager' | 'user' | 'viewer';
  created_at: string;
  updated_at: string;
  tenant?: Tenant;
  role?: Role;
}

// Tenant types
export interface Tenant {
  id: string;
  name: string;
  schema_name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  subscription?: Subscription;
  domains: Domain[];
}

export interface Domain {
  id: string;
  domain: string;
  is_primary: boolean;
  tenant: string;
}

// Subscription types
export interface Subscription {
  id: string;
  plan: SubscriptionPlan;
  billing_cycle: 'monthly' | 'yearly';
  status: 'active' | 'inactive' | 'cancelled' | 'past_due';
  current_period_start: string;
  current_period_end: string;
  created_at: string;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price_monthly: string;
  price_yearly: string;
  max_users: number;
  max_storage_gb: number;
  features: Record<string, any>;
  is_active: boolean;
}

// Permission types
export interface Permission {
  id: string;
  name: string;
  codename: string;
  description?: string;
}

export interface Role {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  permissions: Permission[];
}

// Demo request types
export interface DemoRequest {
  id: string;
  company_name: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  job_title?: string;
  company_size?: string;
  industry?: string;
  message?: string;
  status: 'pending' | 'processing' | 'approved' | 'converted' | 'failed' | 'rejected';
  created_at: string;
  updated_at: string;
}

// Form types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  company_name: string;
}

export interface UserForm {
  email: string;
  first_name: string;
  last_name: string;
  user_type: User['user_type'];
  is_active: boolean;
}

// API response types
export interface PaginatedResponse<T> {
  results: T[];
  next?: string;
  previous?: string;
  has_next: boolean;
  has_previous: boolean;
}

export interface ListParams {
  page?: number;
  limit?: number;
  search?: string;
  ordering?: string;
  [key: string]: any;
}
```

## 🔐 Authentication System

### Auth Context

Create `lib/auth/AuthContext.tsx`:

```typescript
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User } from '@/types/api';
import { apiClient } from '@/lib/api/client';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setState(prev => ({ ...prev, isLoading: false }));
      return;
    }

    try {
      await refreshUser();
    } catch (error) {
      console.error('Auth initialization failed:', error);
      logout();
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/login/', {
        email,
        password,
      });

      const { access_token, refresh_token, user } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
      });
    } catch (error) {
      throw new Error('Login failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
    });
  };

  const refreshUser = async () => {
    try {
      const response = await apiClient.get('/auth/me/');
      const user = response.data;

      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
      });
    } catch (error) {
      throw new Error('Failed to refresh user');
    }
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Protected Route Component

Create `components/auth/ProtectedRoute.tsx`:

```typescript
import React, { ReactNode } from 'react';
import { useAuth } from '@/lib/auth/AuthContext';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  requireAuth?: boolean;
  requiredPermissions?: string[];
}

export function ProtectedRoute({ 
  children, 
  requireAuth = true,
  requiredPermissions = [] 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && requireAuth && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, requireAuth, router]);

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (requireAuth && !isAuthenticated) {
    return null;
  }

  // Check permissions if required
  if (requiredPermissions.length > 0 && user) {
    const hasPermission = requiredPermissions.every(permission =>
      user.role?.permissions.some(p => p.codename === permission)
    );

    if (!hasPermission) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
            <p className="text-gray-600">You don't have permission to access this page.</p>
          </div>
        </div>
      );
    }
  }

  return <>{children}</>;
}
```

## 🎣 Custom API Hooks

### Base Query Hooks

Create `hooks/useAPI.ts`:

```typescript
import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query';
import { apiClient, APIResponse } from '@/lib/api/client';
import { ListParams, PaginatedResponse } from '@/types/api';

// Generic list hook
export function useList<T>(
  endpoint: string,
  params?: ListParams,
  options?: Omit<UseQueryOptions<APIResponse<PaginatedResponse<T>>>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: [endpoint, params],
    queryFn: () => apiClient.get<PaginatedResponse<T>>(endpoint, { params }),
    ...options,
  });
}

// Generic detail hook
export function useDetail<T>(
  endpoint: string,
  id: string | undefined,
  options?: Omit<UseQueryOptions<APIResponse<T>>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: [endpoint, id],
    queryFn: () => apiClient.get<T>(`${endpoint}${id}/`),
    enabled: !!id,
    ...options,
  });
}

// Generic create mutation
export function useCreate<T, TVariables = any>(endpoint: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TVariables) => apiClient.post<T>(endpoint, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [endpoint] });
    },
  });
}

// Generic update mutation
export function useUpdate<T, TVariables = any>(endpoint: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TVariables }) =>
      apiClient.patch<T>(`${endpoint}${id}/`, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [endpoint] });
      queryClient.invalidateQueries({ queryKey: [endpoint, id] });
    },
  });
}

// Generic delete mutation
export function useDelete(endpoint: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`${endpoint}${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [endpoint] });
    },
  });
}
```

### Specific API Hooks

Create `hooks/useUsers.ts`:

```typescript
import { User, UserForm } from '@/types/api';
import { useList, useDetail, useCreate, useUpdate, useDelete } from './useAPI';

// Users hooks
export const useUsers = (params?: any) => useList<User>('/users/', params);
export const useUser = (id?: string) => useDetail<User>('/users/', id);
export const useCreateUser = () => useCreate<User, UserForm>('/users/');
export const useUpdateUser = () => useUpdate<User, Partial<UserForm>>('/users/');
export const useDeleteUser = () => useDelete('/users/');

// Current user hook
export const useCurrentUser = () => useDetail<User>('/auth/', 'me');

// User permissions hook
export const useUserPermissions = (userId?: string) =>
  useDetail<string[]>('/users/', userId ? `${userId}/permissions` : undefined);
```

## 📝 Form Components

### Login Form

Create `components/forms/LoginForm.tsx`:

```typescript
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/lib/auth/AuthContext';
import { useRouter } from 'next/router';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      await login(data.email, data.password);
      router.push('/dashboard');
    } catch (error) {
      setError('root', {
        message: 'Invalid email or password',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email address
        </label>
        <input
          {...register('email')}
          type="email"
          autoComplete="email"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          {...register('password')}
          type="password"
          autoComplete="current-password"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
        )}
      </div>

      {errors.root && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{errors.root.message}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isLoading ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  );
}
```

### User Management Form

Create `components/forms/UserForm.tsx`:

```typescript
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { User, UserForm as UserFormData } from '@/types/api';

const userSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  user_type: z.enum(['admin', 'manager', 'user', 'viewer']),
  is_active: z.boolean(),
});

interface UserFormProps {
  user?: User;
  onSubmit: (data: UserFormData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function UserForm({ user, onSubmit, onCancel, isLoading = false }: UserFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: user || {
      email: '',
      first_name: '',
      last_name: '',
      user_type: 'user',
      is_active: true,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
            First Name
          </label>
          <input
            {...register('first_name')}
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          {errors.first_name && (
            <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
            Last Name
          </label>
          <input
            {...register('last_name')}
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          {errors.last_name && (
            <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email Address
        </label>
        <input
          {...register('email')}
          type="email"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="user_type" className="block text-sm font-medium text-gray-700">
          User Type
        </label>
        <select
          {...register('user_type')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="user">User</option>
          <option value="manager">Manager</option>
          <option value="admin">Admin</option>
          <option value="viewer">Viewer</option>
        </select>
        {errors.user_type && (
          <p className="mt-1 text-sm text-red-600">{errors.user_type.message}</p>
        )}
      </div>

      <div className="flex items-center">
        <input
          {...register('is_active')}
          type="checkbox"
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
          Active
        </label>
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : user ? 'Update User' : 'Create User'}
        </button>
      </div>
    </form>
  );
}
```

## 📱 Main App Setup

### App Configuration

Create `pages/_app.tsx` (Next.js) or update `src/App.tsx` (Vite):

```typescript
import React from 'react';
import type { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from '@/lib/auth/AuthContext';
import '@/styles/globals.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        if (error?.response?.status === 401) return false;
        return failureCount < 3;
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export default function App({ Component, pageProps }: AppProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Component {...pageProps} />
        <ReactQueryDevtools initialIsOpen={false} />
      </AuthProvider>
    </QueryClientProvider>
  );
}
```

### Environment Configuration

Create `.env.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# App Configuration
NEXT_PUBLIC_APP_NAME=ClientIQ
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_BETA_FEATURES=false
```

## 🎨 UI Components

### Data Table Component

Create `components/ui/DataTable.tsx`:

```typescript
import React from 'react';
import { PaginatedResponse } from '@/types/api';

interface Column<T> {
  key: keyof T | string;
  label: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  data: PaginatedResponse<T>;
  columns: Column<T>[];
  isLoading?: boolean;
  onPageChange?: (page: number) => void;
  onSort?: (field: string, direction: 'asc' | 'desc') => void;
}

export function DataTable<T extends { id: string }>({
  data,
  columns,
  isLoading,
  onPageChange,
  onSort,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-10 bg-gray-200 rounded mb-4"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 bg-gray-100 rounded mb-2"></div>
        ))}
      </div>
    );
  }

  return (
    <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key as string}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.results.map((item) => (
            <tr key={item.id}>
              {columns.map((column) => (
                <td
                  key={column.key as string}
                  className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                >
                  {column.render
                    ? column.render(item)
                    : String(item[column.key as keyof T] || '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div className="flex-1 flex justify-between sm:hidden">
          <button className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            Previous
          </button>
          <button className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            Next
          </button>
        </div>
        <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-gray-700">
              Showing <span className="font-medium">{data.results.length}</span> results
            </p>
          </div>
          <div>
            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
              {/* Pagination controls */}
            </nav>
          </div>
        </div>
      </div>
    </div>
  );
}
```

## 🚀 Example Pages

### Users List Page

Create `pages/users/index.tsx`:

```typescript
import React, { useState } from 'react';
import { useUsers, useDeleteUser } from '@/hooks/useUsers';
import { DataTable } from '@/components/ui/DataTable';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { User } from '@/types/api';

export default function UsersPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const { data: usersData, isLoading } = useUsers({ search: searchTerm });
  const deleteUser = useDeleteUser();

  const columns = [
    {
      key: 'first_name',
      label: 'Name',
      render: (user: User) => `${user.first_name} ${user.last_name}`,
    },
    { key: 'email', label: 'Email' },
    { key: 'user_type', label: 'Role' },
    {
      key: 'is_active',
      label: 'Status',
      render: (user: User) => (
        <span
          className={`px-2 py-1 text-xs rounded-full ${
            user.is_active
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {user.is_active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (user: User) => (
        <div className="flex space-x-2">
          <button className="text-blue-600 hover:text-blue-900">Edit</button>
          <button
            onClick={() => deleteUser.mutate(user.id)}
            className="text-red-600 hover:text-red-900"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  return (
    <ProtectedRoute requiredPermissions={['manage_users']}>
      <div className="space-y-6">
        <div className="sm:flex sm:items-center">
          <div className="sm:flex-auto">
            <h1 className="text-xl font-semibold text-gray-900">Users</h1>
            <p className="mt-2 text-sm text-gray-700">
              Manage your team members and their permissions.
            </p>
          </div>
        </div>

        <div className="flex justify-between">
          <input
            type="text"
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-lg block w-full shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm border-gray-300 rounded-md"
          />
          <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
            Add User
          </button>
        </div>

        {usersData && (
          <DataTable
            data={usersData.data}
            columns={columns}
            isLoading={isLoading}
          />
        )}
      </div>
    </ProtectedRoute>
  );
}
```

## 🔧 Development Tools

### API Response Inspector

Create `components/dev/APIInspector.tsx`:

```typescript
import React, { useState } from 'react';

interface APIInspectorProps {
  data: any;
  title?: string;
}

export function APIInspector({ data, title = 'API Response' }: APIInspectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (process.env.NODE_ENV === 'production') {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-gray-800 text-white px-3 py-1 rounded text-xs"
      >
        {title}
      </button>
      
      {isOpen && (
        <div className="absolute bottom-8 right-0 w-96 max-h-96 overflow-auto bg-gray-900 text-green-400 text-xs p-4 rounded shadow-lg font-mono">
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

## 📚 Next Steps

With this comprehensive setup, you have:

- ✅ **Type-safe API client** with automatic token management
- ✅ **Authentication system** with context and protected routes  
- ✅ **Custom hooks** for API operations using React Query
- ✅ **Form components** with validation using React Hook Form
- ✅ **Reusable UI components** for common patterns
- ✅ **Development tools** for debugging

### Recommended Next Steps

1. **State Management**: Add Zustand or Redux Toolkit for complex state
2. **UI Library**: Integrate Shadcn/ui or Chakra UI for comprehensive components
3. **Testing**: Set up Jest and React Testing Library
4. **Deployment**: Configure for Vercel, Netlify, or your preferred platform

### Additional Resources

- [🧪 Testing Guide](../05-development/testing.md)
- [🎨 UI Component Library](./ui-components.md)
- [🔐 Advanced Authentication](./auth-flow.md)
- [🏢 Multi-Tenant Frontend](./multi-tenant-ui.md)

---

**Happy coding!** 🚀
