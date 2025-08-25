// frontend/src/api/contacts.ts - Updated with correct backend API endpoints
import { apiClient } from './client';

export interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  full_name?: string; // Computed field from backend
  email: string;
  phone?: string;
  job_title?: string;
  contact_type: string;
  score: number;
  priority: 'low' | 'medium' | 'high';
  is_active: boolean;
  company?: {
    id: number;
    name: string;
  };
  company_name?: string; // Computed field from backend
  owner?: {
    id: number;
    first_name: string;
    last_name: string;
  };
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: number;
  name: string;
  website?: string;
  industry?: string;
  size?: string;
  phone?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ContactFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  job_title?: string;
  contact_type: string;
  priority: 'low' | 'medium' | 'high';
  company_id?: number;
  notes?: string;
}

export interface CompanyFormData {
  name: string;
  website?: string;
  industry?: string;
  size?: string;
  phone?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  notes?: string;
}

export interface ContactStats {
  total: number;
  by_type: Record<string, { count: number; display_name: string }>;
  by_score_level: Record<string, number>;
  by_priority: Record<string, number>;
}

export const contactsApi = {
  // CONTACTS ENDPOINTS
  
  // Get all contacts - Using ViewSet endpoint
  getContacts: async (params?: Record<string, any>): Promise<{ results: Contact[]; count: number }> => {
    const response = await apiClient.get('/api/v1/contacts/api/contacts/', { params });
    return response.data;
  },

  // Get single contact
  getContact: async (contactId: number): Promise<Contact> => {
    const response = await apiClient.get(`/api/v1/contacts/api/contacts/${contactId}/`);
    return response.data;
  },

  // Create new contact
  createContact: async (contactData: ContactFormData): Promise<Contact> => {
    const response = await apiClient.post('/api/v1/contacts/api/contacts/', contactData);
    return response.data;
  },

  // Update contact
  updateContact: async (contactId: number, contactData: Partial<ContactFormData>): Promise<Contact> => {
    const response = await apiClient.put(`/api/v1/contacts/api/contacts/${contactId}/`, contactData);
    return response.data;
  },

  // Partially update contact
  patchContact: async (contactId: number, contactData: Partial<ContactFormData>): Promise<Contact> => {
    const response = await apiClient.patch(`/api/v1/contacts/api/contacts/${contactId}/`, contactData);
    return response.data;
  },

  // Delete contact
  deleteContact: async (contactId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/contacts/api/contacts/${contactId}/`);
  },

  // Update contact score (custom action)
  updateContactScore: async (contactId: number, delta: number): Promise<{ score: number; score_level: string }> => {
    const response = await apiClient.post(`/api/v1/contacts/api/contacts/${contactId}/update_score/`, { delta });
    return response.data;
  },

  // Add tag to contact (custom action)
  addContactTag: async (contactId: number, tagId: number): Promise<void> => {
    await apiClient.post(`/api/v1/contacts/api/contacts/${contactId}/add_tag/`, { tag_id: tagId });
  },

  // Remove tag from contact (custom action)
  removeContactTag: async (contactId: number, tagId: number): Promise<void> => {
    await apiClient.post(`/api/v1/contacts/api/contacts/${contactId}/remove_tag/`, { tag_id: tagId });
  },

  // Get contact statistics (custom action)
  getContactStats: async (): Promise<ContactStats> => {
    const response = await apiClient.get('/api/v1/contacts/api/contacts/stats/');
    return response.data;
  },

  // COMPANIES ENDPOINTS

  // Get all companies - Using ViewSet endpoint
  getCompanies: async (params?: Record<string, any>): Promise<{ results: Company[]; count: number }> => {
    const response = await apiClient.get('/api/v1/contacts/api/companies/', { params });
    return response.data;
  },

  // Get single company
  getCompany: async (companyId: number): Promise<Company> => {
    const response = await apiClient.get(`/api/v1/contacts/api/companies/${companyId}/`);
    return response.data;
  },

  // Create new company
  createCompany: async (companyData: CompanyFormData): Promise<Company> => {
    const response = await apiClient.post('/api/v1/contacts/api/companies/', companyData);
    return response.data;
  },

  // Update company
  updateCompany: async (companyId: number, companyData: Partial<CompanyFormData>): Promise<Company> => {
    const response = await apiClient.put(`/api/v1/contacts/api/companies/${companyId}/`, companyData);
    return response.data;
  },

  // Delete company
  deleteCompany: async (companyId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/contacts/api/companies/${companyId}/`);
  },

  // UTILITY ENDPOINTS

  // Get contact types (if endpoint exists, otherwise fallback to defaults)
  getContactTypes: async (): Promise<string[]> => {
    try {
      const response = await apiClient.get('/api/v1/contacts/api/contact-types/');
      return response.data;
    } catch (error) {
      // Return default types if endpoint doesn't exist
      console.warn('Contact types endpoint not available, using defaults');
      return ['lead', 'prospect', 'customer', 'partner'];
    }
  },

  // Search contacts
  searchContacts: async (query: string): Promise<Contact[]> => {
    const response = await apiClient.get('/api/v1/contacts/api/contacts/', { 
      params: { search: query } 
    });
    return response.data.results || response.data;
  },

  // Search companies  
  searchCompanies: async (query: string): Promise<Company[]> => {
    const response = await apiClient.get('/api/v1/contacts/api/companies/', { 
      params: { search: query } 
    });
    return response.data.results || response.data;
  },

  // Get contacts by company
  getContactsByCompany: async (companyId: number): Promise<Contact[]> => {
    const response = await apiClient.get('/api/v1/contacts/api/contacts/', { 
      params: { company: companyId } 
    });
    return response.data.results || response.data;
  },

  // LEGACY ENDPOINTS (Simple List/Detail Views)
  // These use the simpler URLs for basic operations
  
  // Get contacts using simple endpoint
  getContactsSimple: async (params?: Record<string, any>): Promise<Contact[]> => {
    const response = await apiClient.get('/api/v1/contacts/', { params });
    return response.data.results || response.data;
  },

  // Get single contact using simple endpoint
  getContactSimple: async (contactId: number): Promise<Contact> => {
    const response = await apiClient.get(`/api/v1/contacts/${contactId}/`);
    return response.data;
  },

  // Create contact using simple endpoint
  createContactSimple: async (contactData: ContactFormData): Promise<Contact> => {
    const response = await apiClient.post('/api/v1/contacts/', contactData);
    return response.data;
  },

  // Update contact using simple endpoint
  updateContactSimple: async (contactId: number, contactData: Partial<ContactFormData>): Promise<Contact> => {
    const response = await apiClient.put(`/api/v1/contacts/${contactId}/`, contactData);
    return response.data;
  },

  // Delete contact using simple endpoint
  deleteContactSimple: async (contactId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/contacts/${contactId}/`);
  },

  // BULK OPERATIONS (if implemented in backend)
  
  // Bulk update contacts
  bulkUpdateContacts: async (contactIds: number[], updateData: Partial<ContactFormData>): Promise<void> => {
    try {
      await apiClient.post('/api/v1/contacts/api/contacts/bulk_update/', {
        contact_ids: contactIds,
        ...updateData
      });
    } catch (error) {
      console.warn('Bulk update endpoint not available');
      throw error;
    }
  },

  // Bulk delete contacts
  bulkDeleteContacts: async (contactIds: number[]): Promise<void> => {
    try {
      await apiClient.post('/api/v1/contacts/api/contacts/bulk_delete/', {
        contact_ids: contactIds
      });
    } catch (error) {
      console.warn('Bulk delete endpoint not available');
      throw error;
    }
  },

  // TAGS ENDPOINTS (if implemented)

  // Get all contact tags
  getContactTags: async (): Promise<any[]> => {
    try {
      const response = await apiClient.get('/api/v1/contacts/api/tags/');
      return response.data.results || response.data;
    } catch (error) {
      console.warn('Contact tags endpoint not available');
      return [];
    }
  },

  // Create contact tag
  createContactTag: async (tagData: { name: string; color?: string }): Promise<any> => {
    const response = await apiClient.post('/api/v1/contacts/api/tags/', tagData);
    return response.data;
  }
};

// Export individual functions for convenience
export const {
  getContacts,
  getContact,
  createContact,
  updateContact,
  deleteContact,
  getCompanies,
  getCompany,
  createCompany,
  updateCompany,
  deleteCompany,
  searchContacts,
  searchCompanies,
  getContactTypes
} = contactsApi;