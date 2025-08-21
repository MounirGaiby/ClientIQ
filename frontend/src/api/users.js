/**
 * User management API functions
 */

import { getAuthHeader, getBaseURL } from './config';

const BASE_URL = `${getBaseURL()}/api/v1/users`;

/**
 * Get all users for the current tenant
 */
export const getUsers = async (params = {}) => {
  const url = new URL(BASE_URL);
  
  // Add query parameters
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
      url.searchParams.append(key, params[key]);
    }
  });

  const response = await fetch(url, {
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch users: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get a specific user by ID
 */
export const getUser = async (userId) => {
  const response = await fetch(`${BASE_URL}/${userId}/`, {
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Create a new user
 */
export const createUser = async (userData) => {
  const response = await fetch(BASE_URL + '/', {
    method: 'POST',
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create user: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Update an existing user
 */
export const updateUser = async (userId, userData) => {
  const response = await fetch(`${BASE_URL}/${userId}/`, {
    method: 'PUT',
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update user: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Partially update an existing user
 */
export const patchUser = async (userId, userData) => {
  const response = await fetch(`${BASE_URL}/${userId}/`, {
    method: 'PATCH',
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update user: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Delete a user
 */
export const deleteUser = async (userId) => {
  const response = await fetch(`${BASE_URL}/${userId}/`, {
    method: 'DELETE',
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to delete user: ${response.statusText}`);
  }

  // DELETE typically returns 204 No Content
  return response.status === 204 ? {} : response.json();
};

/**
 * Get current user information
 */
export const getCurrentUser = async () => {
  const response = await fetch(`${BASE_URL}/me/`, {
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch current user: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Update current user information
 */
export const updateCurrentUser = async (userData) => {
  const response = await fetch(`${BASE_URL}/me/`, {
    method: 'PUT',
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update current user: ${response.statusText}`);
  }

  return response.json();
};
