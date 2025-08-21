import { createContext, useContext, ReactNode } from 'react'

interface TenantContextType {
  getCurrentSubdomain: () => string | null
  isMainDomain: () => boolean
  getTenantApiUrl: () => string
}

const TenantContext = createContext<TenantContextType | undefined>(undefined)

export function TenantProvider({ children }: { children: ReactNode }) {
  const getCurrentSubdomain = () => {
    const hostname = window.location.hostname
    if (hostname === 'localhost' || !hostname.includes('.')) {
      return null
    }
    
    const parts = hostname.split('.')
    return parts[0] // Return the subdomain part
  }

  const isMainDomain = () => {
    return getCurrentSubdomain() === null
  }

  const getTenantApiUrl = () => {
    const subdomain = getCurrentSubdomain()
    if (subdomain) {
      return `http://${subdomain}.localhost:8000`
    }
    return 'http://localhost:8000'
  }

  const value = {
    getCurrentSubdomain,
    isMainDomain,
    getTenantApiUrl
  }

  return (
    <TenantContext.Provider value={value}>
      {children}
    </TenantContext.Provider>
  )
}

export function useTenant() {
  const context = useContext(TenantContext)
  if (context === undefined) {
    throw new Error('useTenant must be used within a TenantProvider')
  }
  return context
}
