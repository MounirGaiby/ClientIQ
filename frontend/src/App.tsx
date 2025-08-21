import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import DemoPage from './pages/DemoPage'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import { AuthProvider } from './contexts/AuthContext'
import { TenantProvider } from './contexts/TenantContext'
import ProtectedRoute from './components/ProtectedRoute'

// Detect if we're on a subdomain (tenant)
const hostname = window.location.hostname
const isTenant = hostname !== 'localhost' && hostname.includes('.')

function App() {
  return (
    <TenantProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gradient-to-br from-primary-400 via-primary-500 to-accent-500">
            <Routes>
              {isTenant ? (
                // Tenant routes (subdomain.localhost)
                <>
                  <Route path="/" element={<LoginPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route 
                    path="/dashboard" 
                    element={
                      <ProtectedRoute>
                        <Dashboard />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/users" 
                    element={
                      <ProtectedRoute>
                        <Dashboard activeTab="users" />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/contacts" 
                    element={
                      <ProtectedRoute>
                        <Dashboard activeTab="contacts" />
                      </ProtectedRoute>
                    } 
                  />
                </>
              ) : (
                // Main domain routes (localhost)
                <>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/demo" element={<DemoPage />} />
                </>
              )}
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </TenantProvider>
  );
};

export default App;
