// frontend/src/components/ContactManagement.jsx - Fixed to connect to backend API
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
  ChevronDown,
  Filter,
  MoreVertical
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { contactsApi } from '../api/contacts';
import ContactModal from './ContactModal';

const ContactManagement = () => {
  const [contacts, setContacts] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedContact, setSelectedContact] = useState(null);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    total: 0,
    by_type: {},
    by_score_level: {}
  });

  const { user } = useAuth();

  const contactTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'lead', label: 'Lead' },
    { value: 'prospect', label: 'Prospect' },
    { value: 'customer', label: 'Customer' },
    { value: 'partner', label: 'Partner' }
  ];

  // Fetch contacts from backend API
  const fetchContacts = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedType !== 'all') params.contact_type = selectedType;
      
      const response = await contactsApi.getContacts(params);
      setContacts(response.results || response);
      
      console.log('Contacts loaded from API:', response.results?.length || response.length || 0);
    } catch (error) {
      console.error('Error fetching contacts:', error);
      setError('Failed to load contacts. Please try again.');
      setContacts([]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch companies for dropdowns
  const fetchCompanies = async () => {
    try {
      const response = await contactsApi.getCompanies();
      setCompanies(response.results || response);
    } catch (error) {
      console.error('Error fetching companies:', error);
      setCompanies([]);
    }
  };

  // Fetch contact statistics
  const fetchStats = async () => {
    try {
      // Using the stats endpoint if available
      const response = await contactsApi.getContacts();
      const allContacts = response.results || response;
      
      // Calculate stats from the data
      const statsData = {
        total: allContacts.length,
        by_type: {},
        by_score_level: {
          hot: 0,
          warm: 0,
          cold: 0,
          unqualified: 0
        }
      };

      // Count by type
      contactTypes.forEach(type => {
        if (type.value !== 'all') {
          statsData.by_type[type.value] = allContacts.filter(c => c.contact_type === type.value).length;
        }
      });

      // Count by score level
      allContacts.forEach(contact => {
        const score = contact.score || 0;
        if (score >= 80) statsData.by_score_level.hot++;
        else if (score >= 60) statsData.by_score_level.warm++;
        else if (score >= 40) statsData.by_score_level.cold++;
        else statsData.by_score_level.unqualified++;
      });

      setStats(statsData);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Load data on component mount and when search/filter changes
  useEffect(() => {
    fetchContacts();
    fetchStats();
  }, [searchTerm, selectedType]);

  // Load companies once on mount
  useEffect(() => {
    fetchCompanies();
  }, []);

  // Create or update contact
  const saveContact = async (contactData) => {
    try {
      setError('');
      if (selectedContact) {
        // Update existing contact
        await contactsApi.updateContact(selectedContact.id, contactData);
      } else {
        // Create new contact
        await contactsApi.createContact(contactData);
      }
      
      // Close modal and refresh data
      setShowCreateModal(false);
      setShowEditModal(false);
      setSelectedContact(null);
      
      // Refresh contacts list
      await fetchContacts();
      await fetchStats();
    } catch (error) {
      console.error('Error saving contact:', error);
      setError('Failed to save contact. Please try again.');
    }
  };

  // Delete contact
  const deleteContact = async (contactId) => {
    if (!window.confirm('Are you sure you want to delete this contact?')) {
      return;
    }

    try {
      setError('');
      await contactsApi.deleteContact(contactId);
      
      // Refresh contacts list
      await fetchContacts();
      await fetchStats();
    } catch (error) {
      console.error('Error deleting contact:', error);
      setError('Failed to delete contact. Please try again.');
    }
  };

  // Update contact score
  const updateContactScore = async (contactId, delta) => {
    try {
      const contact = contacts.find(c => c.id === contactId);
      if (!contact) return;

      // Call the update score endpoint
      await contactsApi.updateContact(contactId, {
        score: Math.max(0, Math.min(100, (contact.score || 0) + delta))
      });
      
      // Refresh contacts list
      await fetchContacts();
    } catch (error) {
      console.error('Error updating score:', error);
    }
  };

  // Open edit modal
  const openEditModal = (contact) => {
    setSelectedContact(contact);
    setShowEditModal(true);
  };

  // Open create modal
  const openCreateModal = () => {
    setSelectedContact(null);
    setShowCreateModal(true);
  };

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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading && contacts.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
        <span className="ml-2 text-gray-400">Loading contacts...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Contact Management</h2>
          <p className="text-gray-400 mt-1">
            {stats.total} total contacts
          </p>
        </div>
        <button
          onClick={openCreateModal}
          className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-4 py-2 rounded-lg font-semibold shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 transition-all duration-200 flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Contact
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-lg p-4">
          <h3 className="text-blue-400 text-sm font-medium">Total Contacts</h3>
          <p className="text-2xl font-bold text-white mt-1">{stats.total}</p>
        </div>
        <div className="bg-gradient-to-r from-green-500/20 to-teal-500/20 rounded-lg p-4">
          <h3 className="text-green-400 text-sm font-medium">Hot Leads</h3>
          <p className="text-2xl font-bold text-white mt-1">{stats.by_score_level.hot}</p>
        </div>
        <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-lg p-4">
          <h3 className="text-yellow-400 text-sm font-medium">Warm Leads</h3>
          <p className="text-2xl font-bold text-white mt-1">{stats.by_score_level.warm}</p>
        </div>
        <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg p-4">
          <h3 className="text-purple-400 text-sm font-medium">Customers</h3>
          <p className="text-2xl font-bold text-white mt-1">{stats.by_type.customer || 0}</p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search contacts by name, email, or company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex gap-2">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          >
            {contactTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Contacts Table */}
      <div className="bg-slate-800/50 rounded-lg overflow-hidden">
        {contacts.length === 0 ? (
          <div className="text-center py-12">
            <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No contacts found</h3>
            <p className="text-gray-400 mb-4">
              {searchTerm || selectedType !== 'all' 
                ? 'Try adjusting your search or filters'
                : 'Get started by adding your first contact'
              }
            </p>
            <button
              onClick={openCreateModal}
              className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Add Contact
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-700/50">
                <tr>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-300">Contact</th>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-300">Company</th>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-300">Type</th>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-300">Score</th>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-300">Created</th>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {contacts.map((contact) => (
                  <tr key={contact.id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gradient-to-r from-orange-500 to-pink-500 flex items-center justify-center text-white font-semibold">
                            {contact.first_name?.[0]}{contact.last_name?.[0]}
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-white">
                            {contact.first_name} {contact.last_name}
                          </div>
                          <div className="text-sm text-gray-400">
                            <div className="flex items-center">
                              <Mail className="h-3 w-3 mr-1" />
                              {contact.email}
                            </div>
                            {contact.phone && (
                              <div className="flex items-center mt-1">
                                <Phone className="h-3 w-3 mr-1" />
                                {contact.phone}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-white">
                        {contact.company?.name || contact.company_name || 'No Company'}
                      </div>
                      {contact.job_title && (
                        <div className="text-sm text-gray-400">{contact.job_title}</div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(contact.contact_type)}`}>
                        {contact.contact_type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <span className={`text-sm font-medium ${getScoreColor(contact.score)}`}>
                          {contact.score || 0}
                        </span>
                        <div className="ml-2 flex gap-1">
                          <button
                            onClick={() => updateContactScore(contact.id, 5)}
                            className="text-green-400 hover:text-green-300 text-xs"
                            title="Increase score"
                          >
                            +
                          </button>
                          <button
                            onClick={() => updateContactScore(contact.id, -5)}
                            className="text-red-400 hover:text-red-300 text-xs"
                            title="Decrease score"
                          >
                            -
                          </button>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-400">
                        <Clock className="h-3 w-3 inline mr-1" />
                        {formatDate(contact.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => openEditModal(contact)}
                          className="text-gray-400 hover:text-white p-1 rounded"
                          title="Edit contact"
                        >
                          <Edit3 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => deleteContact(contact.id)}
                          className="text-red-400 hover:text-red-300 p-1 rounded"
                          title="Delete contact"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Contact Modal */}
      {showCreateModal && (
        <ContactModal
          isOpen={showCreateModal}
          isCreating={true}
          onClose={() => setShowCreateModal(false)}
          onSave={saveContact}
          companies={companies}
        />
      )}

      {/* Edit Contact Modal */}
      {showEditModal && selectedContact && (
        <ContactModal
          isOpen={showEditModal}
          isCreating={false}
          isEdit={true}
          contact={selectedContact}
          onClose={() => {
            setShowEditModal(false);
            setSelectedContact(null);
          }}
          onSave={saveContact}
          companies={companies}
        />
      )}
    </div>
  );
};

export default ContactManagement;