'use client';

import { useState, useEffect, useCallback } from 'react';
import { Layout } from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { userApi, User, UserListParams } from '@/lib/api/users';
import CreateUserModal from '@/components/users/CreateUserModal';
import EditUserModal from '@/components/users/EditUserModal';
import DeleteUserModal from '@/components/users/DeleteUserModal';
import { 
  MagnifyingGlassIcon, 
  PlusIcon, 
  PencilIcon, 
  TrashIcon
} from '@heroicons/react/24/outline';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<UserListParams>({});
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const params: UserListParams = {
        ...filters,
        search: searchTerm || undefined
      };
      const response = await userApi.getUsers(params);
      setUsers(response.results);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, filters]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleSelectUser = (userId: string) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSelectAll = () => {
    setSelectedUsers(
      selectedUsers.length === users.length ? [] : users.map(u => u.id)
    );
  };

  const getUserTypeColor = (userType: string) => {
    switch (userType) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'manager': return 'bg-blue-100 text-blue-800';
      case 'user': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setShowEditModal(true);
  };

  const handleDeleteUser = (user: User) => {
    setSelectedUser(user);
    setShowDeleteModal(true);
  };

  const handleBulkDelete = async () => {
    try {
      await userApi.bulkDeleteUsers(selectedUsers);
      setSelectedUsers([]);
      loadUsers();
    } catch (error) {
      console.error('Failed to delete users:', error);
    }
  };

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage users and their permissions within your organization</p>
        </div>

        {/* Actions Bar */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex flex-1 gap-4 items-center">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Filters */}
            <div className="flex gap-2">
              <select
                value={filters.user_type || ''}
                onChange={(e) => setFilters(prev => ({
                  ...prev,
                  user_type: e.target.value || undefined
                }))}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="">All Types</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="user">User</option>
              </select>

              <select
                value={filters.is_active === undefined ? '' : filters.is_active.toString()}
                onChange={(e) => setFilters(prev => ({
                  ...prev,
                  is_active: e.target.value === '' ? undefined : e.target.value === 'true'
                }))}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="">All Status</option>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            {selectedUsers.length > 0 && (
              <Button variant="outline" size="sm" onClick={handleBulkDelete}>
                <TrashIcon className="h-4 w-4 mr-2" />
                Delete ({selectedUsers.length})
              </Button>
            )}
            <Button size="sm" onClick={() => setShowCreateModal(true)}>
              <PlusIcon className="h-4 w-4 mr-2" />
              Add User
            </Button>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg border">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading users...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedUsers.length === users.length && users.length > 0}
                        onChange={handleSelectAll}
                        className="rounded"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Department
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Login
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <input
                          type="checkbox"
                          checked={selectedUsers.includes(user.id)}
                          onChange={() => handleSelectUser(user.id)}
                          className="rounded"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
                              {user.first_name.charAt(0)}{user.last_name.charAt(0)}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {user.first_name} {user.last_name}
                            </div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getUserTypeColor(user.user_type)}`}>
                          {user.user_type}
                          {user.is_tenant_admin && (
                            <span className="ml-1 text-xs">👑</span>
                          )}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>
                          <div className="font-medium">{user.department || '-'}</div>
                          <div className="text-gray-500">{user.job_title || '-'}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(user.last_login)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          user.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <Button variant="outline" size="sm" onClick={() => handleEditUser(user)}>
                            <PencilIcon className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => handleDeleteUser(user)}>
                            <TrashIcon className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {users.length === 0 && (
                <div className="p-8 text-center">
                  <p className="text-gray-500">No users found</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Pagination */}
        {users.length > 0 && (
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {users.length} users
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled>
                Previous
              </Button>
              <Button variant="outline" size="sm" disabled>
                Next
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Create User Modal */}
      <CreateUserModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onUserCreated={loadUsers}
      />

      {/* Edit User Modal */}
      <EditUserModal
        isOpen={showEditModal}
        user={selectedUser}
        onClose={() => setShowEditModal(false)}
        onUserUpdated={loadUsers}
      />

      {/* Delete User Modal */}
      <DeleteUserModal
        isOpen={showDeleteModal}
        user={selectedUser}
        onClose={() => setShowDeleteModal(false)}
        onUserDeleted={loadUsers}
      />
    </Layout>
  );
}
