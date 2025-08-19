# Architecture Deep Dive

## Overview

ClientIQ is a multi-tenant SaaS platform using **schema-based tenant isolation** with Django and PostgreSQL. Each tenant gets a completely isolated database schema while sharing the same application code.

## Multi-Tenant Architecture

### Schema Separation

```text
┌─── Public Schema (shared) ───────────────────────────────────┐
│                                                               │
│  🌐 Platform Management                                      │
│  ├─ apps.platform.SuperUser     # Platform administrators   │
│  ├─ apps.tenants.Tenant        # Tenant definitions         │
│  ├─ apps.tenants.Domain        # Domain mappings            │
│  ├─ apps.demo.DemoRequest      # Pre-tenant demo requests   │
│  └─ Django Admin Interface     # Platform administration    │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌─── Tenant Schema: "acme" ────────────────────────────────────┐
│                                                               │
│  🏢 ACME Corporation                                         │
│  ├─ apps.users.CustomUser      # ACME tenant users          │
│  ├─ Business Models            # Tenant-specific data       │
│  ├─ User Groups & Permissions  # Tenant access control      │
│  └─ Tenant Admin Interface     # Business administration    │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌─── Tenant Schema: "techcorp" ─────────────────────────────────┐
│                                                               │
│  🏢 TechCorp Ltd                                             │
│  ├─ apps.users.CustomUser      # TechCorp tenant users      │
│  ├─ Business Models            # Completely isolated data   │
│  ├─ User Groups & Permissions  # Independent access control │
│  └─ Tenant Admin Interface     # Business administration    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Domain-Based Routing

ClientIQ uses `django-tenants` for automatic tenant resolution:

1. **Request**: User visits `acme.localhost:8000`
2. **Middleware**: `TenantMainMiddleware` extracts subdomain `acme`
3. **Resolution**: Looks up `Domain` record pointing to `Tenant` with schema `acme`
4. **Context**: Sets PostgreSQL `search_path` to `acme` schema
5. **Processing**: All queries automatically use tenant schema

## Application Architecture

### App Organization

```text
apps/
├── authentication/     # 🔐 Multi-tenant authentication
│   ├── middleware.py  # Tenant-aware auth middleware
│   ├── backends.py    # Custom authentication backends
│   └── views.py       # JWT login/logout endpoints
│
├── common/            # 🔧 Shared utilities
│   ├── models.py      # Abstract base models
│   └── utils.py       # Common helper functions
│
├── demo/              # 🎯 Demo request system (public schema)
│   ├── models.py      # DemoRequest model
│   ├── views.py       # Demo submission API
│   └── admin.py       # Platform admin interface
│
├── permissions/       # 🛡️ Permission management (shared)
│   ├── models.py      # Custom permission models
│   └── utils.py       # Permission filtering utilities
│
├── platform/          # 👑 Platform administration (public schema)
│   ├── models.py      # SuperUser model
│   ├── admin.py       # Django admin configuration
│   └── managers.py    # Platform user managers
│
├── tenants/           # 🏢 Tenant management (public schema)
│   ├── models.py      # Tenant & Domain models
│   ├── admin.py       # Tenant administration
│   └── views.py       # Tenant API endpoints
│
└── users/             # 👥 Tenant user management (tenant schemas)
    ├── models.py      # CustomUser model
    ├── views.py       # User CRUD API
    ├── serializers.py # User data serialization
    └── managers.py    # Tenant user managers
```

### User Model Strategy

ClientIQ uses **separate user models** for different contexts:

**Platform Users (Public Schema)**

```python
# apps/platform/models.py
class SuperUser(AbstractUser):
    """Platform administrators with global access"""
    username = None  # Email-based authentication
    email = models.EmailField(unique=True)
    
    # Platform-specific fields
    can_create_tenants = models.BooleanField(default=True)
    platform_role = models.CharField(max_length=50)
    
    USERNAME_FIELD = 'email'
```

**Tenant Users (Tenant Schemas)**

```python
# apps/users/models.py  
class CustomUser(AbstractUser):
    """Tenant-specific users with business focus"""
    username = None  # Email-based authentication
    email = models.EmailField(unique=True)
    
    # Simplified tenant admin flag
    is_admin = models.BooleanField(default=False)
    
    # Business fields
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    USERNAME_FIELD = 'email'
```

### Settings Architecture

ClientIQ uses **modular settings** for different environments:

```text
config/settings/
├── base.py          # Shared settings
├── development.py   # Local development
├── production.py    # Production deployment
├── testing.py       # Test environment
└── docker.py        # Docker container settings
```

**Key Configuration Patterns:**

```python
# Multi-tenant app separation
SHARED_APPS = [
    'django_tenants',
    'apps.tenants',     # Tenant management
    'apps.demo',        # Demo requests
    'apps.platform',    # Platform users
]

TENANT_APPS = [
    'apps.users',       # Tenant users
    'apps.permissions', # Business permissions
    # Business logic apps
]

# Custom user model (platform)
AUTH_USER_MODEL = 'platform.SuperUser'

# Tenant routing
TENANT_MODEL = 'tenants.Tenant'
TENANT_DOMAIN_MODEL = 'tenants.Domain'
```

## Authentication & Authorization

### Multi-Level Authentication

**1. Platform Level (Public Schema)**

- **Users**: Platform SuperUsers
- **Access**: Django admin, tenant management
- **Authentication**: Email + password, Django sessions
- **Permissions**: Full platform control

**2. Tenant Level (Tenant Schemas)**

- **Users**: Tenant CustomUsers
- **Access**: Business functionality within tenant
- **Authentication**: JWT tokens, tenant-aware
- **Permissions**: Filtered business permissions only

### JWT Implementation

```python
# Tenant-aware JWT authentication
class TenantJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        # Get user within current tenant context
        with schema_context(self.request.tenant.schema_name):
            return super().get_user(validated_token)
```

### Permission Filtering

Tenant users only see **business-relevant permissions**:

```python
# Filtered permissions (10 vs 100+)
TENANT_PERMISSIONS = [
    'users.add_customuser',
    'users.change_customuser', 
    'users.delete_customuser',
    'users.view_customuser',
    # Business model permissions only
]

# Hidden from tenants
PLATFORM_PERMISSIONS = [
    'auth.add_permission',      # Meta-permissions
    'contenttypes.*',           # Content type management
    'admin.*',                  # Django admin
]
```

## Data Flow

### Demo to Tenant Conversion

```text
1. Demo Request (Public Schema)
   ├─ User submits demo form
   ├─ DemoRequest created in public schema
   └─ Platform admin reviews

2. Tenant Creation
   ├─ Platform admin approves demo
   ├─ `convert_demo_to_tenant` command executed
   ├─ New schema created with full table structure
   ├─ Domain mapping established
   └─ Tenant admin user created

3. User Access
   ├─ Tenant users visit tenant.domain.com
   ├─ Automatic schema routing
   ├─ JWT authentication within tenant context
   └─ Business functionality available
```

### Request Lifecycle

```text
1. Request: acme.localhost:8000/api/users/
   
2. Middleware Chain:
   ├─ TenantMainMiddleware → Set tenant context (schema: 'acme')
   ├─ AuthenticationMiddleware → Authenticate user
   ├─ TenantAuthenticationMiddleware → Validate user in tenant
   └─ CorsMiddleware → Handle CORS

3. View Processing:
   ├─ All database queries use 'acme' schema
   ├─ User permissions filtered to business scope
   ├─ Business logic executed
   └─ Response serialized

4. Response: User data from 'acme' schema only
```

## Database Design

### Schema Structure

Each tenant schema contains **identical table structure**:

```sql
-- Schema: public (shared)
CREATE SCHEMA public;
CREATE TABLE tenants_tenant (...);
CREATE TABLE tenants_domain (...);
CREATE TABLE platform_superuser (...);
CREATE TABLE demo_demorequest (...);

-- Schema: acme (tenant)  
CREATE SCHEMA acme;
CREATE TABLE users_customuser (...);
CREATE TABLE auth_group (...);
CREATE TABLE auth_permission (...);
-- Business model tables

-- Schema: techcorp (tenant)
CREATE SCHEMA techcorp;
CREATE TABLE users_customuser (...);
CREATE TABLE auth_group (...);
CREATE TABLE auth_permission (...);
-- Business model tables (completely isolated)
```

### Migration Strategy

```python
# Tenant migrations apply to ALL tenant schemas
python manage.py migrate_schemas --tenant

# Shared migrations apply to public schema only
python manage.py migrate_schemas --shared

# New tenant gets full structure automatically
python manage.py create_tenant_schema acme
```

## Scalability Considerations

### Database Performance

- **Schema Isolation**: No cross-tenant queries possible
- **Connection Pooling**: Shared connection pool across schemas
- **Indexing**: Per-tenant indexes for optimal performance
- **Backup Strategy**: Schema-level backup granularity

### Application Performance

- **Tenant Caching**: Cache keys include tenant context
- **Static Files**: Shared across all tenants
- **Media Files**: Tenant-specific media organization
- **Session Management**: Tenant-aware session handling

### Security Benefits

- **Data Isolation**: Impossible to access other tenant data
- **Permission Isolation**: Tenant permissions cannot escalate
- **Admin Separation**: Platform vs tenant admin boundaries
- **Audit Trails**: Tenant-specific audit logging

This architecture provides **enterprise-grade multi-tenancy** with complete data isolation, scalable performance, and maintainable security boundaries.
