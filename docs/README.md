# ClientIQ Documentation

Welcome to the ClientIQ documentation. This multi-tenant CRM application is built with Django (backend) and React (frontend).

## Quick Navigation

- [🚀 Getting Started](./getting-started.md) - Setup and run the application
- [🏗️ Architecture](./architecture.md) - System design and multi-tenant setup
- [🔗 API Reference](./api.md) - Complete API endpoints and parameters
- [🧪 Testing](./testing.md) - Running tests and development workflows
- [🚀 Deployment](./deployment.md) - Production deployment guide

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd ClientIQ
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Start database
docker-compose up -d db

# Setup and seed database
cd backend
python manage.py migrate
python manage.py seed

# Start development servers
cd ..
npm run dev
```

**Access:** <http://acme.localhost:5173> (admin@acme.com / admin123)
**Access:** <http://localhost:8000/admin> (admin@platform.com / platform123)

## Tech Stack

- **Backend:** Django 5.2, DRF, PostgreSQL, JWT Auth
- **Frontend:** React 18, Vite, Tailwind CSS
- **Database:** PostgreSQL with django-tenants
- **Auth:** JWT with multi-tenant context
