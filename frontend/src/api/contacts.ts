// frontend/src/api/contacts.ts
import { apiClient } from './client';

export interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  job_title?: string;
  contact_type: string;
  score: number;
  priority: 'low' | 'medium' | 'high';
  is_active: boolean;
  company?: {
    id: number;
    name: string;
  };
  owner?: {
    id: number;
    first_name: string;
    last_name: string;
  };
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

export const contactsApi = {
  // Get all contacts
  getContacts: async (params?: Record<string, any>): Promise<{ results: Contact[]; count: number }> => {
    const response = await apiClient.get('/api/v1/contacts/', { params });
    return response.data;
  },

  // Get single contact
  getContact: async (contactId: number): Promise<Contact> => {
    const response = await apiClient.get(`/api/v1/contacts/${contactId}/`);
    return response.data;
  },

  // Create new contact
  createContact: async (contactData: ContactFormData): Promise<Contact> => {
    const response = await apiClient.post('/api/v1/contacts/', contactData);
    return response.data;
  },

  // Update contact
  updateContact: async (contactId: number, contactData: Partial<ContactFormData>): Promise<Contact> => {
    const response = await apiClient.put(`/api/v1/contacts/${contactId}/`, contactData);
    return response.data;
  },

  // Delete contact
  deleteContact: async (contactId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/contacts/${contactId}/`);
  },

  // Get all companies
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

  // Get contact types
  getContactTypes: async (): Promise<string[]> => {
    try {
      const response = await apiClient.get('/api/v1/contacts/types/');
      return response.data;
    } catch (error) {
      // Return default types if endpoint doesn't exist
      return ['lead', 'prospect', 'customer', 'partner'];
    }
  },

  // Search contacts
  searchContacts: async (query: string): Promise<Contact[]> => {
    const response = await apiClient.get('/api/v1/contacts/', { 
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
    const response = await apiClient.get('/api/v1/contacts/', { 
      params: { company: companyId } 
    });
    return response.data.results || response.data;
  },

  // Bulk operations
  bulkUpdateContacts: async (contactIds: number[], updateData: Partial<ContactFormData>): Promise<void> => {
    await apiClient.post('/api/v1/contacts/bulk_update/', {
      contact_ids: contactIds,
      ...updateData
    });
  },

  bulkDeleteContacts: async (contactIds: number[]): Promise<void> => {
    await apiClient.post('/api/v1/contacts/bulk_delete/', {
      contact_ids: contactIds
    });
  }
};