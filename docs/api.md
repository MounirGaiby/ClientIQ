# API Documentation

## Overview

ClientIQ provides a **multi-tenant REST API** built with Django REST Framework. The API automatically routes to the correct tenant based on the domain and provides JWT-based authentication with tenant isolation.

## Base URLs

### Tenant-Specific APIs

```text
# ACME Tenant
https://acme.localhost:8000/api/v1/

# TechCorp Tenant  
https://techcorp.localhost:8000/api/v1/

# Production Example
https://acme.clientiq.com/api/v1/
```

### Platform APIs (Public Schema)

```text
# Platform Administration
https://localhost:8000/admin/api/

# Demo Requests (No authentication required)
https://localhost:8000/api/v1/demo/
```

## Authentication

### JWT Token Authentication

**Login (Get JWT Token):**

```bash
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "admin@acme.com",
  "password": "admin123"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "admin@acme.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_admin": true,
    "job_title": "Administrator",
    "department": "Management"
  }
}
```

**Using JWT Token:**

```bash
# Include in Authorization header
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

# Example request
curl -H "Authorization: Bearer <token>" \
     https://acme.localhost:8000/api/v1/users/
```

**Refresh Token:**

```bash
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Logout (Blacklist Token):**

```bash
POST /api/v1/auth/logout/
Authorization: Bearer <token>
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

# Response
{
  "message": "Successfully logged out"
}
```

## User Management API

### Current User

**Get Current User Info:**

```bash
GET /api/v1/auth/user/
Authorization: Bearer <token>

# Response
{
  "id": 1,
  "email": "admin@acme.com",
  "first_name": "Admin",
  "last_name": "User",
  "is_admin": true,
  "job_title": "Administrator",
  "department": "Management",
  "date_joined": "2025-08-19T10:30:00Z",
  "last_login": "2025-08-19T14:45:00Z"
}
```

**Update Current User:**

```bash
PUT /api/v1/auth/user/
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "Name",
  "job_title": "Senior Administrator",
  "department": "IT"
}
```

### User CRUD Operations

**List Tenant Users:**

```bash
GET /api/v1/users/
Authorization: Bearer <token>

# Query parameters
?page=1&page_size=20
?search=john
?department=IT
?is_admin=true

# Response
{
  "count": 25,
  "next": "http://acme.localhost:8000/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "admin@acme.com",
      "first_name": "Admin",
      "last_name": "User",
      "is_admin": true,
      "job_title": "Administrator",
      "department": "Management",
      "date_joined": "2025-08-19T10:30:00Z"
    },
    // ... more users
  ]
}
```

**Create New User:**

```bash
POST /api/v1/users/
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newuser@acme.com",
  "password": "securepassword123",
  "first_name": "New",
  "last_name": "User",
  "job_title": "Developer",
  "department": "Engineering",
  "is_admin": false
}

# Response
{
  "id": 26,
  "email": "newuser@acme.com",
  "first_name": "New",
  "last_name": "User",
  "is_admin": false,
  "job_title": "Developer",
  "department": "Engineering",
  "date_joined": "2025-08-19T15:00:00Z"
}
```

**Get User Details:**

```bash
GET /api/v1/users/{id}/
Authorization: Bearer <token>

# Response
{
  "id": 1,
  "email": "admin@acme.com",
  "first_name": "Admin",
  "last_name": "User",
  "is_admin": true,
  "job_title": "Administrator",
  "department": "Management",
  "date_joined": "2025-08-19T10:30:00Z",
  "last_login": "2025-08-19T14:45:00Z",
  "groups": [
    {
      "id": 1,
      "name": "Tenant Admins"
    }
  ]
}
```

**Update User:**

```bash
PUT /api/v1/users/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "User",
  "job_title": "Senior Developer",
  "department": "Engineering",
  "is_admin": false
}

# Partial update with PATCH
PATCH /api/v1/users/{id}/
{
  "job_title": "Lead Developer"
}
```

**Delete User:**

```bash
DELETE /api/v1/users/{id}/
Authorization: Bearer <token>

# Response: 204 No Content
```

## Demo Request API

### Public Demo Requests (No Authentication)

**Submit Demo Request:**

```bash
POST /api/v1/demo/requests/
Content-Type: application/json

{
  "company_name": "TechCorp Ltd",
  "contact_email": "admin@techcorp.com",
  "contact_name": "John Smith",
  "contact_phone": "+1-555-0123",
  "industry": "Technology",
  "company_size": "51-200",
  "message": "We're interested in your platform for our team collaboration needs."
}

# Response
{
  "id": 5,
  "company_name": "TechCorp Ltd",
  "contact_email": "admin@techcorp.com",
  "contact_name": "John Smith",
  "status": "pending",
  "created_at": "2025-08-19T15:30:00Z",
  "message": "Thank you for your demo request. We'll contact you within 24 hours."
}
```

**Check Demo Request Status:**

```bash
GET /api/v1/demo/requests/{id}/
# or
GET /api/v1/demo/requests/?email=admin@techcorp.com

# Response
{
  "id": 5,
  "company_name": "TechCorp Ltd",
  "contact_email": "admin@techcorp.com",
  "status": "approved",  # pending, approved, rejected, converted
  "created_at": "2025-08-19T15:30:00Z",
  "updated_at": "2025-08-19T16:00:00Z"
}
```

## Error Handling

### Standard Error Responses

**400 Bad Request:**

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": {
    "email": ["This field is required."],
    "password": ["Password must be at least 8 characters."]
  }
}
```

**401 Unauthorized:**

```json
{
  "error": "authentication_failed",
  "message": "Invalid credentials or token expired"
}
```

**403 Forbidden:**

```json
{
  "error": "permission_denied",
  "message": "You do not have permission to perform this action"
}
```

**404 Not Found:**

```json
{
  "error": "not_found",
  "message": "User not found"
}
```

**429 Rate Limited:**

```json
{
  "error": "throttled",
  "message": "Request was throttled. Try again in 60 seconds."
}
```

### Tenant-Specific Errors

**Invalid Tenant Domain:**

```json
{
  "error": "tenant_not_found",
  "message": "No tenant found for domain: invalid.localhost"
}
```

**Cross-Tenant Access Attempt:**

```json
{
  "error": "tenant_isolation_violation",
  "message": "User does not exist in current tenant context"
}
```

## Rate Limiting

### API Rate Limits

```text
Authentication endpoints: 5 requests/minute
User CRUD operations: 100 requests/minute  
Demo requests: 10 requests/minute
General API: 1000 requests/hour
```

**Rate Limit Headers:**

```text
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1629384000
```

## Pagination

### Standard Pagination

```bash
GET /api/v1/users/?page=2&page_size=10

# Response
{
  "count": 25,
  "next": "http://acme.localhost:8000/api/v1/users/?page=3&page_size=10",
  "previous": "http://acme.localhost:8000/api/v1/users/?page=1&page_size=10",
  "results": [...]
}
```

### Cursor Pagination (Large Datasets)

```bash
GET /api/v1/users/?cursor=cD0yMDI1LTA4LTE5KzE0JTNBMzA%3D

# Response
{
  "next": "http://acme.localhost:8000/api/v1/users/?cursor=cD0yMDI1LTA4LTE5KzE1JTNBMzA%3D",
  "previous": null,
  "results": [...]
}
```

## Filtering and Search

### User Filtering

```bash
# Filter by department
GET /api/v1/users/?department=Engineering

# Filter by admin status
GET /api/v1/users/?is_admin=true

# Search by name or email
GET /api/v1/users/?search=john

# Combined filters
GET /api/v1/users/?department=IT&search=admin&is_admin=true

# Date range filters
GET /api/v1/users/?date_joined__gte=2025-01-01&date_joined__lt=2025-12-31
```

### Ordering

```bash
# Order by date joined (newest first)
GET /api/v1/users/?ordering=-date_joined

# Order by name
GET /api/v1/users/?ordering=first_name,last_name

# Multiple ordering
GET /api/v1/users/?ordering=department,last_name
```

## Webhooks

### Demo Request Webhooks

**Configuration:**

```python
# settings.py
WEBHOOK_ENDPOINTS = {
    'demo_request_created': 'https://your-app.com/webhooks/demo-created/',
    'demo_request_approved': 'https://your-app.com/webhooks/demo-approved/',
}
```

**Webhook Payload:**

```json
{
  "event": "demo_request_created",
  "timestamp": "2025-08-19T15:30:00Z",
  "data": {
    "id": 5,
    "company_name": "TechCorp Ltd",
    "contact_email": "admin@techcorp.com",
    "status": "pending"
  }
}
```

## SDK Examples

### Python SDK

```python
import requests

class ClientIQAPI:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def login(self, email, password):
        response = self.session.post(
            f'{self.base_url}/auth/login/',
            json={'email': email, 'password': password}
        )
        data = response.json()
        self.session.headers.update({
            'Authorization': f'Bearer {data["access"]}'
        })
        return data
    
    def list_users(self, **params):
        response = self.session.get(
            f'{self.base_url}/users/',
            params=params
        )
        return response.json()
    
    def create_user(self, user_data):
        response = self.session.post(
            f'{self.base_url}/users/',
            json=user_data
        )
        return response.json()

# Usage
api = ClientIQAPI('https://acme.localhost:8000/api/v1')
api.login('admin@acme.com', 'admin123')
users = api.list_users(department='Engineering')
```

### JavaScript SDK

```javascript
class ClientIQAPI {
  constructor(baseUrl, token = null) {
    this.baseUrl = baseUrl;
    this.token = token;
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }
    
    const response = await fetch(url, {
      ...options,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    
    return response.json();
  }
  
  async login(email, password) {
    const data = await this.request('/auth/login/', {
      method: 'POST',
      body: { email, password },
    });
    this.token = data.access;
    return data;
  }
  
  async listUsers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/users/?${query}`);
  }
  
  async createUser(userData) {
    return this.request('/users/', {
      method: 'POST',
      body: userData,
    });
  }
}

// Usage
const api = new ClientIQAPI('https://acme.localhost:8000/api/v1');
await api.login('admin@acme.com', 'admin123');
const users = await api.listUsers({ department: 'Engineering' });
```

## Testing the API

### Development Testing

```bash
# Test authentication
curl -X POST http://acme.localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@acme.com", "password": "admin123"}'

# Test user listing
curl -H "Authorization: Bearer <token>" \
  http://acme.localhost:8000/api/v1/users/

# Test user creation
curl -X POST http://acme.localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@acme.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Automated Testing

```python
# API tests
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    # Login and set token
    response = api_client.post('/api/v1/auth/login/', {
        'email': 'admin@acme.com',
        'password': 'admin123'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

def test_list_users(authenticated_client):
    response = authenticated_client.get('/api/v1/users/')
    assert response.status_code == 200
    assert 'results' in response.data

def test_create_user(authenticated_client):
    user_data = {
        'email': 'newuser@acme.com',
        'password': 'testpass123',
        'first_name': 'New',
        'last_name': 'User'
    }
    response = authenticated_client.post('/api/v1/users/', user_data)
    assert response.status_code == 201
    assert response.data['email'] == user_data['email']
```

This API provides **secure, tenant-isolated access** to ClientIQ functionality with **comprehensive authentication** and **intuitive RESTful endpoints**.
