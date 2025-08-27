// frontend/src/components/ActivityModal.tsx
import React, { useState, useEffect } from 'react';
import {
  X,
  Save,
  Calendar,
  Clock,
  User,
  Building,
  Target,
  Bell,
  Phone,
  Mail,
  Users,
  FileText,
  CheckSquare,
  AlertCircle
} from 'lucide-react';
import { activitiesApi, Activity, ActivityType, ActivityFormData } from '../api/activities';
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

interface ActivityModalProps {
  activity?: Activity | null;
  isOpen: boolean;
  isCreating: boolean;
  activityTypes: ActivityType[];
  contacts: Contact[];
  companies: Company[];
  opportunities: Opportunity[];
  users: User[];
  onClose: () => void;
  onSave: () => void;
}

const ActivityModal: React.FC<ActivityModalProps> = ({
  activity,
  isOpen,
  isCreating,
  activityTypes,
  contacts,
  companies,
  opportunities,
  users,
  onClose,
  onSave
}) => {
  const { user } = useAuth();
  
  const [formData, setFormData] = useState<ActivityFormData>({
    title: '',
    description: '',
    activity_type_id: 0,
    priority: 'medium',
    scheduled_at: '',
    duration_minutes: undefined,
    reminder_minutes_before: undefined,
    contact_id: undefined,
    company_id: undefined,
    opportunity_id: undefined,
    assigned_to_id: user?.id || 0,
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      if (activity && !isCreating) {
        // Edit mode - populate form with activity data
        const scheduledDate = new Date(activity.scheduled_at);
        const formattedDateTime = scheduledDate.toISOString().slice(0, 16); // Format for datetime-local input

        setFormData({
          title: activity.title,
          description: activity.description,
          activity_type_id: activity.activity_type.id,
          priority: activity.priority,
          scheduled_at: formattedDateTime,
          duration_minutes: activity.duration_minutes,
          reminder_minutes_before: activity.reminder_minutes_before,
          contact_id: activity.contact?.id,
          company_id: activity.company?.id,
          opportunity_id: activity.opportunity?.id,
          assigned_to_id: activity.assigned_to.id,
        });
      } else {
        // Create mode - reset to defaults
        const now = new Date();
        const defaultDateTime = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour from now
        
        setFormData({
          title: '',
          description: '',
          activity_type_id: activityTypes.length > 0 ? activityTypes[0].id : 0,
          priority: 'medium',
          scheduled_at: defaultDateTime.toISOString().slice(0, 16),
          duration_minutes: 30,
          reminder_minutes_before: 15,
          contact_id: undefined,
          company_id: undefined,
          opportunity_id: undefined,
          assigned_to_id: user?.id || 0,
        });
      }
      setErrors({});
    }
  }, [isOpen, activity, isCreating, activityTypes, user]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? undefined : 
              (name.includes('_id') || name.includes('minutes')) ? parseInt(value) || undefined : 
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

    if (!formData.activity_type_id) {
      newErrors.activity_type_id = 'Activity type is required';
    }

    if (!formData.scheduled_at) {
      newErrors.scheduled_at = 'Scheduled date and time is required';
    } else {
      const scheduledDate = new Date(formData.scheduled_at);
      const now = new Date();
      if (scheduledDate < now && isCreating) {
        newErrors.scheduled_at = 'Scheduled time cannot be in the past';
      }
    }

    if (!formData.assigned_to_id) {
      newErrors.assigned_to_id = 'Assigned user is required';
    }

    // Check if selected activity type requires duration
    const selectedActivityType = activityTypes.find(t => t.id === formData.activity_type_id);
    if (selectedActivityType?.requires_duration && !formData.duration_minutes) {
      newErrors.duration_minutes = 'Duration is required for this activity type';
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
        await activitiesApi.createActivity(formData);
      } else if (activity) {
        await activitiesApi.updateActivity(activity.id, formData);
      }
      onSave();
      onClose();
    } catch (err: any) {
      console.error('Error saving activity:', err);
      setErrors({ submit: err.message || 'Failed to save activity' });
    } finally {
      setLoading(false);
    }
  };

  const getActivityTypeIcon = (typeName: string) => {
    switch (typeName?.toLowerCase()) {
      case 'call': return Phone;
      case 'email': return Mail;
      case 'meeting': return Users;
      case 'task': return CheckSquare;
      case 'note': return FileText;
      default: return Calendar;
    }
  };

  if (!isOpen) return null;

  const selectedActivityType = activityTypes.find(t => t.id === formData.activity_type_id);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-orange-500/20 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700/50">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-orange-500/20 rounded-lg">
              <Calendar className="h-6 w-6 text-orange-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">
                {isCreating ? 'Create Activity' : 'Edit Activity'}
              </h2>
              <p className="text-gray-400 text-sm">
                {isCreating ? 'Schedule a new activity or meeting' : 'Update activity details'}
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
            <h3 className="text-lg font-semibold text-white">Basic Information</h3>
            
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Calendar className="h-4 w-4 inline mr-1" />
                Activity Title *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="Enter activity title"
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
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="Enter activity description"
              />
            </div>

            {/* Activity Type and Priority */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Activity Type *
                </label>
                <select
                  name="activity_type_id"
                  value={formData.activity_type_id}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="">Select activity type</option>
                  {activityTypes.map(type => {
                    const Icon = getActivityTypeIcon(type.name);
                    return (
                      <option key={type.id} value={type.id}>
                        {type.name} - {type.description}
                      </option>
                    );
                  })}
                </select>
                {errors.activity_type_id && (
                  <p className="mt-1 text-sm text-red-400">{errors.activity_type_id}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Priority
                </label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="low">Low Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="high">High Priority</option>
                </select>
              </div>
            </div>
          </div>

          {/* Scheduling */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Scheduling</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Scheduled Date & Time */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Clock className="h-4 w-4 inline mr-1" />
                  Scheduled At *
                </label>
                <input
                  type="datetime-local"
                  name="scheduled_at"
                  value={formData.scheduled_at}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
                {errors.scheduled_at && (
                  <p className="mt-1 text-sm text-red-400">{errors.scheduled_at}</p>
                )}
              </div>

              {/* Duration */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Duration (minutes) {selectedActivityType?.requires_duration && '*'}
                </label>
                <input
                  type="number"
                  name="duration_minutes"
                  value={formData.duration_minutes || ''}
                  onChange={handleInputChange}
                  min="1"
                  step="1"
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="30"
                />
                {errors.duration_minutes && (
                  <p className="mt-1 text-sm text-red-400">{errors.duration_minutes}</p>
                )}
              </div>

              {/* Reminder */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Bell className="h-4 w-4 inline mr-1" />
                  Reminder (minutes before)
                </label>
                <select
                  name="reminder_minutes_before"
                  value={formData.reminder_minutes_before || ''}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="">No reminder</option>
                  <option value="5">5 minutes</option>
                  <option value="15">15 minutes</option>
                  <option value="30">30 minutes</option>
                  <option value="60">1 hour</option>
                  <option value="120">2 hours</option>
                  <option value="1440">1 day</option>
                </select>
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
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
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
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
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
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
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
                  className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
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

          {/* Activity Type Info */}
          {selectedActivityType && (
            <div className="bg-slate-700/30 rounded-lg p-4 border border-gray-600">
              <div className="flex items-center space-x-3">
                <div 
                  className="p-2 rounded-lg"
                  style={{ backgroundColor: `${selectedActivityType.color}20` }}
                >
                  {React.createElement(getActivityTypeIcon(selectedActivityType.name), {
                    className: "h-4 w-4",
                    style: { color: selectedActivityType.color }
                  })}
                </div>
                <div>
                  <h4 className="text-white font-medium">{selectedActivityType.name}</h4>
                  <p className="text-gray-400 text-sm">{selectedActivityType.description}</p>
                </div>
              </div>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                {selectedActivityType.requires_duration && (
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded">
                    Duration Required
                  </span>
                )}
                {selectedActivityType.requires_outcome && (
                  <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded">
                    Outcome Required
                  </span>
                )}
              </div>
            </div>
          )}

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
              className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-6 py-2 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Save className="h-4 w-4" />
              )}
              <span>{loading ? 'Saving...' : (isCreating ? 'Create Activity' : 'Update Activity')}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ActivityModal;