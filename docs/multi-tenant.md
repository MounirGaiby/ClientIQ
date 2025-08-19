# Multi-Tenant Setup Guide

## Overview

ClientIQ implements **schema-based multi-tenancy** using `django-tenants`. Each tenant gets a completely isolated PostgreSQL schema while sharing the same application code and server resources.

## Tenant Architecture

### Schema Isolation

```text
Database: clientiq_db
├── Schema: public (shared)
│   ├── tenants_tenant          # Tenant definitions
│   ├── tenants_domain          # Domain mappings  
│   ├── platform_superuser      # Platform admins
│   ├── demo_demorequest        # Demo requests
│   └── django_* tables         # Django core tables
│
├── Schema: acme (tenant)
│   ├── users_customuser        # ACME users only
│   ├── auth_group             # ACME groups only
│   ├── auth_permission        # Filtered permissions
│   └── business_* tables      # ACME business data
│
└── Schema: techcorp (tenant) 
    ├── users_customuser        # TechCorp users only
    ├── auth_group             # TechCorp groups only
    ├── auth_permission        # Filtered permissions
    └── business_* tables      # TechCorp business data
```

### Domain-Based Routing

**How Requests Route to Tenants:**

```text
1. Request: https://acme.localhost:8000/api/users/
   
2. TenantMainMiddleware extracts subdomain: "acme"
   
3. Database lookup:
   Domain.objects.get(domain="acme.localhost")
   → Returns Tenant(schema_name="acme")
   
4. PostgreSQL context switch:
   SET search_path TO "acme", public;
   
5. All queries now use "acme" schema automatically
   
6. Response contains only ACME tenant data
```

## Setting Up Multi-Tenancy

### 1. Database Configuration

**PostgreSQL Setup (Production):**

```python
# config/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'clientiq_db',
        'USER': 'clientiq_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Required for django-tenants
DATABASE_ROUTERS = ['django_tenants.routers.TenantSyncRouter']
TENANT_MODEL = 'tenants.Tenant'
TENANT_DOMAIN_MODEL = 'tenants.Domain'
PUBLIC_SCHEMA_NAME = 'public'
```

**SQLite Development (Alternative):**

```python
# config/settings_simple.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Note: Limited multi-tenancy support, mainly for development
```

### 2. App Configuration

**Shared Apps (Public Schema):**

```python
SHARED_APPS = [
    'django_tenants',          # Multi-tenant framework
    'django.contrib.admin',    # Platform admin only
    'django.contrib.auth',     # Core auth framework
    'django.contrib.sessions', # Session management
    
    # Platform apps (shared across tenants)
    'apps.tenants',           # Tenant management
    'apps.demo',              # Demo requests  
    'apps.platform',          # Platform administrators
    'apps.common',            # Shared utilities
]
```

**Tenant Apps (Per-Tenant Schemas):**

```python
TENANT_APPS = [
    'django.contrib.contenttypes',  # Required for permissions
    'django.contrib.auth',          # User groups & permissions
    'django.contrib.sessions',      # Tenant sessions
    
    # Business apps (isolated per tenant)
    'apps.users',              # Tenant user management
    'apps.permissions',        # Business permissions
    # Add your business logic apps here
]

# Combined for Django
INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]
```

### 3. Middleware Configuration

**Multi-Tenant Middleware Stack:**

```python
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',  # Must be first
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.authentication.middleware.TenantAuthenticationMiddleware',  # Custom
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

## Creating Tenants

### 1. Automated Setup (Recommended)

**Complete ACME Tenant Setup:**

```bash
# Creates tenant, domain, and platform superuser
python manage.py setup_simple

# Seed with business users
python manage.py simple_seed

# Result: Fully functional ACME tenant
# Domain: acme.localhost
# Users: admin@acme.com, manager@acme.com, user@acme.com, superuser@acme.com
```

### 2. Manual Tenant Creation

**Step-by-Step Manual Process:**

```python
# 1. Create Tenant
from apps.tenants.models import Tenant, Domain

tenant = Tenant.objects.create(
    name="TechCorp Ltd",
    schema_name="techcorp",  # Must be valid PostgreSQL schema name
    contact_email="admin@techcorp.com",
    industry="Technology",
    company_size="51-200",
    plan="trial"
)

# 2. Create Domain Mapping
domain = Domain.objects.create(
    tenant=tenant,
    domain="techcorp.localhost",  # For development
    is_primary=True
)

# 3. Schema Creation (automatic)
# Django-tenants automatically creates the schema with all tables

# 4. Create Tenant Admin User
from django_tenants.utils import schema_context
from apps.users.models import CustomUser

with schema_context('techcorp'):
    admin_user = CustomUser.objects.create_user(
        email='admin@techcorp.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        is_admin=True,  # Tenant admin flag
        job_title='Administrator',
        department='Management'
    )
```

### 3. Demo-to-Tenant Conversion

**Convert Demo Request to Full Tenant:**

```bash
# 1. List demo requests
python manage.py shell
>>> from apps.demo.models import DemoRequest
>>> DemoRequest.objects.all()

# 2. Convert specific demo to tenant
python manage.py convert_demo_to_tenant --demo-id=1

# This automatically:
# - Creates tenant based on demo info
# - Sets up domain mapping
# - Creates admin user
# - Configures permissions
# - Sends notification email
```

## Domain Management

### Development Domains

**Local Development Setup:**

```bash
# Add to /etc/hosts (Linux/Mac)
sudo echo "127.0.0.1 acme.localhost" >> /etc/hosts
sudo echo "127.0.0.1 techcorp.localhost" >> /etc/hosts

# Add to C:\Windows\System32\drivers\etc\hosts (Windows)
127.0.0.1 acme.localhost
127.0.0.1 techcorp.localhost
```

**Access URLs:**

- Platform Admin: `http://localhost:8000/admin/`
- ACME Tenant: `http://acme.localhost:8000/`
- TechCorp Tenant: `http://techcorp.localhost:8000/`
- API Root: `http://tenant.localhost:8000/api/v1/`

### Production Domains

**Production Domain Configuration:**

```python
# Create production domains
Domain.objects.create(
    tenant=acme_tenant,
    domain="acme.clientiq.com",  # Production subdomain
    is_primary=True
)

# Or custom domains
Domain.objects.create(
    tenant=acme_tenant,
    domain="app.acmecorp.com",   # Customer's own domain
    is_primary=False
)
```

**DNS Configuration:**

```text
# DNS Records for Multi-Tenant Setup
*.clientiq.com     CNAME  your-server.com
acme.clientiq.com  CNAME  your-server.com  
app.acmecorp.com   CNAME  your-server.com
```

## User Management

### Platform Users vs Tenant Users

**Platform SuperUsers (Public Schema):**

```python
# apps/platform/models.py
class SuperUser(AbstractUser):
    """Global platform administrators"""
    email = models.EmailField(unique=True)
    can_create_tenants = models.BooleanField(default=True)
    platform_role = models.CharField(max_length=50)
    
    # Access: All tenants, platform configuration
    # Created via: python manage.py createsuperuser
```

**Tenant CustomUsers (Tenant Schemas):**

```python
# apps/users/models.py  
class CustomUser(AbstractUser):
    """Tenant-specific business users"""
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)  # Tenant admin flag
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    
    # Access: Current tenant only
    # Created via: Tenant admin interface or API
```

### Permission System

**Filtered Permissions for Tenants:**

```python
# Only business-relevant permissions in tenant schemas
TENANT_PERMISSIONS = [
    'users.add_customuser',
    'users.change_customuser', 
    'users.delete_customuser',
    'users.view_customuser',
    # Business model permissions
]

# Hidden from tenants
PLATFORM_PERMISSIONS = [
    'auth.add_permission',      # Meta-permissions
    'contenttypes.*',           # Content type management
    'admin.*',                  # Django admin
    'tenants.*',                # Tenant management
]
```

**Tenant Admin Setup:**

```python
# Create tenant admin user
with schema_context('acme'):
    admin = CustomUser.objects.create_user(
        email='admin@acme.com',
        password='secure_password',
        is_admin=True  # Full tenant control
    )
    
    # Grant business permissions
    from django.contrib.auth.models import Group
    admin_group = Group.objects.create(name='Tenant Admins')
    # Add filtered permissions to group
    admin.groups.add(admin_group)
```

## Migration Management

### Schema Migrations

**Shared Schema Migrations:**

```bash
# Apply to public schema only
python manage.py migrate_schemas --shared

# Affects: Tenant definitions, platform users, demo requests
```

**Tenant Schema Migrations:**

```bash
# Apply to all tenant schemas
python manage.py migrate_schemas --tenant

# Affects: All existing tenant schemas get new tables/changes
```

**New Tenant Setup:**

```bash
# New tenants automatically get complete structure
tenant = Tenant.objects.create(schema_name='newclient', ...)
# Django-tenants automatically runs all tenant migrations
```

### Migration Strategy

**Development Workflow:**

```bash
# 1. Create migration
python manage.py makemigrations users

# 2. Test on development tenant
python manage.py migrate_schemas --tenant

# 3. Verify working tests still pass
python run_working_tests.py

# 4. Production deployment
python manage.py migrate_schemas --shared    # Platform updates
python manage.py migrate_schemas --tenant    # All tenant updates
```

## Tenant Isolation Verification

### Data Isolation Testing

**Verify Complete Isolation:**

```python
# Test script to verify tenant isolation
from django_tenants.utils import schema_context
from apps.users.models import CustomUser

# Create users in different tenants
with schema_context('acme'):
    acme_user = CustomUser.objects.create_user(
        email='test@acme.com', password='test'
    )
    acme_count = CustomUser.objects.count()

with schema_context('techcorp'):
    techcorp_user = CustomUser.objects.create_user(
        email='test@techcorp.com', password='test'
    )
    techcorp_count = CustomUser.objects.count()

# Verify isolation
assert acme_count == 1    # Only sees ACME users
assert techcorp_count == 1  # Only sees TechCorp users

# Cross-tenant access should be impossible
with schema_context('acme'):
    # This should NOT see techcorp_user
    assert not CustomUser.objects.filter(email='test@techcorp.com').exists()
```

### Security Verification

**Permission Boundary Testing:**

```python
# Verify tenant users cannot access platform functions
with schema_context('acme'):
    user = CustomUser.objects.get(email='admin@acme.com')
    
    # Should NOT have these permissions
    assert not user.has_perm('tenants.add_tenant')
    assert not user.has_perm('platform.add_superuser')
    assert not user.has_perm('demo.delete_demorequest')
    
    # Should ONLY have business permissions
    assert user.has_perm('users.add_customuser')  # If admin
```

## Troubleshooting

### Common Issues

**Schema Not Found:**

```bash
# Check tenant exists
python manage.py shell
>>> from apps.tenants.models import Tenant
>>> Tenant.objects.all()

# Recreate schema if needed
>>> tenant = Tenant.objects.get(schema_name='acme')
>>> tenant.create_schema()
```

**Domain Resolution Issues:**

```bash
# Check domain mapping
>>> from apps.tenants.models import Domain
>>> Domain.objects.filter(domain='acme.localhost')

# Test domain resolution
>>> from django.test import Client
>>> client = Client(SERVER_NAME='acme.localhost')
>>> response = client.get('/')
```

**Migration Conflicts:**

```bash
# Reset tenant migrations (development only)
python manage.py migrate_schemas --tenant --fake-initial

# Or reset specific app
python manage.py migrate_schemas --tenant users zero
python manage.py migrate_schemas --tenant users
```

### Performance Monitoring

**Query Analysis:**

```python
# Monitor cross-schema queries (should be none)
from django.db import connection

with schema_context('acme'):
    users = CustomUser.objects.all()
    print(connection.queries)  # Should only query 'acme' schema
```

This multi-tenant setup provides **enterprise-grade isolation** with **scalable performance** and **maintainable architecture**.
