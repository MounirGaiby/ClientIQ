# 🚀 Getting Started

This guide will help you set up ClientIQ for development in minutes.

## Prerequisites

- **Python 3.12+** with pip
- **Node.js 18+** with npm
- **Docker** for database
- **Git** for version control

## Setup Steps

### 1. Clone & Environment

```bash
git clone <repo-url>
cd ClientIQ

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Database Setup

```bash
# Start PostgreSQL with docker
docker-compose up -d db

# Run migrations and seed data
cd backend
python manage.py migrate
python manage.py seed
```

### 3. Start Development

```bash
# From project root - starts both backend and frontend
npm run dev
```

## Access Points

- **Main App:** <http://localhost:5173>
- **ACME Tenant:** <http://acme.localhost:5173>
- **Demo Tenant:** <http://demo.localhost:5173>

## Default Login

- **Email:** admin@acme.com
- **Password:** admin123

## Useful Commands

```bash
# Reset database (deletes all data)
cd backend
python manage.py reset

# Install frontend dependencies
npm install

# Run backend only
cd backend
python manage.py runserver

# Run frontend only
cd frontend
npm run dev
```

## Troubleshooting

**Database issues:**

```bash
docker-compose down
docker-compose up -d db
cd backend && python manage.py migrate
```

**Virtual environment activation:**

```bash
# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**Port conflicts:**

- Backend runs on `:8000`
- Frontend runs on `:5173`
- Database runs on `:5432`

## Next Steps

- Read [Architecture](./architecture.md) to understand the system
- Check [API Reference](./api.md) for endpoints
- See [Testing](./testing.md) for running tests
