'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Layout } from '@/components/layout';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  job_title: string;
  phone_number: string;
  is_active: boolean;
  is_admin: boolean;
  date_joined: string;
}

interface UserFormData {
  email: string;
  first_name: string;
  last_name: string;
  job_title: string;
  phone_number: string;
  password?: string;
  is_admin: boolean;
}

export default function UsersPage() {
  const router = useRouter();
  const params = useParams();
  const { user, token, logout } = useAuth();
  const subdomain = params.subdomain as string;
  
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<UserFormData>({
    email: '',
    first_name: '',
    last_name: '',
    job_title: '',
    phone_number: '',
    password: '',
    is_admin: false,
  });

  const makeApiRequest = useCallback(async (url: string, options: RequestInit = {}) => {
    if (!token) throw new Error('No authentication token');
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return fetch(`${apiUrl}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Host': `${subdomain}.localhost`,
        ...options.headers,
      },
    });
  }, [token, subdomain]);

  const fetchUsers = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await makeApiRequest('/api/v1/users/');
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else if (response.status === 401) {
        logout();
        router.push(`/tenant/${subdomain}/login`);
      } else {
        setError('Failed to load users');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Failed to load users');
    } finally {
      setIsLoading(false);
    }
  }, [makeApiRequest, logout, router, subdomain]);

  useEffect(() => {
    if (!user) {
      router.replace(`/tenant/${subdomain}/login`);
    } else {
      fetchUsers();
    }
  }, [user, router, subdomain, fetchUsers]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError('');
      const response = await makeApiRequest('/api/v1/users/', {
        method: 'POST',
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowForm(false);
        setFormData({
          email: '',
          first_name: '',
          last_name: '',
          job_title: '',
          phone_number: '',
          password: '',
          is_admin: false,
        });
        fetchUsers();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create user');
      }
    } catch (error) {
      console.error('Error creating user:', error);
      setError('Failed to create user');
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;

    try {
      setError('');
      const updateData = { ...formData };
      // Don't send password if it's empty
      if (!updateData.password) {
        delete updateData.password;
      }

      const response = await makeApiRequest(`/api/v1/users/${editingUser.id}/`, {
        method: 'PUT',
        body: JSON.stringify(updateData),
      });

      if (response.ok) {
        setShowForm(false);
        setEditingUser(null);
        setFormData({
          email: '',
          first_name: '',
          last_name: '',
          job_title: '',
          phone_number: '',
          password: '',
          is_admin: false,
        });
        fetchUsers();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update user');
      }
    } catch (error) {
      console.error('Error updating user:', error);
      setError('Failed to update user');
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;

    try {
      setError('');
      const response = await makeApiRequest(`/api/v1/users/${userId}/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchUsers();
      } else {
        setError('Failed to delete user');
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      setError('Failed to delete user');
    }
  };

  const startEditing = (user: User) => {
    setEditingUser(user);
    setFormData({
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      job_title: user.job_title,
      phone_number: user.phone_number,
      password: '',
      is_admin: user.is_admin,
    });
    setShowForm(true);
  };

  const cancelForm = () => {
    setShowForm(false);
    setEditingUser(null);
    setFormData({
      email: '',
      first_name: '',
      last_name: '',
      job_title: '',
      phone_number: '',
      password: '',
      is_admin: false,
    });
  };

  if (!user) {
    return null;
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Users</h1>
            <p className="text-muted-foreground">
              Manage users and their permissions for your organization
            </p>
          </div>
          <Button onClick={() => setShowForm(true)} className="flex items-center gap-2">
            <PlusIcon className="w-4 h-4" />
            Add User
          </Button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {showForm && (
          <Card>
            <CardHeader>
              <CardTitle>
                {editingUser ? 'Edit User' : 'Create New User'}
              </CardTitle>
              <CardDescription>
                {editingUser 
                  ? 'Update user information and permissions' 
                  : 'Add a new user to your organization'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={editingUser ? handleUpdateUser : handleCreateUser} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="first_name">First Name</Label>
                    <Input
                      id="first_name"
                      type="text"
                      value={formData.first_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, first_name: e.target.value }))}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="last_name">Last Name</Label>
                    <Input
                      id="last_name"
                      type="text"
                      value={formData.last_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="job_title">Job Title</Label>
                    <Input
                      id="job_title"
                      type="text"
                      value={formData.job_title}
                      onChange={(e) => setFormData(prev => ({ ...prev, job_title: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone_number">Phone Number</Label>
                    <Input
                      id="phone_number"
                      type="text"
                      value={formData.phone_number}
                      onChange={(e) => setFormData(prev => ({ ...prev, phone_number: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="password">
                    {editingUser ? 'New Password (leave blank to keep current)' : 'Password'}
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                    required={!editingUser}
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    id="is_admin"
                    type="checkbox"
                    checked={formData.is_admin}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_admin: e.target.checked }))}
                    className="rounded"
                  />
                  <Label htmlFor="is_admin">Administrator privileges</Label>
                </div>

                <div className="flex gap-2">
                  <Button type="submit">
                    {editingUser ? 'Update User' : 'Create User'}
                  </Button>
                  <Button type="button" variant="outline" onClick={cancelForm}>
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {isLoading ? (
          <div className="flex justify-center py-8">
            <div className="text-muted-foreground">Loading users...</div>
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Users ({users.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map((userItem) => (
                  <div
                    key={userItem.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium">
                          {userItem.first_name} {userItem.last_name}
                        </h3>
                        {userItem.is_admin && (
                          <Badge variant="secondary">Admin</Badge>
                        )}
                        {!userItem.is_active && (
                          <Badge variant="destructive">Inactive</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{userItem.email}</p>
                      {userItem.job_title && (
                        <p className="text-sm text-muted-foreground">{userItem.job_title}</p>
                      )}
                      {userItem.phone_number && (
                        <p className="text-sm text-muted-foreground">{userItem.phone_number}</p>
                      )}
                      <p className="text-xs text-muted-foreground">
                        Joined {new Date(userItem.date_joined).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => startEditing(userItem)}
                        className="flex items-center gap-1"
                      >
                        <PencilIcon className="w-4 h-4" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteUser(userItem.id)}
                        className="flex items-center gap-1 text-red-600 hover:text-red-700"
                      >
                        <TrashIcon className="w-4 h-4" />
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
                {users.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No users found. Create your first user to get started.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
}
