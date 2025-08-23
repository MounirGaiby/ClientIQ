import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Edit3, 
  Trash2, 
  Phone, 
  Mail, 
  Building, 
  User,
  Star,
  Clock,
  ChevronDown
} from 'lucide-react';

// Let's first test without the context imports
// import { useAuth } from '../contexts/AuthContext';
// import { useTenant } from '../contexts/TenantContext';

const ContactManagement = () => {
  const [contacts, setContacts] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false); // Set to false for testing
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedContact, setSelectedContact] = useState(null);
  const [error, setError] = useState('');
  
  // Mock auth and tenant data for testing
  const token = 'test-token';
  const getCurrentSubdomain = () => 'acme';
  const getTenantApiUrl = () => 'http://localhost:8000';

  // Commented out for now - we'll add this back later
  // const { token } = useAuth();
  // const { getTenantApiUrl, getCurrentSubdomain } = useTenant();

  const contactTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'lead', label: 'Lead' },
    { value: 'prospect', label: 'Prospect' },
    { value: 'customer', label: 'Customer' },
    { value: 'partner', label: 'Partner' }
  ];

  // Simplified fetch function for testing
  const fetchContacts = async () => {
    console.log('Fetching contacts...');
    try {
      setLoading(true);
      
      // Mock data for testing
      const mockContacts = [
        {
          id: 1,
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '+1234567890',
          job_title: 'CEO',
          company: { id: 1, name: 'Test Company' },
          contact_type: 'lead',
          score: 85,
          created_at: '2024-01-01T10:00:00Z'
        },
        {
          id: 2,
          first_name: 'Jane',
          last_name: 'Smith',
          email: 'jane@example.com',
          phone: '+1987654321',
          job_title: 'CTO',
          company: { id: 2, name: 'Another Company' },
          contact_type: 'customer',
          score: 92,
          created_at: '2024-01-02T10:00:00Z'
        }
      ];
      
      setContacts(mockContacts);
      setError('');
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to fetch contacts');
    } finally {
      setLoading(false);
    }
  };

  // Simplified fetch companies
  const fetchCompanies = async () => {
    console.log('Fetching companies...');
    const mockCompanies = [
      { id: 1, name: 'Test Company' },
      { id: 2, name: 'Another Company' },
      { id: 3, name: 'Third Company' }
    ];
    setCompanies(mockCompanies);
  };

  // Load data on component mount
  useEffect(() => {
    console.log('Component mounted, loading data...');
    fetchContacts();
    fetchCompanies();
  }, []); // Remove dependencies for now

  // Helper functions
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getTypeColor = (type) => {
    const colors = {
      lead: 'text-blue-400 bg-blue-500/20',
      prospect: 'text-purple-400 bg-purple-500/20',
      customer: 'text-green-400 bg-green-500/20',
      partner: 'text-orange-400 bg-orange-500/20'
    };
    return colors[type] || 'text-gray-400 bg-gray-500/20';
  };

  // Simplified save and delete functions
  const saveContact = async (contactData) => {
    console.log('Saving contact:', contactData);
    // Mock save - just close the modal
    setShowCreateModal(false);
    setShowEditModal(false);
    setSelectedContact(null);
  };

  const deleteContact = async (contactId) => {
    if (!confirm('Are you sure you want to delete this contact?')) return;
    console.log('Deleting contact:', contactId);
    // Mock delete - remove from array
    setContacts(prev => prev.filter(c => c.id !== contactId));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Contact Management</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-4 py-2 rounded-lg font-semibold shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 transition-all duration-200 flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Contact
        </button>
      </div>

      {/* Debug Info */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <p className="text-blue-400">
          Debug: Component loaded successfully! Contacts: {contacts.length}, Companies: {companies.length}
        </p>
      </div>

      {/* Filters */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-slate-700 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search contacts by name, email, or company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>
          
          {/* Type Filter */}
          <div className="relative">
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="appearance-none bg-slate-700/50 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent pr-8"
            >
              {contactTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Contacts Table */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-700/50 border-b border-slate-600">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Contact</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Contact Info</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Added</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-slate-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {contacts.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center">
                    <div className="text-center">
                      <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-white mb-2">No contacts found</h3>
                      <p className="text-gray-400 mb-4">
                        {searchTerm || selectedType !== 'all' 
                          ? 'Try adjusting your filters or search terms.'
                          : 'Get started by adding your first contact.'
                        }
                      </p>
                      {!searchTerm && selectedType === 'all' && (
                        <button
                          onClick={() => setShowCreateModal(true)}
                          className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-4 py-2 rounded-lg font-semibold"
                        >
                          Add First Contact
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ) : (
                contacts.map((contact) => (
                  <tr key={contact.id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 bg-gradient-to-br from-orange-500 to-pink-500 rounded-full flex items-center justify-center">
                          <span className="text-white font-medium">
                            {contact.first_name?.charAt(0)}{contact.last_name?.charAt(0)}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-white">
                            {contact.first_name} {contact.last_name}
                          </div>
                          {contact.job_title && (
                            <div className="text-sm text-slate-400">{contact.job_title}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {contact.company ? (
                        <div className="flex items-center text-sm text-slate-300">
                          <Building className="h-4 w-4 mr-2 text-slate-400" />
                          {typeof contact.company === 'object' ? contact.company.name : contact.company}
                        </div>
                      ) : (
                        <span className="text-slate-500 text-sm">No company</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTypeColor(contact.contact_type)}`}>
                        {contact.contact_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Star className="h-4 w-4 mr-1 text-yellow-500" />
                        <span className={`font-semibold ${getScoreColor(contact.score)}`}>
                          {contact.score || 0}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="space-y-1">
                        <div className="flex items-center text-sm text-slate-300">
                          <Mail className="h-4 w-4 mr-2 text-slate-400" />
                          {contact.email}
                        </div>
                        {contact.phone && (
                          <div className="flex items-center text-sm text-slate-300">
                            <Phone className="h-4 w-4 mr-2 text-slate-400" />
                            {contact.phone}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-slate-300">
                        <Clock className="h-4 w-4 mr-2 text-slate-400" />
                        {new Date(contact.created_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => {
                            setSelectedContact(contact);
                            setShowEditModal(true);
                          }}
                          className="text-slate-400 hover:text-orange-400 transition-colors p-1"
                        >
                          <Edit3 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => deleteContact(contact.id)}
                          className="text-slate-400 hover:text-red-400 transition-colors p-1"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Modal */}
      {(showCreateModal || showEditModal) && (
        <ContactModal
          isEdit={showEditModal}
          contact={selectedContact}
          companies={companies}
          onSave={saveContact}
          onClose={() => {
            setShowCreateModal(false);
            setShowEditModal(false);
            setSelectedContact(null);
          }}
        />
      )}
    </div>
  );
};

// Simplified Contact Modal Component
const ContactModal = ({ isEdit, contact, companies, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    first_name: contact?.first_name || '',
    last_name: contact?.last_name || '',
    email: contact?.email || '',
    phone: contact?.phone || '',
    job_title: contact?.job_title || '',
    company: contact?.company?.id || contact?.company || '',
    contact_type: contact?.contact_type || 'lead',
    score: contact?.score || 0,
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    console.log('Form submitted with data:', formData);
    
    const submitData = {
      ...formData,
      company: formData.company ? parseInt(formData.company) : null,
      score: parseInt(formData.score) || 0,
    };
    
    await onSave(submitData);
    setLoading(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            {isEdit ? 'Edit Contact' : 'Add New Contact'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name Fields */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  placeholder="John"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  placeholder="Doe"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="john@example.com"
              />
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Phone
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            {/* Job Title */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Job Title
              </label>
              <input
                type="text"
                name="job_title"
                value={formData.job_title}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="Sales Manager"
              />
            </div>

            {/* Company */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Company
              </label>
              <select
                name="company"
                value={formData.company}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="">Select a company</option>
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Contact Type */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Contact Type
              </label>
              <select
                name="contact_type"
                value={formData.contact_type}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="lead">Lead</option>
                <option value="prospect">Prospect</option>
                <option value="customer">Customer</option>
                <option value="partner">Partner</option>
              </select>
            </div>

            {/* Score */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Score (0-100)
              </label>
              <input
                type="number"
                name="score"
                min="0"
                max="100"
                value={formData.score}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="50"
              />
            </div>

            {/* Buttons */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-4 py-2 rounded-lg font-semibold shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Saving...' : (isEdit ? 'Update Contact' : 'Create Contact')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ContactManagement;