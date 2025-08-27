// frontend/src/components/TaskModal.tsx
import React, { useState, useEffect } from 'react';
import {
  X,
  Save,
  CheckSquare,
  Calendar,
  User,
  Building,
  Target,
  AlertCircle,
  Flag
} from 'lucide-react';
import { activitiesApi, Task, TaskFormData } from '../api/activities';
import { useAuth } from '../contexts/AuthContext';

interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  full_name?: string;
}

interface Company {
  id: number;
  name: string;
}

interface Opportunity {
  id: number;
  name: string;
}

interface User {
  id: number;
  first_name: string;
  last_name: string;
  full_name?: string;
}

interface TaskModalProps {
  task?: Task | null;
  isOpen: boolean;
  isCreating: boolean;
  contacts: Contact[];
  companies: Company[];
  opportunities: Opportunity[];
  users: User[];
  onClose: () => void;
  onSave: () => void;
}

const TaskModal: React.FC<TaskModalProps> = ({
  task,
  isOpen,
  isCreating,
  contacts,
  companies,
  opportunities,
  users,
  onClose,
  onSave
}) => {
  const { user } = useAuth();
  
  const [formData, setFormData] = useState<TaskFormData>({
    title: '',
    description: '',
    priority: 'medium',
    due_date: '',
    assigned_to_id: user?.id || 0,
    contact_id: undefined,
    company_id: undefined,
    opportunity_id: undefined,
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      if (task && !isCreating) {
        // Edit mode - populate form with task data
        const dueDate = task.due_date ? new Date(task.due_date).toISOString().slice(0, 10) : '';

        setFormData({
          title: task.title,
          description: task.description || '',
          priority: task.priority,
          due_date: dueDate,
          assigned_to_id: task.assigned_to.id,
          contact_id: task.contact?.id,
          company_id: task.company?.id,
          opportunity_id: task.opportunity?.id,
        });
      } else {
        // Create mode - reset to defaults
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        setFormData({
          title: '',
          description: '',
          priority: 'medium',
          due_date: tomorrow.toISOString().slice(0, 10),
          assigned_to_id: user?.id || 0,
          contact_id: undefined,
          company_id: undefined,
          opportunity_id: undefined,
        });
      }
      setErrors({});
    }
  }, [isOpen, task, isCreating, user]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? undefined : 
              name.includes('_id') ? parseInt(value) || undefined : 
              value
    }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.assigned_to_id) {
      newErrors.assigned_to_id = 'Assigned user is required';
    }

    if (formData.due_date) {
      const dueDate = new Date(formData.due_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (dueDate < today && isCreating) {
        newErrors.due_date = 'Due date cannot be in the past';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      if (isCreating) {
        await activitiesApi.createTask(formData);
      } else if (task) {
        await activitiesApi.updateTask(task.id, formData);
      }
      onSave();
      onClose();
    } catch (err: any) {
      console.error('Error saving task:', err);
      setErrors({ submit: err.message || 'Failed to save task' });
    } finally {
      setLoading(false);
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'from-red-500/20 to-pink-500/20 border-red-500/30';
      case 'medium': return 'from-yellow-500/20 to-orange-500/20 border-yellow-500/30';
      case 'low': return 'from-green-500/20 to-emerald-500/20 border-green-500/30';
      default: return 'from-gray-500/20 to-slate-500/20 border-gray-500/30';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-orange-500/20 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700/50">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <CheckSquare className="h-6 w-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">
                {isCreating ? 'Create Task' : 'Edit Task'}
              </h2>
              <p className="text-gray-400 text-sm">
                {isCreating ? 'Create a new task or to-do item' : 'Update task details'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {errors.submit && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-center space-x-3">
              <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
              <p className="text-red-400">{errors.submit}</p>
            </div>
          )}

          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Task Details</h3>
            
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <CheckSquare className="h-4 w-4 inline mr-1" />
                Task Title *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter task title"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-400">{errors.title}</p>
              )}
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description || ''}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter task description (optional)"
              />
            </div>

            {/* Priority and Due Date */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Flag className="h-4 w-4 inline mr-1" />
                  Priority
                </label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">🟢 Low Priority</option>
                  <option value="medium">🟡 Medium Priority</option>
                  <option value="high">🔴 High Priority</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Calendar className="h-4 w-4 inline mr-1" />
                  Due Date
                </label>
                <input
                  type="date"
                  name="due_date"
                  value={formData.due_date || ''}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.due_date && (
                  <p className="mt-1 text-sm text-red-400">{errors.due_date}</p>
                )}
              </div>
            </div>
          </div>

          {/* Assignment & Relations */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Assignment & Relations</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Assigned To */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <User className="h-4 w-4 inline mr-1" />
                  Assigned To *
                </label>
                <select
                  name="assigned_to_id"
                  value={formData.assigned_to_id}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select assignee</option>
                  {users.map(u => (
                    <option key={u.id} value={u.id}>
                      {u.first_name} {u.last_name}
                    </option>
                  ))}
                </select>
                {errors.assigned_to_id && (
                  <p className="mt-1 text-sm text-red-400">{errors.assigned_to_id}</p>
                )}
              </div>

              {/* Contact */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <User className="h-4 w-4 inline mr-1" />
                  Related Contact
                </label>
                <select
                  name="contact_id"
                  value={formData.contact_id || ''}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select contact</option>
                  {contacts.map(contact => (
                    <option key={contact.id} value={contact.id}>
                      {contact.full_name || `${contact.first_name} ${contact.last_name}`}
                    </option>
                  ))}
                </select>
              </div>

              {/* Company */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Building className="h-4 w-4 inline mr-1" />
                  Related Company
                </label>
                <select
                  name="company_id"
                  value={formData.company_id || ''}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select company</option>
                  {companies.map(company => (
                    <option key={company.id} value={company.id}>
                      {company.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Opportunity */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Target className="h-4 w-4 inline mr-1" />
                  Related Opportunity
                </label>
                <select
                  name="opportunity_id"
                  value={formData.opportunity_id || ''}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select opportunity</option>
                  {opportunities.map(opp => (
                    <option key={opp.id} value={opp.id}>
                      {opp.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Priority Preview */}
          <div className={`bg-gradient-to-r ${getPriorityColor(formData.priority)} rounded-lg p-4 border`}>
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{getPriorityIcon(formData.priority)}</div>
              <div>
                <h4 className="text-white font-medium capitalize">{formData.priority} Priority Task</h4>
                <p className="text-gray-400 text-sm">
                  {formData.priority === 'high' && 'This task requires immediate attention'}
                  {formData.priority === 'medium' && 'This task should be completed in a timely manner'}
                  {formData.priority === 'low' && 'This task can be completed when time permits'}
                </p>
              </div>
            </div>
            {formData.due_date && (
              <div className="mt-3 text-sm text-gray-300">
                <Calendar className="h-4 w-4 inline mr-1" />
                Due: {new Date(formData.due_date).toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-2 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Save className="h-4 w-4" />
              )}
              <span>{loading ? 'Saving...' : (isCreating ? 'Create Task' : 'Update Task')}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskModal;