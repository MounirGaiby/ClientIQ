# TDD Quick Reference - ClientIQ

## Essential Commands

### Environment Setup
```bash
cd /root/projects/ClientIQ
source .venv/bin/activate
```

### Test Execution
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users

# Run with verbose output
python manage.py test --verbosity=2

# Run specific test
python manage.py test apps.users.tests.TenantUserModelTest.test_user_creation
```

### Development Workflow
```bash
# 1. Check current status
python manage.py test
python manage.py check

# 2. Write failing test
# 3. Run tests (should fail)
python manage.py test apps.users

# 4. Implement minimum code
# 5. Run tests (should pass)
python manage.py test apps.users

# 6. Refactor and repeat
```

## Multi-Tenant Test Patterns

### Basic Setup
```python
from django_tenants.utils import schema_context
from apps.tenants.models import Tenant
from apps.users.models import TenantUser

class MyTestCase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            schema_name='test_tenant',
            name='Test Tenant'
        )
```

### Schema Context Usage
```python
# For database operations
with schema_context(self.tenant.schema_name):
    user = TenantUser.objects.create(email='test@example.com')

# For API authentication
with schema_context(self.tenant.schema_name):
    self.client.force_login(user)
```

### Exception Testing
```python
with self.assertRaises(ValueError) as context:
    service.create_user(invalid_data)
self.assertIn('expected message', str(context.exception))
```

## Common Test Patterns

### Model Tests
```python
def test_model_creation(self):
    # Arrange
    data = {'field': 'value'}
    
    # Act
    with schema_context(self.tenant.schema_name):
        instance = Model.objects.create(**data)
    
    # Assert
    self.assertEqual(instance.field, 'value')
```

### Service Tests
```python
@patch('external.service.method')
def test_service_method(self, mock_method):
    # Setup mock
    mock_method.return_value = expected_result
    
    # Test service
    result = MyService.method(parameters)
    
    # Verify
    self.assertEqual(result, expected_result)
    mock_method.assert_called_once_with(parameters)
```

### API Tests
```python
def test_api_endpoint(self):
    with schema_context(self.tenant.schema_name):
        user = TenantUser.objects.create(email='test@example.com')
        with schema_context(self.tenant.schema_name):
            self.client.force_login(user)
    
    response = self.client.get('/api/endpoint/')
    self.assertEqual(response.status_code, 200)
```

## Debugging Tips

### Common Errors
```python
# ProgrammingError: relation does not exist
# Solution: Missing schema_context

# DatabaseError: Save with update_fields did not affect any rows  
# Solution: Wrap force_login with schema_context

# ValueError: User already exists
# Solution: Use unique identifiers in tests
```

### Debug Commands
```bash
# Keep test database for inspection
python manage.py test --keepdb

# Debug specific test
python manage.py test apps.users.tests.TestClass.test_method --verbosity=3

# Check migrations
python manage.py showmigrations
```

## Test Structure Template

```python
class FeatureTestCase(TenantTestCase):
    """Test cases for Feature functionality."""
    
    def setUp(self):
        """Set up test dependencies."""
        super().setUp()
        # Setup code here
    
    def test_feature_success_case(self):
        """Test successful feature operation."""
        # Arrange
        
        # Act
        
        # Assert
    
    def test_feature_error_case(self):
        """Test feature error handling."""
        with self.assertRaises(ExpectedError):
            # Code that should raise error
            pass
```

## Red-Green-Refactor Cycle

1. **🔴 RED**: Write failing test
2. **🟢 GREEN**: Make test pass with minimal code  
3. **🔵 REFACTOR**: Improve code while keeping tests green

## Best Practices Checklist

- [ ] Test names describe the scenario
- [ ] Each test is independent  
- [ ] Use schema_context for tenant operations
- [ ] Mock external dependencies
- [ ] Test both success and error cases
- [ ] Use unique identifiers to avoid conflicts
- [ ] Keep tests fast and focused
- [ ] Write tests before implementation

## Resources

- Main Guide: `.vscode/instructions/test-driven-development-guide.md`
- Django Testing: https://docs.djangoproject.com/en/4.2/topics/testing/
- Django-Tenants: https://django-tenants.readthedocs.io/
