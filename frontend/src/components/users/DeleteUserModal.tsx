'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { User, userApi } from '@/lib/api/users';
import { XMarkIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface DeleteUserModalProps {
  isOpen: boolean;
  user: User | null;
  onClose: () => void;
  onUserDeleted: () => void;
}

export default function DeleteUserModal({ isOpen, user, onClose, onUserDeleted }: DeleteUserModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleDelete = async () => {
    if (!user) return;

    try {
      setLoading(true);
      setError('');
      await userApi.deleteUser(user.id);
      onUserDeleted();
      onClose();
    } catch (error) {
      console.error('Failed to delete user:', error);
      setError('Failed to delete user. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="inline-block w-full max-w-md p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Delete User</h3>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <div className="mb-6">
            <p className="text-sm text-gray-500 mb-4">
              Are you sure you want to delete this user? This action cannot be undone.
            </p>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center">
                <div className="flex-shrink-0 h-10 w-10">
                  <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
                    {user.first_name.charAt(0)}{user.last_name.charAt(0)}
                  </div>
                </div>
                <div className="ml-3">
                  <div className="text-sm font-medium text-gray-900">
                    {user.first_name} {user.last_name}
                  </div>
                  <div className="text-sm text-gray-500">{user.email}</div>
                  <div className="text-sm text-gray-500">
                    {user.department && `${user.department} • `}
                    {user.job_title}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              onClick={handleDelete} 
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {loading ? 'Deleting...' : 'Delete User'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
