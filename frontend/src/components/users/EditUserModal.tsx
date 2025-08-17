'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { User, UpdateUserData, userApi } from '@/lib/api/users';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface EditUserModalProps {
  isOpen: boolean;
  user: User | null;
  onClose: () => void;
  onUserUpdated: () => void;
}

export default function EditUserModal({ isOpen, user, onClose, onUserUpdated }: EditUserModalProps) {
  const [formData, setFormData] = useState<UpdateUserData>({});
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Initialize form data when user changes
  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        user_type: user.user_type,
        phone_number: user.phone_number || '',
        department: user.department || '',
        job_title: user.job_title || '',
        is_active: user.is_active,
        is_tenant_admin: user.is_tenant_admin
      });
    }
  }, [user]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.first_name) {
      newErrors.first_name = 'First name is required';
    }

    if (!formData.last_name) {
      newErrors.last_name = 'Last name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!user || !validateForm()) {
      return;
    }

    try {
      setLoading(true);
      await userApi.updateUser(user.id, formData);
      onUserUpdated();
      onClose();
      setErrors({});
    } catch (error) {
      console.error('Failed to update user:', error);
      setErrors({ general: 'Failed to update user. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof UpdateUserData, value: string | boolean | undefined) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="inline-block w-full max-w-md p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Edit User</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {errors.general && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Basic Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
                  First Name *
                </label>
                <Input
                  id="first_name"
                  type="text"
                  value={formData.first_name || ''}
                  onChange={(e) => handleInputChange('first_name', e.target.value)}
                  className={errors.first_name ? 'border-red-500' : ''}
                />
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.first_name}</p>
                )}
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name *
                </label>
                <Input
                  id="last_name"
                  type="text"
                  value={formData.last_name || ''}
                  onChange={(e) => handleInputChange('last_name', e.target.value)}
                  className={errors.last_name ? 'border-red-500' : ''}
                />
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.last_name}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address *
              </label>
              <Input
                id="email"
                type="email"
                value={formData.email || ''}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className={errors.email ? 'border-red-500' : ''}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            {/* Role and Type */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="user_type" className="block text-sm font-medium text-gray-700 mb-1">
                  User Type
                </label>
                <select
                  id="user_type"
                  value={formData.user_type || 'user'}
                  onChange={(e) => handleInputChange('user_type', e.target.value as 'admin' | 'manager' | 'user')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="user">User</option>
                  <option value="manager">Manager</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div className="flex items-center space-x-4 pt-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_tenant_admin || false}
                    onChange={(e) => handleInputChange('is_tenant_admin', e.target.checked)}
                    className="rounded"
                  />
                  <span className="ml-2 text-sm">Tenant Admin</span>
                </label>
              </div>
            </div>

            {/* Additional Information */}
            <div>
              <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <Input
                id="phone_number"
                type="tel"
                value={formData.phone_number || ''}
                onChange={(e) => handleInputChange('phone_number', e.target.value)}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <Input
                  id="department"
                  type="text"
                  value={formData.department || ''}
                  onChange={(e) => handleInputChange('department', e.target.value)}
                />
              </div>

              <div>
                <label htmlFor="job_title" className="block text-sm font-medium text-gray-700 mb-1">
                  Job Title
                </label>
                <Input
                  id="job_title"
                  type="text"
                  value={formData.job_title || ''}
                  onChange={(e) => handleInputChange('job_title', e.target.value)}
                />
              </div>
            </div>

            {/* Status */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active || false}
                onChange={(e) => handleInputChange('is_active', e.target.checked)}
                className="rounded"
              />
              <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                Active User
              </label>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3 pt-4">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Updating...' : 'Update User'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
