# 🧪 Testing

Guide for running tests and development workflows in ClientIQ.

## Quick Test Commands

```bash
# Run all backend tests
cd backend
python manage.py test

# Run specific app tests  
python manage.py test apps.users
python manage.py test apps.contacts

# Run with coverage
python -m pytest --cov=apps --cov-report=html

# Frontend tests
cd frontend
npm test
```

## Backend Testing

### Test Structure

```
backend/
├── apps/
│   ├── users/
│   │   ├── tests_working.py    # User management tests
│   │   └── test_models.py      # Model tests
│   ├── contacts/
│   │   ├── tests_working.py    # Contact/company tests
│   │   └── test_views.py       # API tests
│   └── authentication/
│       └── tests_working.py    # Auth/tenant tests
```

### Running Tests

```bash
# All tests
python manage.py test

# Specific test file
python manage.py test apps.users.tests_working

# Specific test class
python manage.py test apps.users.tests_working.UserModelTests

# Specific test method
python manage.py test apps.users.tests_working.UserModelTests.test_user_creation

# With verbosity
python manage.py test --verbosity=2

# Keep test database
python manage.py test --keepdb
```

### Test Database

Tests automatically:

- Create isolated tenant schemas
- Run migrations
- Clean up after each test
- Use separate test database

### Coverage Reports

```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run --source='apps' manage.py test
coverage report
coverage html  # Generate HTML report
```

## Frontend Testing

### Test Structure

```
frontend/src/
├── __tests__/
│   ├── components/
│   ├── pages/
│   └── api/
├── components/
│   └── ComponentName.test.tsx
└── pages/
    └── PageName.test.tsx
```

### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- ComponentName.test.tsx
```

### Test Examples

**Component Test:**
```jsx
import { render, screen } from '@testing-library/react';
import Button from '../Button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});
```

**API Test:**
```jsx
import { getUsers } from '../../api/users';

test('fetches users from API', async () => {
  const users = await getUsers();
  expect(users).toHaveLength(2);
});
```

## Integration Testing

### API Testing with Postman/Insomnia

1. Import collection from `docs/api-collection.json`
2. Set environment variables:
   - `base_url`: `http://localhost:8000`
   - `tenant_url`: `http://acme.localhost:8000`
   - `auth_token`: JWT token from login

### End-to-End Testing

```bash
# Start all services
npm run dev

# Run E2E tests (if configured)
npm run test:e2e
```

## Test Data

### Fixtures & Seeds

```bash
# Reset and seed database
python manage.py reset
python manage.py seed

# Create test tenant
python manage.py create_tenant acme "ACME Corp"
```

### Sample Test Data

**Test Users:**
- admin@acme.com / admin123
- user@acme.com / user123

**Test Companies:**
- ACME Corp (Technology)
- Demo Company (Healthcare)

**Test Contacts:**
- John Doe (ACME Corp)
- Jane Smith (Demo Company)

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Write tests first (TDD)
# Implement feature
# Run tests
python manage.py test

# Commit changes
git add .
git commit -m "Add new feature with tests"
```

### 2. Pre-commit Checks

```bash
# Run all tests
python manage.py test

# Check code style
flake8 apps/
black apps/ --check

# Frontend tests
cd frontend && npm test
```

### 3. CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run tests
        run: cd backend && python manage.py test
  
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Run tests
        run: cd frontend && npm test
```

## Debugging Tests

### Backend Debugging

```python
# Add debugging to tests
import pdb; pdb.set_trace()

# Or use pytest debugging
python -m pytest apps/users/tests_working.py::UserModelTests::test_user_creation -s --pdb
```

### Database Inspection

```bash
# Access test database
python manage.py dbshell --database=test

# View test data
python manage.py shell
>>> from apps.users.models import CustomUser
>>> CustomUser.objects.all()
```

### Frontend Debugging

```jsx
// Debug component in test
import { screen, debug } from '@testing-library/react';

test('debug component', () => {
  render(<Component />);
  debug(); // Prints DOM to console
});
```

## Performance Testing

### Backend Load Testing

```bash
# Install locust
pip install locust

# Run load tests
locust -f load_tests.py --host=http://localhost:8000
```

### Frontend Performance

```bash
# Lighthouse CI
npm install -g @lhci/cli
lhci autorun
```

## Continuous Testing

### Watch Mode

```bash
# Backend: Install pytest-watch
pip install pytest-watch
ptw -- apps/

# Frontend: Already included
npm test -- --watch
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Manual run
pre-commit run --all-files
```
