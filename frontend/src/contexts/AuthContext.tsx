import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useTenant } from './TenantContext'

interface User {
  id: number
  email: string
  first_name: string
  last_name: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { getTenantApiUrl, getCurrentSubdomain } = useTenant()

  useEffect(() => {
    // Check for existing token on page load
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken) {
      setToken(storedToken)
      fetchUserInfo(storedToken)
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchUserInfo = async (authToken: string): Promise<boolean> => {
    try {
      const subdomain = getCurrentSubdomain()
      const apiBaseUrl = getTenantApiUrl()
      
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/me/`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
          ...(subdomain && { 'Host': `${subdomain}.localhost` }),
        },
      })

      if (response.ok) {
        const result = await response.json()
        const userData = result.data || result
        setUser(userData)
        setIsLoading(false)
        return true
      } else {
        logout()
        return false
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
      logout()
      return false
    }
  }

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      setIsLoading(true)
      
      const subdomain = getCurrentSubdomain()
      const apiBaseUrl = getTenantApiUrl()
      
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(subdomain && { 'Host': `${subdomain}.localhost` }),
        },
        body: JSON.stringify({ email, password }),
      })

      const data = await response.json()

      if (response.ok) {
        const { access, user: userData } = data
        setToken(access)
        setUser(userData)
        localStorage.setItem('auth_token', access)
        
        setIsLoading(false)
        return { success: true }
      } else {
        setIsLoading(false)
        return { 
          success: false, 
          error: data.error || 'Invalid email or password' 
        }
      }
    } catch (error) {
      setIsLoading(false)
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      }
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    setIsLoading(false)
    localStorage.removeItem('auth_token')
  }

  const value = {
    user,
    token,
    isLoading,
    login,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
