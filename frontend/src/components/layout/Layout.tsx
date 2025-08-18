'use client';

import React, { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import { Bars3Icon } from '@heroicons/react/24/outline';

interface LayoutProps {
  children: React.ReactNode;
  user?: {
    name: string;
    email: string;
    avatar?: string;
  };
  showSidebar?: boolean;
  onLogout?: () => void;
}

export default function Layout({ 
  children, 
  user, 
  showSidebar = true, 
  onLogout = () => {} 
}: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile menu button */}
      {showSidebar && (
        <button
          className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-white shadow-md"
          onClick={() => setSidebarOpen(true)}
        >
          <Bars3Icon className="h-6 w-6 text-gray-600" />
        </button>
      )}

      <div className="flex h-screen">
        {/* Sidebar */}
        {showSidebar && (
          <Sidebar 
            isOpen={sidebarOpen} 
            onClose={() => setSidebarOpen(false)} 
          />
        )}

        {/* Main content */}
        <div className={`flex-1 flex flex-col overflow-hidden ${showSidebar ? 'lg:ml-0' : ''}`}>
          {/* Header - only show for tenant domains (when showSidebar is true) */}
          {showSidebar && <Header user={user} onLogout={onLogout} />}

          {/* Page content */}
          <main className="flex-1 overflow-y-auto">
            <div className="h-full">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
