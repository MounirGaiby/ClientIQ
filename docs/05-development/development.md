# 🛠️ Development Guide

Complete guide for developing and contributing to ClientIQ, including setup, workflows, testing, and best practices.

## 🚀 Development Environment Setup

### Prerequisites

- **Python 3.11+** - Latest Python version
- **PostgreSQL 13+** - Database server
- **Redis 6.0+** - Caching and task queue
- **Node.js 18+** - Frontend development
- **Git** - Version control
- **Docker** (optional) - Containerized development

### Local Development Setup

1. **Clone Repository**
```bash
git clone https://github.com/your-org/clientiq.git
cd clientiq
```

2. **Python Environment Setup**
```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

3. **Database Setup**
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres createuser --interactive clientiq
sudo -u postgres createdb clientiq_dev -O clientiq
sudo -u postgres psql -c "ALTER USER clientiq PASSWORD 'dev_password';"
```

4. **Redis Setup**
```bash
# Install Redis (Ubuntu/Debian)
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

5. **Environment Configuration**
```bash
# Copy environment template
cp .env.example .env.local

# Edit configuration
nano .env.local
```

**Development Environment Variables (`.env.local`):**
```bash
# Django
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=your-dev-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://clientiq:dev_password@localhost:5432/clientiq_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (use console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# File Storage (local for development)
DEFAULT_FILE_STORAGE=django.core.files.storage.FileSystemStorage
```

6. **Database Migration & Setup**
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed database with development data
python manage.py seed_db --mode development
```

7. **Start Development Server**
```bash
# Start Django development server
python manage.py runserver

# In another terminal, start Celery worker
celery -A config worker -l info

# In another terminal, start Celery beat (optional)
celery -A config beat -l info
```

## 🏗️ Project Architecture

### Django Apps Structure

```
apps/
├── authentication/         # JWT auth, MFA, session management
├── common/                # Shared utilities, base models, exceptions
├── payments/              # Payment processing, billing integration
├── permissions/           # RBAC system, role management
├── subscriptions/         # Subscription management, plans
├── tenants/              # Multi-tenancy, domain routing
├── translations/         # i18n, language management
└── users/                # User profiles, management
```

### Key Design Patterns

**1. Multi-Tenant Architecture:**
```python
# All tenant-aware models inherit from TenantMixin
class TenantMixin(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    
    class Meta:
        abstract = True

class Project(TenantMixin):
    name = models.CharField(max_length=200)
    # Automatically isolated by tenant
```

**2. Permission System:**
```python
# Custom permission checking
class UserPermissionMixin:
    def has_tenant_permission(self, permission_codename):
        """Check if user has permission within their tenant"""
        return self.roles.filter(
            permissions__codename=permission_codename
        ).exists()
```

**3. API Design:**
```python
# Consistent API response format
class StandardResponse:
    def success(data=None, message=None):
        return {
            'success': True,
            'data': data,
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
    
    def error(message, errors=None, status_code=400):
        return {
            'success': False,
            'error': message,
            'errors': errors,
            'timestamp': timezone.now().isoformat()
        }
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/                  # Unit tests for individual components
├── integration/           # Integration tests for app interactions
├── api/                  # API endpoint tests
├── functional/           # End-to-end functional tests
└── fixtures/             # Test data fixtures
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML coverage report

# Run specific test class
python manage.py test apps.users.tests.test_models.UserModelTest

# Run with debugging
python manage.py test --debug-mode --verbosity=2
```

### Writing Tests

**Model Tests:**
```python
# apps/users/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.users.models import User
from apps.tenants.models import Tenant

class UserModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            schema_name="test_tenant"
        )
    
    def test_user_creation(self):
        """Test basic user creation"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            tenant=self.tenant
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertEqual(user.tenant, self.tenant)
    
    def test_email_validation(self):
        """Test email validation"""
        with self.assertRaises(ValidationError):
            User.objects.create_user(
                email="invalid-email",
                password="testpass123",
                tenant=self.tenant
            )
```

**API Tests:**
```python
# apps/users/tests/test_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from apps.tenants.models import Tenant

class UserAPITest(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            schema_name="test_tenant"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            tenant=self.tenant
        )
        self.client.force_authenticate(user=self.user)
    
    def test_user_list(self):
        """Test user list endpoint"""
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], "test@example.com")
```

### Test Data Management

**Using Fixtures:**
```python
# apps/users/fixtures/test_users.json
[
    {
        "model": "users.user",
        "pk": 1,
        "fields": {
            "email": "admin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "is_active": true,
            "is_staff": true
        }
    }
]

# Load fixtures in tests
class UserTestCase(TestCase):
    fixtures = ['test_users.json']
```

**Using Factory Boy:**
```python
# tests/factories.py
import factory
from apps.users.models import User
from apps.tenants.models import Tenant

class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant
    
    name = factory.Sequence(lambda n: f"Tenant {n}")
    schema_name = factory.Sequence(lambda n: f"tenant_{n}")

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    tenant = factory.SubFactory(TenantFactory)

# Usage in tests
def test_user_creation(self):
    user = UserFactory()
    self.assertIsInstance(user, User)
```

## 📝 Coding Standards

### Python Code Style

**Follow PEP 8 with these additions:**

```python
# Use type hints
def create_user(email: str, password: str, tenant: Tenant) -> User:
    """Create a new user with proper validation."""
    return User.objects.create_user(
        email=email,
        password=password,
        tenant=tenant
    )

# Docstrings for all functions/classes
class UserManager(BaseUserManager):
    """Custom user manager for tenant-aware user creation."""
    
    def create_user(self, email: str, password: str, **extra_fields) -> User:
        """
        Create and return a regular user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            **extra_fields: Additional user fields
            
        Returns:
            User: Created user instance
            
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
```

### Code Quality Tools

**Pre-commit Hooks Setup:**
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

**`.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [django-stubs]
```

### Database Migrations

**Migration Best Practices:**

```bash
# Create migration
python manage.py makemigrations app_name

# Review migration before applying
python manage.py sqlmigrate app_name 0001

# Apply migrations
python manage.py migrate

# Create empty migration for data operations
python manage.py makemigrations --empty app_name
```

**Data Migration Example:**
```python
# apps/users/migrations/0002_migrate_user_data.py
from django.db import migrations

def migrate_user_data(apps, schema_editor):
    """Migrate existing user data to new format."""
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        # Perform data transformation
        user.full_name = f"{user.first_name} {user.last_name}"
        user.save()

def reverse_migrate_user_data(apps, schema_editor):
    """Reverse the migration."""
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        user.full_name = ""
        user.save()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            migrate_user_data,
            reverse_migrate_user_data
        ),
    ]
```

## 🔧 Development Workflows

### Git Workflow

**Branch Naming:**
- `feature/user-authentication` - New features
- `bugfix/login-validation` - Bug fixes
- `hotfix/security-patch` - Critical fixes
- `docs/api-documentation` - Documentation updates

**Commit Message Format:**
```
type(scope): description

[optional body]

[optional footer]
```

**Examples:**
```bash
git commit -m "feat(auth): add JWT token refresh endpoint"
git commit -m "fix(users): resolve email validation bug"
git commit -m "docs(api): update authentication examples"
git commit -m "test(permissions): add role-based access tests"
```

### Code Review Process

**Pull Request Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
```

### Development Tools

**Django Debug Toolbar:**
```python
# config/settings/local.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }
```

**Django Extensions:**
```bash
# Install
pip install django-extensions

# Useful commands
python manage.py show_urls          # List all URLs
python manage.py shell_plus         # Enhanced shell
python manage.py graph_models       # Generate model diagrams
python manage.py runserver_plus     # Enhanced dev server
```

## 📦 Dependencies Management

### Requirements Files

**`requirements.txt` (Production):**
```txt
Django==4.2.7
django-tenants==3.5.0
djangorestframework==3.14.0
# ... production dependencies
```

**`requirements-dev.txt` (Development):**
```txt
-r requirements.txt
pytest-django==4.5.2
coverage==7.2.0
factory-boy==3.2.1
black==23.1.0
isort==5.12.0
flake8==6.0.0
# ... development dependencies
```

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade django

# Update all packages (carefully!)
pip install --upgrade -r requirements.txt

# Generate requirements from current environment
pip freeze > requirements.txt
```

## 🚀 Deployment Preparation

### Environment-Specific Settings

**Local Development:**
```python
# config/settings/local.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
```

**Testing:**
```python
# config/settings/testing.py
from .base import *

# Use in-memory database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()
```

### Performance Optimization

**Database Optimization:**
```python
# Use select_related and prefetch_related
users = User.objects.select_related('tenant').prefetch_related('roles')

# Use database indexes
class User(models.Model):
    email = models.EmailField(db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'email']),
            models.Index(fields=['created_at']),
        ]
```

**Caching Strategies:**
```python
from django.core.cache import cache

def get_user_permissions(user_id):
    cache_key = f"user_permissions_{user_id}"
    permissions = cache.get(cache_key)
    
    if permissions is None:
        permissions = list(
            User.objects.get(id=user_id).get_all_permissions()
        )
        cache.set(cache_key, permissions, 300)  # 5 minutes
    
    return permissions
```

## 📊 Monitoring & Debugging

### Logging Configuration

```python
# config/settings/base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Performance Profiling

```python
# Custom middleware for profiling
import cProfile
import pstats
from io import StringIO

class ProfilerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if 'profile' in request.GET:
            profiler = cProfile.Profile()
            profiler.enable()
            
            response = self.get_response(request)
            
            profiler.disable()
            
            # Generate profile report
            s = StringIO()
            ps = pstats.Stats(profiler, stream=s)
            ps.sort_stats('cumulative')
            ps.print_stats(20)  # Top 20 functions
            
            # Add to response
            response['X-Profile-Stats'] = s.getvalue()
            return response
        
        return self.get_response(request)
```

## 🔍 Troubleshooting Guide

### Common Issues

**1. Migration Conflicts:**
```bash
# Reset migrations (DANGEROUS - dev only)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

**2. Permission Issues:**
```bash
# Clear permission cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

**3. Tenant Schema Issues:**
```bash
# Recreate tenant schemas
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

### Debug Commands

```bash
# Check database connections
python manage.py dbshell

# Validate models
python manage.py check

# Show current settings
python manage.py diffsettings

# List all management commands
python manage.py help

# Show SQL for a migration
python manage.py sqlmigrate app_name migration_number
```

## 🤝 Contributing Guidelines

### Before Contributing

1. **Read Documentation** - Understand the architecture
2. **Set Up Environment** - Follow development setup
3. **Run Tests** - Ensure everything works
4. **Check Issues** - Look for existing issues/discussions

### Contribution Process

1. **Fork Repository**
2. **Create Feature Branch**
3. **Write Code & Tests**
4. **Update Documentation**
5. **Submit Pull Request**
6. **Address Review Feedback**
7. **Merge & Deploy**

### Code Standards

- Follow PEP 8 and project conventions
- Write comprehensive tests
- Add docstrings to all functions/classes
- Update documentation for new features
- Use type hints where appropriate

---

**Happy coding!** 🚀 This guide provides everything you need for productive ClientIQ development.
