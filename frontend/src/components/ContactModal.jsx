// frontend/src/components/ContactModal.jsx - Debug version with simplified validation
import React, { useState, useEffect } from 'react';
import { X, Save, User, Mail, Phone, Building, Star } from 'lucide-react';

const ContactModal = ({ 
  isEdit = false, 
  contact, 
  companies = [], 
  onSave, 
  onClose 
}) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    job_title: '',
    contact_type: 'lead',
    priority: 'medium',
    company_id: '',
    notes: ''
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const contactTypes = [
    { value: 'lead', label: 'Lead' },
    { value: 'prospect', label: 'Prospect' },
    { value: 'customer', label: 'Customer' },
    { value: 'partner', label: 'Partner' }
  ];

  const priorities = [
    { value: 'low', label: 'Low', color: 'text-gray-400' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-400' },
    { value: 'high', label: 'High', color: 'text-red-400' }
  ];

  // Initialize form data
  useEffect(() => {
    console.log('ContactModal mounted/updated:', { isEdit, contact });
    
    if (contact && isEdit) {
      console.log('Setting form data from contact:', contact);
      // Edit mode - populate form with contact data
      const newFormData = {
        first_name: contact.first_name || '',
        last_name: contact.last_name || '',
        email: contact.email || '',
        phone: contact.phone || '',
        job_title: contact.job_title || '',
        contact_type: contact.contact_type || 'lead',
        priority: contact.priority || 'medium',
        // Handle both company object and company_id
        company_id: contact.company?.id || contact.company_id || contact.company || '',
        notes: contact.notes || ''
      };
      setFormData(newFormData);
      console.log('Form data set to:', newFormData);
    } else {
      console.log('Resetting form data for create mode');
      // Create mode - reset form
      const defaultFormData = {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        job_title: '',
        contact_type: 'lead',
        priority: 'medium',
        company_id: '',
        notes: ''
      };
      setFormData(defaultFormData);
      console.log('Form data reset to:', defaultFormData);
    }
    setErrors({});
  }, [contact, isEdit]); // This useEffect will run whenever contact or isEdit changes

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    console.log(`Input changed: ${name} = ${value}`);
    
    setFormData(prev => {
      const newData = { ...prev, [name]: value };
      console.log('New form data:', newData);
      return newData;
    });

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    console.log('Validating form with data:', formData);
    const newErrors = {};

    // Required fields
    if (!formData.first_name?.trim()) {
      newErrors.first_name = 'First name is required';
      console.log('First name validation failed:', formData.first_name);
    }
    if (!formData.last_name?.trim()) {
      newErrors.last_name = 'Last name is required';
      console.log('Last name validation failed:', formData.last_name);
    }
    if (!formData.email?.trim()) {
      newErrors.email = 'Email is required';
      console.log('Email validation failed:', formData.email);
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
      console.log('Email format validation failed:', formData.email);
    }

    console.log('Validation errors:', newErrors);
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted with data:', formData);
    
    if (!validateForm()) {
      console.log('Form validation failed, not submitting');
      return;
    }

    setLoading(true);
    try {
      // Prepare data for API
      const submitData = {
        ...formData,
        company_id: formData.company_id ? parseInt(formData.company_id) : undefined
      };

      // Remove empty company_id
      if (!submitData.company_id) {
        delete submitData.company_id;
      }

      console.log('Submitting data to API:', submitData);
      await onSave(submitData);
    } catch (error) {
      console.error('Error saving contact:', error);
      setErrors({ general: 'Failed to save contact. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  // Calculate if form is valid
  const isFormValid = !!(formData.first_name?.trim() && formData.last_name?.trim() && formData.email?.trim());
  console.log('Form valid check:', {
    first_name: formData.first_name?.trim(),
    last_name: formData.last_name?.trim(), 
    email: formData.email?.trim(),
    isFormValid
  });

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
          <h2 className="text-xl font-semibold text-white flex items-center">
            <User className="h-5 w-5 mr-2" />
            {isEdit ? 'Edit Contact' : 'Add New Contact'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Debug Info */}
          {/* <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-xs text-blue-400">
            <div>Debug Info:</div>
            <div>Is Edit Mode: {isEdit ? 'YES' : 'NO'}</div>
            <div>Contact Passed: {contact ? 'YES' : 'NO'}</div>
            {contact && (
              <div className="mt-2">
                <div>Contact Data:</div>
                <div>- ID: {contact.id}</div>
                <div>- First Name: "{contact.first_name}"</div>
                <div>- Last Name: "{contact.last_name}"</div>
                <div>- Email: "{contact.email}"</div>
                <div>- Company: {contact.company?.name || contact.company_name || 'None'}</div>
              </div>
            )}
            <div className="mt-2">Form Values:</div>
            <div>- First Name: "{formData.first_name}" (length: {formData.first_name?.length || 0})</div>
            <div>- Last Name: "{formData.last_name}" (length: {formData.last_name?.length || 0})</div>
            <div>- Email: "{formData.email}" (length: {formData.email?.length || 0})</div>
            <div>- Company ID: "{formData.company_id}"</div>
            <div>Form Valid: {isFormValid ? 'YES' : 'NO'}</div>
            <div>Loading: {loading ? 'YES' : 'NO'}</div>
            <div>Button Disabled: {(loading || !isFormValid) ? 'YES' : 'NO'}</div>
          </div> */}

          {errors.general && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm">
              {errors.general}
            </div>
          )}

          {/* Name Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                First Name *
              </label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="John"
              />
              {errors.first_name && (
                <p className="mt-1 text-sm text-red-400">{errors.first_name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Last Name *
              </label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="Doe"
              />
              {errors.last_name && (
                <p className="mt-1 text-sm text-red-400">{errors.last_name}</p>
              )}
            </div>
          </div>

          {/* Email and Phone Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Mail className="h-4 w-4 inline mr-1" />
                Email *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="john@company.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-400">{errors.email}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Phone className="h-4 w-4 inline mr-1" />
                Phone
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>

          {/* Job Title and Company Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Job Title
              </label>
              <input
                type="text"
                name="job_title"
                value={formData.job_title}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="CEO, Sales Manager, etc."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Building className="h-4 w-4 inline mr-1" />
                Company
              </label>
              <select
                name="company_id"
                value={formData.company_id}
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
            </div>
          </div>

          {/* Contact Type and Priority Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Contact Type
              </label>
              <select
                name="contact_type"
                value={formData.contact_type}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                {contactTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Star className="h-4 w-4 inline mr-1" />
                Priority
              </label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                {priorities.map(priority => (
                  <option key={priority.value} value={priority.value}>
                    {priority.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Notes
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="Any additional notes about this contact..."
            />
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
              disabled={loading || !isFormValid}
              className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-6 py-2 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Save className="h-4 w-4" />
              )}
              <span>
                {loading ? 'Saving...' : (isEdit ? 'Update Contact' : 'Create Contact')}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContactModal;