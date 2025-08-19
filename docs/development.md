# Development Workflow

## Quick Start Guide

### Fastest Path to Development

**5-Minute Setup:**

```bash
# 1. Clone and setup environment
git clone <repo-url> && cd ClientIQ
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt

# 2. Database and migrations
cd backend
python manage.py migrate

# 3. Create complete ACME tenant with users
python manage.py setup_simple  # Creates tenant + domain + superuser
python manage.py simple_seed   # Creates 4 tenant users

# 4. Validate setup with working tests
python run_working_tests.py    # Should show 43/43 tests passing

# 5. Start development servers
python manage.py runserver     # Backend: :8000
# New terminal:
cd ../frontend && npm install && npm run dev  # Frontend: :3000
```

**Immediate Access:**

- Django Admin: `localhost:8000/admin/` (superuser@acme.com / admin123)
- ACME Tenant: `acme.localhost:8000/` (admin@acme.com / admin123)
- Frontend: `localhost:3000`

### User Accounts Created

**Platform SuperUser (Global Admin)**
- Email: `superuser@acme.com`
- Password: `admin123`
- Access: Platform administration, all tenants

**ACME Tenant Users**
- Admin: `admin@acme.com / admin123` (is_admin=True, full tenant control)
- Manager: `manager@acme.com / manager123` (business user with permissions)
- User: `user@acme.com / user123` (basic tenant user)

## Development Environment

### Backend Development

**File Structure for Development:**

```text
backend/
├── apps/                     # Main application code
│   ├── authentication/      # 🔐 Auth middleware & backends
│   ├── users/               # 👥 Tenant user management
│   ├── platform/            # 👑 Platform administration
│   ├── tenants/             # 🏢 Multi-tenant management
│   └── demo/                # 🎯 Demo request system
├── config/                  # ⚙️ Django configuration
│   ├── settings/            # Environment-specific settings
│   ├── urls.py              # URL routing
│   └── wsgi.py             # WSGI application
├── run_working_tests.py     # 🧪 Reliable test runner
└── manage.py               # Django management
```

**Key Development Files:**

```bash
# Settings for development
config/settings.py              # Main development settings
config/settings_simple.py       # Simplified multi-tenant settings
config/settings_comprehensive_test.py  # Test configuration

# Essential management commands
apps/users/management/commands/
├── setup_simple.py            # Complete ACME tenant setup
├── simple_seed.py             # Seed 4 ACME users
└── clean_tenant_permissions.py # Permission cleanup

# Working tests (100% reliable)
apps/*/tests_working.py         # Curated working tests
run_working_tests.py            # Consolidated test runner
```

### Frontend Development

**Next.js 14 Setup:**

```bash
cd frontend

# Development server
npm run dev         # Hot reload on :3000

# Key directories
src/
├── app/           # Next.js 14 App Router
├── components/    # Reusable UI components
├── contexts/      # React contexts for state
└── lib/          # Utility functions
```

**Frontend Features:**
- TypeScript for type safety
- Tailwind CSS for styling
- shadcn/ui components
- JWT authentication
- Multi-tenant routing

## Daily Development Workflow

### 1. Morning Startup

```bash
# Start development environment
cd ClientIQ/backend
source ../venv/bin/activate  # or venv\Scripts\activate on Windows

# Quick health check
python run_working_tests.py  # Should pass 43/43 tests

# Start servers
python manage.py runserver   # Terminal 1: Backend
cd ../frontend && npm run dev # Terminal 2: Frontend
```

### 2. Feature Development

**Test-Driven Development (Recommended):**

```bash
# 1. Create/update working test
# Edit apps/yourapp/tests_working.py
def test_new_feature(self):
    # Write test for new functionality
    pass

# 2. Run working tests (should fail for new feature)
python run_working_tests.py

# 3. Implement feature
# Edit apps/yourapp/models.py, views.py, etc.

# 4. Run tests until they pass
python run_working_tests.py

# 5. Add to comprehensive tests if experimental
# Edit apps/yourapp/tests_comprehensive.py
```

**Development Validation:**

```bash
# Before committing any changes
python run_working_tests.py        # Must pass 43/43
python manage.py check --deploy     # Django system checks
python manage.py makemigrations     # Check for model changes
```

### 3. Database Development

**Migration Workflow:**

```bash
# Create new migrations
python manage.py makemigrations

# Apply to shared schema (public)
python manage.py migrate_schemas --shared

# Apply to all tenant schemas
python manage.py migrate_schemas --tenant

# Create new tenant (if needed)
python manage.py setup_simple --schema=newclient
```

**Database Reset (Development):**

```bash
# Nuclear option: reset everything
rm db.sqlite3  # or reset PostgreSQL database
python manage.py migrate
python manage.py setup_simple
python manage.py simple_seed
```

## Testing Workflow

### Working Tests (Daily Use)

```bash
# Standard validation
python run_working_tests.py

# Verbose output for debugging
python run_working_tests.py --verbose

# Specific app testing
python manage.py test apps.users.tests_working

# Run single test method
python manage.py test apps.users.tests_working.CustomUserModelTest.test_create_user
```

### Comprehensive Testing (Pre-Release)

```bash
# Full test suite with coverage
python -m pytest --cov=apps --cov-report=html

# View coverage report
open htmlcov/index.html  # or your browser

# Run specific comprehensive tests
python -m pytest apps/users/tests_comprehensive.py -v
```

### Adding New Tests

**To Working Tests (High Standard):**

```python
# apps/yourapp/tests_working.py
class YourFeatureTest(TestCase):
    def test_core_functionality(self):
        """Test must be 100% reliable and fast"""
        # Arrange
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Act
        result = user.get_full_name()
        
        # Assert
        self.assertEqual(result, 'Test User')
```

**To Comprehensive Tests (Experimental OK):**

```python
# apps/yourapp/tests_comprehensive.py
class ExperimentalFeatureTest(TestCase):
    def test_edge_case_scenario(self):
        """Test can be experimental or work-in-progress"""
        # Complex integration test
        # Edge case testing
        # Performance testing
        pass
```

## Multi-Tenant Development

### Working with Tenants

**Create New Tenant:**

```bash
# Option 1: Complete setup with users
python manage.py setup_simple --schema=techcorp --name="TechCorp Ltd"

# Option 2: Manual tenant creation
from apps.tenants.models import Tenant, Domain
tenant = Tenant.objects.create(
    name="TechCorp Ltd",
    schema_name="techcorp",
    contact_email="admin@techcorp.com"
)
Domain.objects.create(
    tenant=tenant,
    domain="techcorp.localhost",
    is_primary=True
)
```

**Tenant Context Development:**

```python
# Access tenant data in code
from django_tenants.utils import schema_context

# Switch to specific tenant
with schema_context('acme'):
    users = CustomUser.objects.all()  # Only ACME users
    
# Or use tenant-aware views
from django_tenants.utils import tenant_context

@tenant_context
def my_view(request):
    # Automatically in current tenant context
    users = CustomUser.objects.all()
```

### Domain Configuration

**Local Development Domains:**

```bash
# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
127.0.0.1 acme.localhost
127.0.0.1 techcorp.localhost
127.0.0.1 demo.localhost
```

**Testing Different Tenants:**

- `localhost:8000` - Public schema (platform admin)
- `acme.localhost:8000` - ACME tenant
- `techcorp.localhost:8000` - TechCorp tenant
- Frontend automatically detects tenant from URL

## API Development

### Authentication

**JWT Token Usage:**

```bash
# Get JWT token
curl -X POST http://acme.localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@acme.com", "password": "admin123"}'

# Use token in requests
curl -H "Authorization: Bearer <your-jwt-token>" \
  http://acme.localhost:8000/api/v1/users/
```

**API Endpoints:**

```text
Authentication:
POST /api/v1/auth/login/      # Login (get JWT)
POST /api/v1/auth/logout/     # Logout (blacklist token)
GET  /api/v1/auth/user/       # Current user info

Users (tenant-specific):
GET    /api/v1/users/         # List tenant users
POST   /api/v1/users/         # Create user
GET    /api/v1/users/{id}/    # User details
PUT    /api/v1/users/{id}/    # Update user
DELETE /api/v1/users/{id}/    # Delete user

Demo (public schema):
POST /api/v1/demo/requests/   # Submit demo request
```

## Debugging and Troubleshooting

### Common Issues

**Tests Failing:**

```bash
# Check working tests baseline
python run_working_tests.py

# If working tests fail, investigate immediately
python run_working_tests.py --verbose --failfast

# Check recent changes
git diff HEAD~1
```

**Database Issues:**

```bash
# Check migrations
python manage.py showmigrations

# Reset database (development only)
python manage.py reset_db  # if installed
# or manually delete and recreate

# Verify tenant schemas
python manage.py shell
>>> from apps.tenants.models import Tenant
>>> Tenant.objects.all()
```

**Multi-Tenant Issues:**

```bash
# Check tenant routing
python manage.py shell
>>> from django.test import Client
>>> client = Client(SERVER_NAME='acme.localhost')
>>> response = client.get('/')

# Verify domain configuration
>>> from apps.tenants.models import Domain
>>> Domain.objects.all()
```

### Performance Monitoring

**Development Performance:**

```bash
# Test execution time
time python run_working_tests.py

# Database query analysis
python manage.py shell
>>> from django.db import connection
>>> connection.queries  # After running operations
```

## Git Workflow

### Branch Strategy

```bash
# Feature development
git checkout -b feature/user-permissions
# Make changes
python run_working_tests.py  # Must pass
git add .
git commit -m "Add user permission system"

# Before push
python run_working_tests.py  # Final validation
git push origin feature/user-permissions
```

### Commit Standards

**Good Commit Messages:**

```bash
git commit -m "Add tenant user creation API

- Implement CustomUser model with tenant isolation
- Add JWT authentication for tenant users  
- Include working tests for user CRUD operations
- Update API documentation

Tests: 43/43 passing"
```

This workflow ensures **rapid development velocity** while maintaining **high code quality** and **reliable testing standards**.
