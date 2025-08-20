'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  is_admin: boolean;
  department: string;
  job_title: string;
  date_joined: string;
}

interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  company_name?: string;
  created_at: string;
}

export default function DashboardPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [subdomain, setSubdomain] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  
  const { user, logout, token, makeApiRequest } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Extract subdomain from hostname
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      const parts = hostname.split('.');
      if (parts.length > 1 && parts[0] !== 'www' && parts[0] !== 'localhost') {
        setSubdomain(parts[0]);
      } else if (hostname.includes('localhost') && parts.length > 1) {
        setSubdomain(parts[0]);
      }
    }
  }, []);

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    
    const fetchData = async () => {
      if (!token) return;
      
      try {
        // Fetch users
        const usersResponse = await makeApiRequest('/api/v1/users/');
        if (usersResponse.ok) {
          const usersData = await usersResponse.json();
          setUsers(usersData.results || usersData);
        }

        // Fetch contacts
        const contactsResponse = await makeApiRequest('/api/v1/contacts/');
        if (contactsResponse.ok) {
          const contactsData = await contactsResponse.json();
          setContacts(contactsData.results || contactsData);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Error fetching data');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [user, router, token, makeApiRequest]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <div>
                <span className="text-xl font-semibold text-gray-900">ClientIQ</span>
                {subdomain && <span className="ml-2 text-sm text-gray-500">({subdomain})</span>}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user.first_name || user.email}
              </span>
              <Button 
                variant="outline" 
                onClick={handleLogout}
                className="text-sm"
              >
                Sign out
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="mt-2 text-gray-600">
              Welcome to your {subdomain ? `${subdomain} ` : ''}tenant dashboard
            </p>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="users">Users</TabsTrigger>
              <TabsTrigger value="contacts">Contacts</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Overview Cards */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{users.length}</div>
                    <p className="text-xs text-muted-foreground">
                      Active tenant users
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium">Total Contacts</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{contacts.length}</div>
                    <p className="text-xs text-muted-foreground">
                      Contact records
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium">Admin Users</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {users.filter(u => u.is_admin).length}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Users with admin privileges
                    </p>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="users" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Users</CardTitle>
                  <CardDescription>
                    Manage users in your organization
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="text-center py-4">Loading users...</div>
                  ) : error ? (
                    <div className="text-red-600 text-center py-4">{error}</div>
                  ) : users.length === 0 ? (
                    <div className="text-gray-500 text-center py-4">No users found</div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full table-auto">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left py-2 px-4">Email</th>
                            <th className="text-left py-2 px-4">Name</th>
                            <th className="text-left py-2 px-4">Department</th>
                            <th className="text-left py-2 px-4">Role</th>
                            <th className="text-left py-2 px-4">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {users.map((user) => (
                            <tr key={user.id} className="border-b hover:bg-gray-50">
                              <td className="py-2 px-4">{user.email}</td>
                              <td className="py-2 px-4">
                                {user.full_name || '-'}
                              </td>
                              <td className="py-2 px-4">{user.department || '-'}</td>
                              <td className="py-2 px-4">
                                <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                                  user.is_admin 
                                    ? 'bg-purple-100 text-purple-800' 
                                    : 'bg-gray-100 text-gray-800'
                                }`}>
                                  {user.is_admin ? 'Admin' : 'User'}
                                </span>
                              </td>
                              <td className="py-2 px-4">
                                <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                                  user.is_active 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {user.is_active ? 'Active' : 'Inactive'}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="contacts" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Contacts</CardTitle>
                  <CardDescription>
                    Manage your contact database
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="text-center py-4">Loading contacts...</div>
                  ) : error ? (
                    <div className="text-red-600 text-center py-4">{error}</div>
                  ) : contacts.length === 0 ? (
                    <div className="text-gray-500 text-center py-8">
                      <p className="mb-4">No contacts found</p>
                      <Button variant="outline">Add Your First Contact</Button>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full table-auto">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left py-2 px-4">Name</th>
                            <th className="text-left py-2 px-4">Email</th>
                            <th className="text-left py-2 px-4">Phone</th>
                            <th className="text-left py-2 px-4">Company</th>
                            <th className="text-left py-2 px-4">Created</th>
                          </tr>
                        </thead>
                        <tbody>
                          {contacts.map((contact) => (
                            <tr key={contact.id} className="border-b hover:bg-gray-50">
                              <td className="py-2 px-4">
                                {`${contact.first_name} ${contact.last_name}`.trim()}
                              </td>
                              <td className="py-2 px-4">{contact.email}</td>
                              <td className="py-2 px-4">{contact.phone || '-'}</td>
                              <td className="py-2 px-4">{contact.company_name || '-'}</td>
                              <td className="py-2 px-4">
                                {new Date(contact.created_at).toLocaleDateString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
