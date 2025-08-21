# 🔗 API Reference

Complete API documentation for ClientIQ endpoints.

## Base URL

- **Development:** `http://localhost:8000/api/v1/`
- **Tenant URLs:** `http://{tenant}.localhost:8000/api/v1/`

## Authentication

All endpoints require JWT authentication except where noted.

```http
Authorization: Bearer {access_token}
Host: {tenant}.localhost  # For tenant-specific endpoints
```

## Authentication Endpoints

### Login

```http
POST /api/v1/auth/login/
```

**Request:**
```json
{
  "email": "admin@acme.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "user": {
    "id": 1,
    "email": "admin@acme.com",
    "first_name": "Admin",
    "last_name": "User"
  }
}
```

### Current User

```http
GET /api/v1/auth/me/
```

**Response:**
```json
{
  "id": 1,
  "email": "admin@acme.com",
  "first_name": "Admin",
  "last_name": "User",
  "department": "IT",
  "is_active": true
}
```

### Logout

```http
POST /api/v1/auth/logout/
```

**Request:**
```json
{
  "refresh": "refresh_token_here"
}
```

## User Management

### List Users

```http
GET /api/v1/users/
```

**Query Parameters:**
- `search` - Search by name or email
- `department` - Filter by department
- `is_active` - Filter by active status

**Response:**
```json
[
  {
    "id": 1,
    "email": "admin@acme.com",
    "first_name": "Admin",
    "last_name": "User",
    "department": "IT",
    "is_active": true
  }
]
```

### Create User

```http
POST /api/v1/users/
```

**Request:**
```json
{
  "email": "newuser@acme.com",
  "first_name": "New",
  "last_name": "User",
  "password": "securepassword",
  "department": "Sales"
}
```

### Get User

```http
GET /api/v1/users/{id}/
```

### Update User

```http
PUT /api/v1/users/{id}/
PATCH /api/v1/users/{id}/
```

### Delete User

```http
DELETE /api/v1/users/{id}/
```

## Contact Management

### List Contacts

```http
GET /api/v1/contacts/api/contacts/
```

**Query Parameters:**
- `search` - Search by name, email, or company
- `contact_type` - Filter by type (lead, customer, prospect)
- `is_active` - Filter by active status
- `company` - Filter by company ID
- `owner` - Filter by owner ID
- `min_score` - Minimum score filter
- `max_score` - Maximum score filter
- `tags` - Filter by tag IDs (multiple values)
- `ordering` - Sort fields (name, score, created_at)

**Response:**
```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@company.com",
    "phone": "+1234567890",
    "company": {
      "id": 1,
      "name": "Customer Corp"
    },
    "job_title": "CEO",
    "score": 85,
    "contact_type": "lead",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### Create Contact

```http
POST /api/v1/contacts/api/contacts/
```

**Request:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@newcompany.com",
  "phone": "+1987654321",
  "company": 1,
  "job_title": "Marketing Director",
  "contact_type": "prospect",
  "score": 70
}
```

### Get Contact

```http
GET /api/v1/contacts/api/contacts/{id}/
```

### Update Contact

```http
PUT /api/v1/contacts/api/contacts/{id}/
PATCH /api/v1/contacts/api/contacts/{id}/
```

### Update Contact Score

```http
POST /api/v1/contacts/api/contacts/{id}/update_score/
```

**Request:**
```json
{
  "delta": 10  // Positive or negative score change
}
```

## Company Management

### List Companies

```http
GET /api/v1/contacts/api/companies/
```

**Query Parameters:**
- `search` - Search by name, website, industry, city, country
- `industry` - Filter by industry
- `size` - Filter by company size
- `country` - Filter by country
- `ordering` - Sort fields (name, industry, created_at)

**Response:**
```json
[
  {
    "id": 1,
    "name": "ACME Corp",
    "website": "https://acme.com",
    "industry": "Technology",
    "size": "51-200",
    "address": "123 Main St",
    "city": "San Francisco",
    "country": "USA",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### Create Company

```http
POST /api/v1/contacts/api/companies/
```

**Request:**
```json
{
  "name": "New Company",
  "website": "https://newcompany.com",
  "industry": "Healthcare",
  "size": "11-50",
  "address": "456 Oak Ave",
  "city": "New York",
  "country": "USA"
}
```

## Tag Management

### List Tags

```http
GET /api/v1/contacts/api/tags/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "VIP",
    "color": "#ff0000",
    "description": "Very important contacts"
  }
]
```

### Create Tag

```http
POST /api/v1/contacts/api/tags/
```

**Request:**
```json
{
  "name": "Hot Lead",
  "color": "#ff6600",
  "description": "High-priority leads"
}
```

## Tenant Validation

### Validate Tenant

```http
GET /api/v1/tenants/validate/{subdomain}/
```

**Response:**
```json
{
  "valid": true,
  "tenant": {
    "schema_name": "acme",
    "name": "ACME Corp"
  }
}
```

## Demo Requests

### Submit Demo Request

```http
POST /api/v1/demo/requests/
```

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@company.com",
  "company": "Company Inc",
  "message": "Interested in a demo"
}
```

## Error Responses

### Standard Error Format

```json
{
  "error": "Error message",
  "details": {
    "field": ["Field-specific error"]
  }
}
```

### Common Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Server Error

## Rate Limiting

- **Authentication:** 5 requests per minute per IP
- **API calls:** 100 requests per minute per user
- **Demo requests:** 3 requests per hour per IP
