'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { UserIcon, BellIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import { useAuth } from '@/contexts/AuthContext';

interface HeaderProps {
  user?: {
    name: string;
    email: string;
    avatar?: string;
  };
  onLogout?: () => void;
}

export default function Header({ user, onLogout }: HeaderProps) {
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    if (onLogout) {
      onLogout();
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and brand */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <span className="text-xl font-semibold text-gray-900">ClientIQ</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <Link href="/dashboard" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
              Dashboard
            </Link>
            <Link href="/users" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
              Users
            </Link>
            <Link href="/reports" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
              Reports
            </Link>
            <Link href="/settings" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
              Settings
            </Link>
          </nav>

          {/* Right side icons */}
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                {/* Notifications */}
                <button className="text-gray-400 hover:text-gray-500">
                  <BellIcon className="h-6 w-6" />
                </button>

                {/* Settings */}
                <button className="text-gray-400 hover:text-gray-500">
                  <Cog6ToothIcon className="h-6 w-6" />
                </button>

                {/* User menu */}
                <div className="relative ml-3">
                  <div className="flex items-center space-x-3">
                    {user.avatar ? (
                      <Image
                        className="h-8 w-8 rounded-full"
                        src={user.avatar}
                        alt={user.name}
                        width={32}
                        height={32}
                      />
                    ) : (
                      <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                        <UserIcon className="h-5 w-5 text-gray-600" />
                      </div>
                    )}
                    <div className="hidden md:block">
                      <div className="text-sm font-medium text-gray-900">{user.name}</div>
                      <div className="text-xs text-gray-500">{user.email}</div>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="text-sm text-gray-500 hover:text-gray-900"
                    >
                      Logout
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  href="/login"
                  className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Login
                </Link>
                <Link
                  href="/signup"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
