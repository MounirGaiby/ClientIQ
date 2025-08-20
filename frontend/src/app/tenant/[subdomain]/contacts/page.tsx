'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Layout } from '@/components/layout';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { PlusIcon, PencilIcon, TrashIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline';

interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  job_title: string;
  company_name: string;
  company_id: number | null;
  tags: string[];
  notes: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ContactFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  job_title: string;
  company_name: string;
  tags: string;
  notes: string;
}

export default function ContactsPage() {
  const router = useRouter();
  const params = useParams();
  const { user, token, logout } = useAuth();
  const subdomain = params.subdomain as string;
  
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);
  const [formData, setFormData] = useState<ContactFormData>({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    job_title: '',
    company_name: '',
    tags: '',
    notes: '',
  });

  const makeApiRequest = useCallback(async (url: string, options: RequestInit = {}) => {
    if (!token) throw new Error('No authentication token');
    
    return fetch(`http://localhost:8000${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Host': `${subdomain}.localhost`,
        ...options.headers,
      },
    });
  }, [token, subdomain]);

  const fetchContacts = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await makeApiRequest('/api/v1/contacts/');
      
      if (response.ok) {
        const data = await response.json();
        setContacts(data);
      } else if (response.status === 401) {
        logout();
        router.push(`/tenant/${subdomain}/login`);
      } else {
        setError('Failed to load contacts');
      }
    } catch (error) {
      console.error('Error fetching contacts:', error);
      setError('Failed to load contacts');
    } finally {
      setIsLoading(false);
    }
  }, [makeApiRequest, logout, router, subdomain]);

  useEffect(() => {
    if (!user) {
      router.replace(`/tenant/${subdomain}/login`);
    } else {
      fetchContacts();
    }
  }, [user, router, subdomain, fetchContacts]);

  const handleCreateContact = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError('');
      const tagsArray = formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag);
      
      const response = await makeApiRequest('/api/v1/contacts/', {
        method: 'POST',
        body: JSON.stringify({
          ...formData,
          tags: tagsArray,
        }),
      });

      if (response.ok) {
        setShowForm(false);
        setFormData({
          first_name: '',
          last_name: '',
          email: '',
          phone_number: '',
          job_title: '',
          company_name: '',
          tags: '',
          notes: '',
        });
        fetchContacts();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create contact');
      }
    } catch (error) {
      console.error('Error creating contact:', error);
      setError('Failed to create contact');
    }
  };

  const handleUpdateContact = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingContact) return;

    try {
      setError('');
      const tagsArray = formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag);

      const response = await makeApiRequest(`/api/v1/contacts/${editingContact.id}/`, {
        method: 'PUT',
        body: JSON.stringify({
          ...formData,
          tags: tagsArray,
        }),
      });

      if (response.ok) {
        setShowForm(false);
        setEditingContact(null);
        setFormData({
          first_name: '',
          last_name: '',
          email: '',
          phone_number: '',
          job_title: '',
          company_name: '',
          tags: '',
          notes: '',
        });
        fetchContacts();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update contact');
      }
    } catch (error) {
      console.error('Error updating contact:', error);
      setError('Failed to update contact');
    }
  };

  const handleDeleteContact = async (contactId: number) => {
    if (!confirm('Are you sure you want to delete this contact?')) return;

    try {
      setError('');
      const response = await makeApiRequest(`/api/v1/contacts/${contactId}/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchContacts();
      } else {
        setError('Failed to delete contact');
      }
    } catch (error) {
      console.error('Error deleting contact:', error);
      setError('Failed to delete contact');
    }
  };

  const startEditing = (contact: Contact) => {
    setEditingContact(contact);
    setFormData({
      first_name: contact.first_name,
      last_name: contact.last_name,
      email: contact.email,
      phone_number: contact.phone_number,
      job_title: contact.job_title,
      company_name: contact.company_name,
      tags: contact.tags.join(', '),
      notes: contact.notes,
    });
    setShowForm(true);
  };

  const cancelForm = () => {
    setShowForm(false);
    setEditingContact(null);
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone_number: '',
      job_title: '',
      company_name: '',
      tags: '',
      notes: '',
    });
  };

  if (!user) {
    return null;
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Contacts</h1>
            <p className="text-muted-foreground">
              Manage your business contacts and relationships
            </p>
          </div>
          <Button onClick={() => setShowForm(true)} className="flex items-center gap-2">
            <PlusIcon className="w-4 h-4" />
            Add Contact
          </Button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {showForm && (
          <Card>
            <CardHeader>
              <CardTitle>
                {editingContact ? 'Edit Contact' : 'Create New Contact'}
              </CardTitle>
              <CardDescription>
                {editingContact 
                  ? 'Update contact information and details' 
                  : 'Add a new contact to your database'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={editingContact ? handleUpdateContact : handleCreateContact} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="first_name">First Name</Label>
                    <Input
                      id="first_name"
                      type="text"
                      value={formData.first_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, first_name: e.target.value }))}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="last_name">Last Name</Label>
                    <Input
                      id="last_name"
                      type="text"
                      value={formData.last_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="phone_number">Phone Number</Label>
                    <Input
                      id="phone_number"
                      type="text"
                      value={formData.phone_number}
                      onChange={(e) => setFormData(prev => ({ ...prev, phone_number: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="job_title">Job Title</Label>
                    <Input
                      id="job_title"
                      type="text"
                      value={formData.job_title}
                      onChange={(e) => setFormData(prev => ({ ...prev, job_title: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="company_name">Company Name</Label>
                  <Input
                    id="company_name"
                    type="text"
                    value={formData.company_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, company_name: e.target.value }))}
                  />
                </div>

                <div>
                  <Label htmlFor="tags">Tags (comma-separated)</Label>
                  <Input
                    id="tags"
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
                    placeholder="e.g. client, prospect, partner"
                  />
                </div>

                <div>
                  <Label htmlFor="notes">Notes</Label>
                  <textarea
                    id="notes"
                    value={formData.notes}
                    onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                    className="w-full min-h-[100px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Additional notes about this contact..."
                  />
                </div>

                <div className="flex gap-2">
                  <Button type="submit">
                    {editingContact ? 'Update Contact' : 'Create Contact'}
                  </Button>
                  <Button type="button" variant="outline" onClick={cancelForm}>
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {isLoading ? (
          <div className="flex justify-center py-8">
            <div className="text-muted-foreground">Loading contacts...</div>
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Contacts ({contacts.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {contacts.map((contact) => (
                  <div
                    key={contact.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium">
                          {contact.first_name} {contact.last_name}
                        </h3>
                        {!contact.is_active && (
                          <Badge variant="destructive">Inactive</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{contact.email}</p>
                      {contact.phone_number && (
                        <p className="text-sm text-muted-foreground">{contact.phone_number}</p>
                      )}
                      {contact.job_title && contact.company_name && (
                        <p className="text-sm text-muted-foreground flex items-center gap-1">
                          <BuildingOfficeIcon className="w-3 h-3" />
                          {contact.job_title} at {contact.company_name}
                        </p>
                      )}
                      {contact.tags.length > 0 && (
                        <div className="flex gap-1 mt-1">
                          {contact.tags.map((tag, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                      <p className="text-xs text-muted-foreground mt-1">
                        Added {new Date(contact.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => startEditing(contact)}
                        className="flex items-center gap-1"
                      >
                        <PencilIcon className="w-4 h-4" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteContact(contact.id)}
                        className="flex items-center gap-1 text-red-600 hover:text-red-700"
                      >
                        <TrashIcon className="w-4 h-4" />
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
                {contacts.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No contacts found. Add your first contact to get started.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
}
