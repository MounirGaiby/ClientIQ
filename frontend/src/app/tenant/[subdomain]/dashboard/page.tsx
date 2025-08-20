'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Layout } from '@/components/layout';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function TenantDashboardPage() {
  const router = useRouter();
  const params = useParams();
  const { user, logout } = useAuth();
  const subdomain = params.subdomain as string;
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      // User is not logged in, redirect to login
      router.replace(`/tenant/${subdomain}/login`);
    } else {
      setIsLoading(false);
    }
  }, [user, router, subdomain]);

  const handleLogout = () => {
    logout();
    router.push(`/tenant/${subdomain}/login`);
  };

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-lg">C</span>
          </div>
          <div className="text-gray-600">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <Layout 
      showSidebar={true} 
      user={{
        name: `${user.first_name} ${user.last_name}`,
        email: user.email,
        avatar: undefined
      }} 
      onLogout={handleLogout}
    >
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to {subdomain} tenant</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Users</CardTitle>
              <CardDescription>Manage your team members</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">0</div>
              <p className="text-sm text-gray-600">Total users</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Reports</CardTitle>
              <CardDescription>View your analytics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">0</div>
              <p className="text-sm text-gray-600">Reports generated</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Settings</CardTitle>
              <CardDescription>Configure your tenant</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{subdomain}</div>
              <p className="text-sm text-gray-600">Current tenant</p>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle>Welcome to ClientIQ</CardTitle>
              <CardDescription>Get started with your tenant dashboard</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">
                This is your tenant-specific dashboard for <strong>{subdomain}</strong>. 
                Use the navigation sidebar to access different features like user management, 
                reports, and settings.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
}
