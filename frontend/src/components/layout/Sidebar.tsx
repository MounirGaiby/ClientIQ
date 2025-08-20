import React from 'react';
import Link from 'next/link';
import { usePathname, useParams } from 'next/navigation';
import { 
  HomeIcon, 
  UsersIcon, 
  UserCircleIcon,
  PhoneIcon,
  CogIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const pathname = usePathname();
  const params = useParams();
  const subdomain = params?.subdomain as string;

  // Build navigation based on tenant context
  const navigation = [
    { name: 'Dashboard', href: `/tenant/${subdomain}/dashboard`, icon: HomeIcon },
    { name: 'Contacts', href: `/tenant/${subdomain}/contacts`, icon: UserCircleIcon },
    { name: 'Companies', href: `/tenant/${subdomain}/companies`, icon: BuildingOfficeIcon },
    { name: 'Leads', href: `/tenant/${subdomain}/leads`, icon: PhoneIcon },
    { name: 'Users', href: `/tenant/${subdomain}/users`, icon: UsersIcon },
    { name: 'Settings', href: `/tenant/${subdomain}/settings`, icon: CogIcon },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" onClick={onClose}>
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" aria-hidden="true" />
        </div>
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Sidebar header */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
            <Link href={`/tenant/${subdomain}/dashboard`} className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <div>
                <span className="text-xl font-semibold text-gray-900">ClientIQ</span>
                {subdomain && <span className="ml-2 text-sm text-gray-500">({subdomain})</span>}
              </div>
            </Link>
            {/* Close button for mobile */}
            <button
              onClick={onClose}
              className="lg:hidden text-gray-500 hover:text-gray-900"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-2">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`
                    flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150
                    ${isActive 
                      ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700' 
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <item.icon 
                    className={`mr-3 h-5 w-5 ${isActive ? 'text-blue-700' : 'text-gray-400'}`} 
                    aria-hidden="true" 
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Sidebar footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              Version 1.0.0
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
