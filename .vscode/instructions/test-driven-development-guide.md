# Test-Driven Development (TDD) Guide for ClientIQ

## Overview

This document provides comprehensive instructions for implementing Test-Driven Development (TDD) in the ClientIQ Django multi-tenant SaaS platform. Following these guidelines ensures that all new features are thoroughly tested, reducing bugs and improving code quality.

## Project Architecture

ClientIQ is a Django 4.2.7 multi-tenant SaaS platform using:
- **django-tenants** for schema-based multi-tenancy
- **Custom UserManager** for email-based authentication
- **Django REST Framework** for API endpoints
- **Comprehensive test suite** covering models, services, APIs, and integrations

## TDD Workflow

### 1. Test-First Development Cycle

Follow the **Red-Green-Refactor** cycle:

1. **RED**: Write a failing test that describes the desired functionality
2. **GREEN**: Write the minimum code to make the test pass
3. **REFACTOR**: Improve the code while keeping tests passing

### 2. Pre-Development Setup

Before starting any new feature:

```bash
# Activate virtual environment
cd /root/projects/ClientIQ
source .venv/bin/activate

# Ensure all existing tests pass
python manage.py test

# Check for any syntax errors
python manage.py check
```

### 3. Development Environment

- **Python**: 3.12.3
- **Django**: 4.2.7
- **Virtual Environment**: `/root/projects/ClientIQ/.venv/`
- **Database**: PostgreSQL with schema-based tenancy

## Test Organization

### Test File Structure

Tests are organized in `apps/{app_name}/tests.py` files:

```
apps/
├── users/
│   ├── tests.py          # User model, service, API, and integration tests
├── tenants/
│   ├── tests.py          # Tenant management tests
├── permissions/
│   ├── tests.py          # Permission system tests
└── ...
```

### Test Categories

1. **Model Tests**: Validate model behavior, constraints, and relationships
2. **Service Tests**: Test business logic and service layer functionality
3. **API Tests**: Verify REST API endpoints and responses
4. **Integration Tests**: Test component interactions and workflows
5. **Admin Tests**: Validate Django admin interface functionality

## Multi-Tenant Testing Patterns

### Schema Context Management

Always use `schema_context` for tenant-specific operations:

```python
from django_tenants.utils import schema_context

# Test setup with tenant context
def setUp(self):
    self.tenant = Tenant.objects.create(
        schema_name='test_tenant',
        name='Test Tenant'
    )
    
# Use schema context for tenant operations
with schema_context(self.tenant.schema_name):
    user = TenantUser.objects.create(email='test@example.com')
```

### Authentication in Multi-Tenant Tests

For API tests requiring authentication:

```python
def test_api_endpoint(self):
    with schema_context(self.tenant.schema_name):
        user = TenantUser.objects.create(email='test@example.com')
        # Wrap force_login with schema context
        with schema_context(self.tenant.schema_name):
            self.client.force_login(user)
        
        response = self.client.get('/api/endpoint/')
        self.assertEqual(response.status_code, 200)
```

## Writing Effective Tests

### 1. Test Naming Convention

Use descriptive test names that explain the scenario:

```python
def test_create_user_with_valid_email_succeeds(self):
    """Test that creating a user with valid email succeeds."""
    
def test_create_user_with_duplicate_email_raises_error(self):
    """Test that creating a user with duplicate email raises ValueError."""
    
def test_api_requires_authentication(self):
    """Test that API endpoint requires authentication."""
```

### 2. Test Structure (Arrange-Act-Assert)

```python
def test_user_creation(self):
    # Arrange
    user_data = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    # Act
    with schema_context(self.tenant.schema_name):
        user = TenantUser.objects.create(**user_data)
    
    # Assert
    self.assertEqual(user.email, 'test@example.com')
    self.assertTrue(user.is_active)
```

### 3. Exception Testing

Test error conditions using `assertRaises`:

```python
def test_duplicate_email_raises_error(self):
    """Test that duplicate email raises ValueError."""
    user_data = {'email': 'duplicate@example.com'}
    
    # Create first user
    with schema_context(self.tenant.schema_name):
        TenantUser.objects.create(**user_data)
    
    # Attempt to create duplicate should raise error
    with self.assertRaises(ValueError) as context:
        UserManagementService.create_tenant_admin_user(self.tenant, user_data)
    
    self.assertIn('already exists', str(context.exception))
```

## Test Execution Commands

### Running All Tests

```bash
# Run all tests
python manage.py test

# Run tests with verbose output
python manage.py test --verbosity=2

# Run tests with coverage (if coverage installed)
coverage run --source='.' manage.py test
coverage report
```

### Running Specific Tests

```bash
# Run tests for specific app
python manage.py test apps.users

# Run specific test class
python manage.py test apps.users.tests.TenantUserModelTest

# Run specific test method
python manage.py test apps.users.tests.TenantUserModelTest.test_user_creation
```

### Test Database Management

```bash
# Create test database manually (if needed)
python manage.py test --debug-mode

# Keep test database for inspection
python manage.py test --keepdb
```

## Debugging Failed Tests

### 1. Common Multi-Tenant Issues

**Problem**: `ProgrammingError: relation does not exist`
```python
# Solution: Ensure proper schema context
with schema_context(self.tenant.schema_name):
    # Database operations here
```

**Problem**: `DatabaseError: Save with update_fields did not affect any rows`
```python
# Solution: Wrap authentication in schema context
with schema_context(self.tenant.schema_name):
    self.client.force_login(user)
```

### 2. Test Isolation Issues

**Problem**: Tests affecting each other
```python
# Solution: Use unique identifiers
def test_method(self):
    user_data = {
        'email': f'test_{uuid.uuid4()}@example.com',  # Unique email
        'first_name': 'Test'
    }
```

### 3. Debugging Test Output

```bash
# Run with maximum verbosity
python manage.py test --verbosity=3

# Use pdb for debugging
import pdb; pdb.set_trace()

# Add logging to tests
import logging
logger = logging.getLogger(__name__)
logger.info("Test checkpoint reached")
```

## Best Practices

### 1. Test Independence

- Each test should be independent and not rely on other tests
- Use `setUp()` and `tearDown()` methods for test preparation
- Avoid shared state between tests

### 2. Meaningful Assertions

```python
# Good: Specific assertions
self.assertEqual(user.email, 'expected@example.com')
self.assertTrue(user.is_active)

# Avoid: Generic assertions
self.assertTrue(user)  # Too vague
```

### 3. Mock External Dependencies

```python
from unittest.mock import patch, MagicMock

@patch('apps.common.services.permission_service.PermissionService.assign_admin_role')
def test_with_mocked_service(self, mock_assign_role):
    mock_assign_role.return_value = True
    # Test implementation
```

### 4. Test Edge Cases

- Empty data
- Invalid data formats
- Boundary conditions
- Error scenarios
- Permission restrictions

## Test-Driven Feature Development

### Step-by-Step Process

1. **Write User Story**
   ```
   As a tenant admin
   I want to create new users
   So that I can manage team access
   ```

2. **Write Failing Test**
   ```python
   def test_create_user_success(self):
       # This test will fail initially
       result = UserService.create_user(self.tenant, valid_data)
       self.assertTrue(result['success'])
   ```

3. **Implement Minimum Code**
   ```python
   class UserService:
       @staticmethod
       def create_user(tenant, data):
           # Minimal implementation to pass test
           return {'success': True}
   ```

4. **Add More Test Cases**
   ```python
   def test_create_user_invalid_email(self):
       with self.assertRaises(ValueError):
           UserService.create_user(self.tenant, invalid_data)
   ```

5. **Refactor and Improve**
   - Add proper validation
   - Implement business logic
   - Optimize performance
   - Keep tests passing

## Continuous Integration Guidelines

### Pre-Commit Checks

Before committing code:

```bash
# Run all tests
python manage.py test

# Check code style (if flake8 installed)
flake8 apps/

# Check for migrations
python manage.py makemigrations --check --dry-run

# Run security checks (if bandit installed)
bandit -r apps/
```

### Test Coverage Goals

- **Minimum**: 80% code coverage
- **Target**: 90% code coverage
- **Critical paths**: 100% coverage (authentication, payments, security)

## Troubleshooting Common Issues

### 1. Import Errors

```python
# Problem: Circular import in manager
# Solution: Use add_to_class pattern
UserManager().add_to_class(TenantUser, 'objects')
```

### 2. Migration Issues

```bash
# Check migration status
python manage.py showmigrations

# Create missing migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 3. Permission Model Location

```python
# Ensure Permission models are in SHARED_APPS
SHARED_APPS = [
    'apps.permissions',  # Must be shared across tenants
    'django_tenants',
    'apps.tenants',
]
```

## Performance Testing

### Database Query Optimization

```python
from django.test import override_settings
from django.db import connection

def test_query_count(self):
    with self.assertNumQueries(2):  # Expected query count
        # Code that should execute exactly 2 queries
        users = list(TenantUser.objects.select_related('tenant'))
```

### API Response Times

```python
import time

def test_api_performance(self):
    start_time = time.time()
    response = self.client.get('/api/users/')
    end_time = time.time()
    
    self.assertLess(end_time - start_time, 1.0)  # Should respond < 1 second
```

## Resources and Tools

### Useful Libraries

- `factory_boy`: For test data generation
- `pytest-django`: Alternative test runner
- `coverage.py`: Code coverage analysis
- `django-debug-toolbar`: Performance debugging

### VS Code Extensions

- Python Test Explorer
- Django Extension
- Coverage Gutters
- GitLens (for tracking test history)

## Conclusion

Following this TDD guide ensures:
- **High code quality** through comprehensive testing
- **Reduced bugs** in production
- **Better documentation** through descriptive tests
- **Easier refactoring** with confidence
- **Multi-tenant safety** through proper schema management

Remember: **Tests are not just about finding bugs; they're about designing better software.**

---

*Last updated: December 2024*
*Project: ClientIQ Multi-Tenant SaaS Platform*
*Django Version: 4.2.7*
