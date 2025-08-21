# ClientIQ

A modern multi-tenant CRM application built with Django and React.

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker (for database)

### Setup

1. **Clone and setup environment**
   ```bash
   git clone <repo-url>
   cd ClientIQ
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. **Start database**
   ```bash
   docker-compose up -d db
   ```

3. **Setup database**
   ```bash
   cd backend
   python manage.py migrate
   python manage.py seed
   ```

   *Optional: To reset and recreate the database:*
   
   ```bash
   python manage.py reset
   ```

4. **Start development servers**
   ```bash
   # From project root
   npm run dev
   ```

5. **Access the application**
   - Main site: <http://localhost:5173>
   - Tenant example: <http://acme.localhost:5173>
   - Login with: admin@acme.com / admin123

## Default Tenants

- **ACME Corp**: `acme.localhost:5173` (admin@acme.com / admin123)
- **Demo Company**: `demo.localhost:5173` (admin@demo.com / admin123)

## Project Structure

See [docs/architecture.md](docs/architecture.md) for detailed documentation.

## Features

- Multi-tenant architecture
- User management with RBAC
- Contact management
- Modern React UI with dark theme
- JWT authentication
- RESTful API

## Development

- Backend: Django 5.2 + DRF + PostgreSQL
- Frontend: React 18 + Vite + Tailwind CSS
- Database: PostgreSQL with django-tenants
