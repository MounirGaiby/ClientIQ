import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  LogOut, 
  Users, 
  ContactIcon, 
  BarChart3, 
  Settings as SettingsIcon,
  Menu,
  X,
  Plus,
  Search,
  Bell,
  Home
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTenant } from '../contexts/TenantContext';
import UserManagement from '../components/UserManagement';
import ContactManagement from '../components/ContactManagement';
import PipelineManagement from '../components/PipelineManagement';

interface DashboardProps {
  activeTab?: string;
}

const Dashboard: React.FC<DashboardProps> = ({ activeTab = 'overview' }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [currentTab, setCurrentTab] = useState(() => {
    const path = location.pathname;
    if (path === '/users') return 'users';
    if (path === '/contacts') return 'contacts';
    if (path === '/analytics') return 'analytics';
    if (path === '/settings') return 'settings';
    if (path === '/dashboard') return 'overview';
    return activeTab;
  });
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const { getCurrentSubdomain } = useTenant();

  useEffect(() => {
    const getCurrentTabFromUrl = () => {
      const path = location.pathname;
      if (path === '/users') return 'users';
      if (path === '/contacts') return 'contacts';
      if (path === '/pipeline') return 'pipeline';
      if (path === '/analytics') return 'analytics';
      if (path === '/settings') return 'settings';
      if (path === '/dashboard') return 'overview';
      return activeTab;
    };
    
    const newTab = getCurrentTabFromUrl();
    setCurrentTab(newTab);
  }, [location.pathname, activeTab]);

  const subdomain = getCurrentSubdomain();
  const tenantName = subdomain ? subdomain.charAt(0).toUpperCase() + subdomain.slice(1) : 'Demo';

  const navigation = [
    { name: 'Overview', id: 'overview', icon: Home, current: currentTab === 'overview' },
    { name: 'Pipeline', id: 'pipeline', icon: BarChart3, current: currentTab === 'pipeline' },
    { name: 'Contacts', id: 'contacts', icon: ContactIcon, current: currentTab === 'contacts' },
    { name: 'Users', id: 'users', icon: Users, current: currentTab === 'users' },
    { name: 'Analytics', id: 'analytics', icon: BarChart3, current: currentTab === 'analytics' },
    { name: 'Settings', id: 'settings', icon: SettingsIcon, current: currentTab === 'settings' },
  ];

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Mobile backdrop only */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-slate-800/90 to-slate-900/90 
        backdrop-blur-xl border-r border-orange-500/20 transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0
        shadow-2xl shadow-orange-500/10
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-orange-500/20">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg shadow-orange-500/30">
                <span className="text-white font-bold text-sm">{tenantName[0]}</span>
              </div>
              <div>
                <h1 className="text-white font-semibold text-lg">{tenantName}</h1>
                <p className="text-orange-300 text-xs">ClientIQ</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-400 hover:text-white transition-colors p-1 rounded"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    // Navigate to the appropriate route
                    const routes: Record<string, string> = {
                      'overview': '/dashboard',
                      'pipeline': '/pipeline',
                      'users': '/users',
                      'contacts': '/contacts',
                      'analytics': '/analytics',
                      'settings': '/settings'
                    };
                    navigate(routes[item.id] || '/dashboard');
                    setSidebarOpen(false);
                  }}
                  className={`
                    w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200
                    ${item.current 
                      ? 'bg-gradient-to-r from-orange-500/20 to-pink-500/20 text-white border border-orange-500/30 shadow-lg shadow-orange-500/20' 
                      : 'text-gray-300 hover:text-white hover:bg-white/5 hover:shadow-lg hover:shadow-orange-500/10'
                    }
                  `}
                >
                  <Icon className={`mr-3 h-5 w-5 ${item.current ? 'text-orange-400' : ''}`} />
                  {item.name}
                  {item.current && (
                    <div className="ml-auto w-2 h-2 bg-orange-400 rounded-full shadow-lg shadow-orange-400/50"></div>
                  )}
                </button>
              );
            })}
          </nav>

          {/* User Info & Logout */}
          <div className="p-4 border-t border-orange-500/20">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg shadow-orange-500/30">
                <span className="text-white font-semibold">
                  {user?.email?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium truncate">
                  {user?.email || 'user@example.com'}
                </p>
                <p className="text-orange-300 text-xs">Administrator</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-red-500/10 hover:border-red-500/30 border border-transparent rounded-lg transition-all duration-200"
            >
              <LogOut className="mr-3 h-4 w-4" />
              Sign Out
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar */}
        <div className="sticky top-0 z-30 bg-slate-900/80 backdrop-blur-xl border-b border-orange-500/20 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
              >
                <Menu className="h-6 w-6" />
              </button>
              
              <div className="hidden sm:flex items-center ml-4 lg:ml-0">
                <Search className="h-5 w-5 text-gray-400 mr-3" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="bg-slate-800/50 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent w-64"
                />
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                <Bell className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {currentTab === 'overview' && <Overview />}
            {currentTab === 'contacts' && <ContactManagement />}
            {currentTab === 'pipeline' && <PipelineManagement />}
            {currentTab === 'users' && <UserManagement />}
            {currentTab === 'analytics' && <Analytics />}
            {currentTab === 'settings' && <Settings />}
          </div>
        </main>
      </div>
    </div>
  );
};

const Overview = () => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Contacts"
          value="0"
          change="+0%"
          icon={ContactIcon}
          color="orange"
        />
        <StatCard
          title="Active Users"
          value="1"
          change="+100%"
          icon={Users}
          color="pink"
        />
        <StatCard
          title="Monthly Growth"
          value="0%"
          change="+0%"
          icon={BarChart3}
          color="purple"
        />
        <StatCard
          title="Conversion Rate"
          value="0%"
          change="+0%"
          icon={BarChart3}
          color="cyan"
        />
      </div>

      {/* Welcome Card */}
      <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl p-8 shadow-2xl shadow-orange-500/10">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold text-white mb-2">Welcome to your Dashboard</h3>
            <p className="text-gray-300 text-lg">
              Start by adding contacts or inviting team members to get the most out of ClientIQ.
            </p>
          </div>
          <div className="hidden lg:block">
            <div className="w-32 h-32 bg-gradient-to-r from-orange-500/20 to-pink-500/20 rounded-full flex items-center justify-center border border-orange-500/30">
              <BarChart3 className="h-16 w-16 text-orange-400" />
            </div>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-4 mt-6">
          <button className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-6 py-3 rounded-lg font-semibold shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 transition-all duration-200">
            Add First Contact
          </button>
          <button className="bg-slate-700/50 border border-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-slate-600/50 transition-all duration-200">
            Invite Team Member
          </button>
        </div>
      </div>
    </div>
  );
};

const Analytics = () => {
  return (
    <div className="space-y-6">
      <h3 className="text-2xl font-bold text-white">Analytics</h3>
      
      <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl p-8 shadow-2xl shadow-orange-500/10">
        <div className="text-center py-12">
          <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Analytics Coming Soon</h3>
          <p className="text-gray-300 mb-6">We're working on powerful analytics to help you understand your data.</p>
        </div>
      </div>
    </div>
  );
};

const Settings = () => {
  return (
    <div className="space-y-6">
      <h3 className="text-2xl font-bold text-white">Settings</h3>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl p-6 shadow-2xl shadow-orange-500/10">
          <h4 className="text-lg font-semibold text-white mb-4">Account Settings</h4>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Organization Name
              </label>
              <input
                type="text"
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="Enter organization name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Website</label>
              <input
                type="url"
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="https://your-website.com"
              />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl p-6 shadow-2xl shadow-orange-500/10">
          <h4 className="text-lg font-semibold text-white mb-4">Preferences</h4>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-300">Email Notifications</span>
              <input type="checkbox" className="rounded" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-300">Marketing Emails</span>
              <input type="checkbox" className="rounded" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Stat Card Component
interface StatCardProps {
  title: string;
  value: string;
  change: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, icon: Icon, color }) => {
  const colorClasses = {
    orange: 'from-orange-500/20 to-orange-600/20 border-orange-500/30 text-orange-400',
    pink: 'from-pink-500/20 to-pink-600/20 border-pink-500/30 text-pink-400',
    purple: 'from-purple-500/20 to-purple-600/20 border-purple-500/30 text-purple-400',
    cyan: 'from-cyan-500/20 to-cyan-600/20 border-cyan-500/30 text-cyan-400',
  };

  return (
    <div className={`bg-gradient-to-r ${colorClasses[color as keyof typeof colorClasses]} backdrop-blur-xl border rounded-2xl p-6 shadow-2xl`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-300 text-sm font-medium">{title}</p>
          <p className="text-white text-3xl font-bold mt-2">{value}</p>
          <p className="text-green-400 text-sm font-medium mt-1">{change}</p>
        </div>
        <Icon className="h-8 w-8" />
      </div>
    </div>
  );
};

export default Dashboard;