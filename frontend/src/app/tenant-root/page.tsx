'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function TenantRootPage() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4 animate-pulse">
            <span className="text-white font-bold text-lg">C</span>
          </div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md mx-auto">
        <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-6">
          <span className="text-white font-bold text-2xl">C</span>
        </div>
        <h1 className="text-3xl font-semibold text-gray-900 mb-4">Welcome to ClientIQ</h1>
        
        {user ? (
          <div>
            <p className="text-gray-600 mb-6">Hello, {user.first_name}! Ready to get started?</p>
            <Link 
              href="/dashboard"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Go to Dashboard
            </Link>
          </div>
        ) : (
          <div>
            <p className="text-gray-600 mb-6">Please sign in to access your CRM dashboard.</p>
            <div className="space-x-4">
              <Link 
                href="/login"
                className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Sign In
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
