// frontend/src/components/OpportunityModal.tsx
import React, { useState, useEffect } from 'react';
import { X, Save, Trash2, Calendar, DollarSign, User, Building } from 'lucide-react';
import { pipelineApi } from '../api/pipeline';
import { contactsApi } from '../api/contacts';
import { useAuth } from '../contexts/AuthContext';

interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  company?: {
    id: number;
    name: string;
  };
}

interface User {
  id: number
  email: string
  first_name: string
  last_name: string
}

interface Company {
  id: number;
  name: string;
}

interface SalesStage {
  id: number;
  name: string;
  probability: number;
  color: string;
}

interface OpportunityFormData {
  name: string;
  description: string;
  value: number;
  probability: number;
  stage_id: number;
  contact_id: number;
  company_id?: number;
  owner_id: number;
  expected_close_date: string;
  priority: 'low' | 'medium' | 'high';
}

interface OpportunityModalProps {
  opportunity?: any;
  isOpen: boolean;
  isCreating: boolean;
  onClose: () => void;
  onSave: () => void;
}

const OpportunityModal: React.FC<OpportunityModalProps> = ({
  opportunity,
  isOpen,
  isCreating,
  onClose,
  onSave
}) => {
  const { user } = useAuth();
  
  const [formData, setFormData] = useState<OpportunityFormData>({
    name: '',
    description: '',
    value: 0,
    probability: 50,
    stage_id: 1,
    contact_id: 0,
    company_id: undefined,
    owner_id: user?.id || 0,
    expected_close_date: '',
    priority: 'medium'
  });

  const [contacts, setContacts] = useState<Contact[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [stages, setStages] = useState<SalesStage[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen) {
      fetchData();
      if (opportunity && !isCreating) {
        setFormData({
          name: opportunity.name,
          description: opportunity.description,
          value: opportunity.value,
          probability: opportunity.probability,
          stage_id: opportunity.stage.id,
          contact_id: opportunity.contact.id,
          company_id: opportunity.company?.id,
          owner_id: opportunity.owner?.id || user?.id || 0,
          expected_close_date: opportunity.expected_close_date,
          priority: opportunity.priority
        });
      } else {
        // Reset form for new opportunity
        setFormData({
          name: '',
          description: '',
          value: 0,
          probability: 50,
          stage_id: stages[0]?.id || 1,
          contact_id: 0,
          company_id: undefined,
          owner_id: user?.id || 0,
          expected_close_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days from now
          priority: 'medium'
        });
      }
    }
  }, [isOpen, opportunity, isCreating]);

  const fetchData = async () => {
    try {
      const [contactsData, companiesData, stagesData] = await Promise.all([
        contactsApi.getContacts(),
        contactsApi.getCompanies(),
        pipelineApi.getStages(),
        // TODO: Add API call to get users for owner selection
        // For now, include current user in the list
      ]);
      
      setContacts(contactsData.results || contactsData);
      setCompanies(companiesData.results || companiesData);
      setStages(stagesData);

      // ADDED: Set users list (for now just current user, but you should fetch all users)
      if (user) {
        setUsers([user]);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'value' || name === 'probability' || name === 'stage_id' || name === 'contact_id' || name === 'company_id' || name === 'owner_id'
        ? parseInt(value) || 0
        : value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    if (formData.value <= 0) {
      newErrors.value = 'Value must be greater than 0';
    }
    if (formData.contact_id <= 0) {
      newErrors.contact_id = 'Contact is required';
    }
    if (formData.owner_id <= 0) {
      newErrors.owner_id = 'Owner is required';
    }
    if (!formData.expected_close_date) {
      newErrors.expected_close_date = 'Expected close date is required';
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
        await pipelineApi.createOpportunity(formData);
      } else {
        await pipelineApi.updateOpportunity(opportunity.id, formData);
      }
      onSave();
    } catch (error) {
      console.error('Error saving opportunity:', error);
      setErrors({ general: 'Failed to save opportunity. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!opportunity || isCreating) return;
    
    if (window.confirm('Are you sure you want to delete this opportunity?')) {
      setLoading(true);
      try {
        await pipelineApi.deleteOpportunity(opportunity.id);
        onSave();
      } catch (error) {
        console.error('Error deleting opportunity:', error);
        setErrors({ general: 'Failed to delete opportunity. Please try again.' });
      } finally {
        setLoading(false);
      }
    }
  };

  const selectedContact = contacts.find(c => c.id === formData.contact_id);
  const selectedStage = stages.find(s => s.id === formData.stage_id);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-gradient-to-b from-slate-800 to-slate-900 rounded-xl shadow-2xl border border-orange-500/20 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">
            {isCreating ? 'Create New Opportunity' : 'Edit Opportunity'}
          </h2>
          <div className="flex items-center space-x-2">
            {!isCreating && (
              <button
                onClick={handleDelete}
                className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                disabled={loading}
              >
                <Trash2 className="h-5 w-5" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {errors.general && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm">
              {errors.general}
            </div>
          )}

          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="Opportunity name"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-400">{errors.name}</p>
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
              placeholder="Describe the opportunity..."
            />
          </div>

          {/* Value and Probability Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <DollarSign className="h-4 w-4 inline mr-1" />
                Value *
              </label>
              <input
                type="number"
                name="value"
                value={formData.value}
                onChange={handleInputChange}
                min="0"
                step="0.01"
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="0.00"
              />
              {errors.value && (
                <p className="mt-1 text-sm text-red-400">{errors.value}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Probability (%)
              </label>
              <input
                type="number"
                name="probability"
                value={formData.probability}
                onChange={handleInputChange}
                min="0"
                max="100"
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
              {selectedStage && (
                <p className="mt-1 text-xs text-gray-400">
                  Stage default: {selectedStage.probability}%
                </p>
              )}
            </div>
          </div>

          {/* Contact and Company Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <User className="h-4 w-4 inline mr-1" />
                Contact *
              </label>
              <select
                name="contact_id"
                value={formData.contact_id}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value={0}>Select a contact</option>
                {contacts.map(contact => (
                  <option key={contact.id} value={contact.id}>
                    {contact.first_name} {contact.last_name}
                  </option>
                ))}
              </select>
              {errors.contact_id && (
                <p className="mt-1 text-sm text-red-400">{errors.contact_id}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Building className="h-4 w-4 inline mr-1" />
                Company
              </label>
              <select
                name="company_id"
                value={formData.company_id || ''}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="">Select a company (optional)</option>
                {companies.map(company => (
                  <option key={company.id} value={company.id}>
                    {company.name}
                  </option>
                ))}
              </select>
              {selectedContact?.company && (
                <p className="mt-1 text-xs text-gray-400">
                  Contact's company: {selectedContact.company.name}
                </p>
              )}
            </div>
          </div>

          {/* Stage and Owner Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Sales Stage *
              </label>
              <select
                name="stage_id"
                value={formData.stage_id}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                {stages.map(stage => (
                  <option key={stage.id} value={stage.id}>
                    {stage.name} ({stage.probability}%)
                  </option>
                ))}
              </select>
            </div>

            {/* ADDED: Owner Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <User className="h-4 w-4 inline mr-1" />
                Owner *
              </label>
              <select
                name="owner_id"
                value={formData.owner_id}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value={0}>Select an owner</option>
                {users.map(user => (
                  <option key={user.id} value={user.id}>
                    {user.first_name} {user.last_name}
                  </option>
                ))}
              </select>
              {errors.owner_id && (
                <p className="mt-1 text-sm text-red-400">{errors.owner_id}</p>
              )}
            </div>
          </div>

          {/* Priority and Expected Close Date Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Priority
              </label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Calendar className="h-4 w-4 inline mr-1" />
                Expected Close Date *
              </label>
              <input
                type="date"
                name="expected_close_date"
                value={formData.expected_close_date}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
              {errors.expected_close_date && (
                <p className="mt-1 text-sm text-red-400">{errors.expected_close_date}</p>
              )}
            </div>
          </div>

          {/* Weighted Value Display */}
          <div className="bg-slate-700/30 rounded-lg p-4 border border-gray-600">
            <h4 className="text-sm font-medium text-gray-300 mb-2">Calculated Values</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Opportunity Value:</span>
                <div className="text-white font-medium">
                  ${formData.value.toLocaleString()}
                </div>
              </div>
              <div>
                <span className="text-gray-400">Weighted Value:</span>
                <div className="text-green-400 font-medium">
                  ${((formData.value * formData.probability) / 100).toLocaleString()}
                </div>
              </div>
            </div>
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
              className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-6 py-2 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Save className="h-4 w-4" />
              )}
              <span>{loading ? 'Saving...' : (isCreating ? 'Create Opportunity' : 'Update Opportunity')}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OpportunityModal;