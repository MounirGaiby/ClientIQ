'use client';

import { useState } from 'react';
import { Layout } from '@/components/layout';
import { Button } from '@/components/ui/button';
import { 
  UserGroupIcon, 
  PlusIcon, 
  PencilIcon, 
  TrashIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

interface Role {
  id: string;
  name: string;
  display_name: string;
  description: string;
  permissions: string[];
  user_count: number;
  is_system_role: boolean;
}

export default function RolesPage() {
  // Mock data - TODO: Replace with actual API calls when backend is ready
  const [roles] = useState<Role[]>([
    {
      id: '1',
      name: 'admin',
      display_name: 'Administrator',
      description: 'Full system access with all permissions',
      permissions: ['view_dashboard', 'manage_users', 'manage_tenants', 'view_analytics', 'manage_settings'],
      user_count: 2,
      is_system_role: true
    },
    {
      id: '2',
      name: 'manager',
      display_name: 'Manager',
      description: 'Manage users and view analytics',
      permissions: ['view_dashboard', 'manage_users', 'view_analytics'],
      user_count: 5,
      is_system_role: false
    },
    {
      id: '3',
      name: 'user',
      display_name: 'User',
      description: 'Basic user access',
      permissions: ['view_dashboard'],
      user_count: 15,
      is_system_role: false
    }
  ]);

  const [loading] = useState(false);

  const getPermissionColor = (permission: string) => {
    const colors: Record<string, string> = {
      'view_dashboard': 'bg-blue-100 text-blue-800',
      'manage_users': 'bg-green-100 text-green-800',
      'manage_tenants': 'bg-purple-100 text-purple-800',
      'view_analytics': 'bg-yellow-100 text-yellow-800',
      'manage_settings': 'bg-red-100 text-red-800'
    };
    return colors[permission] || 'bg-gray-100 text-gray-800';
  };

  const handleCreateRole = () => {
    // TODO: Implement role creation when backend is ready
    console.log('TODO: Implement role creation');
  };

  const handleEditRole = (role: Role) => {
    // TODO: Implement role editing when backend is ready
    console.log('TODO: Implement role editing for:', role.name);
  };

  const handleDeleteRole = (role: Role) => {
    // TODO: Implement role deletion when backend is ready
    console.log('TODO: Implement role deletion for:', role.name);
  };

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center mb-2">
            <UserGroupIcon className="h-8 w-8 text-blue-600 mr-3" />
            <h1 className="text-2xl font-bold text-gray-900">Role Management</h1>
          </div>
          <p className="text-gray-600">
            Manage user roles and permissions within your organization
          </p>
        </div>

        {/* Actions Bar */}
        <div className="mb-6 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {roles.length} roles configured
          </div>
          <Button onClick={handleCreateRole}>
            <PlusIcon className="h-4 w-4 mr-2" />
            Create Role
          </Button>
        </div>

        {/* Roles Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {roles.map((role) => (
              <div key={role.id} className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                      role.is_system_role ? 'bg-blue-600' : 'bg-green-600'
                    }`}>
                      <ShieldCheckIcon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-lg font-medium text-gray-900">
                        {role.display_name}
                        {role.is_system_role && (
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            System
                          </span>
                        )}
                      </h3>
                      <p className="text-sm text-gray-500">{role.name}</p>
                    </div>
                  </div>
                  
                  {!role.is_system_role && (
                    <div className="flex gap-1">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEditRole(role)}
                      >
                        <PencilIcon className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteRole(role)}
                      >
                        <TrashIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>

                <p className="text-sm text-gray-600 mb-4">{role.description}</p>

                {/* Permissions */}
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Permissions</h4>
                  <div className="flex flex-wrap gap-1">
                    {role.permissions.map((permission) => (
                      <span
                        key={permission}
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getPermissionColor(permission)}`}
                      >
                        {permission.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>

                {/* User Count */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <span className="text-sm text-gray-500">Users</span>
                  <span className="text-sm font-medium text-gray-900">
                    {role.user_count} {role.user_count === 1 ? 'user' : 'users'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info Banner */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <ShieldCheckIcon className="h-5 w-5 text-blue-400 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-blue-800">Role Management</h3>
              <div className="mt-1 text-sm text-blue-700">
                <p>
                  Roles define what actions users can perform in the system. System roles (Admin, Manager, User) 
                  are built-in and cannot be deleted, but you can create custom roles with specific permission sets.
                </p>
                <p className="mt-2">
                  <strong>Note:</strong> Role management features are currently in development. 
                  Backend API endpoints are not yet implemented.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
