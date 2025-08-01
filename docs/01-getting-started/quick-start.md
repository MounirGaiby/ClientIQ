# 🚀 Quick Start Guide

Get ClientIQ up and running in under 10 minutes! This guide will walk you through the fastest way to set up a local development environment.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** and **npm/yarn** (for frontend development)
- **PostgreSQL 13+** running locally
- **Redis 6+** running locally
- **Git** installed

## 🏃‍♂️ Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/clientiq.git
cd clientiq
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Required settings:
# - DATABASE_URL=postgresql://username:password@localhost:5432/clientiq_db
# - REDIS_URL=redis://localhost:6379/0
# - SECRET_KEY=your-secret-key-here
```

### 4. Set Up Database

```bash
# Create database
createdb clientiq_db

# Run migrations
python manage.py migrate

# Seed the database with sample data
python manage.py seed_db --mode development
```

### 5. Start the Development Server

```bash
# Start Django development server
python manage.py runserver
```

🎉 **Your API is now running at `http://localhost:8000`!**

## 🌐 Frontend Setup (Optional)

If you want to run the full-stack application:

### 1. Set Up Frontend Environment

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### 2. Configure Frontend Environment

```bash
# Copy frontend environment template
cp .env.example .env.local

# Edit .env.local with your API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Start Frontend Development Server

```bash
npm run dev
# or
yarn dev
```

🎉 **Your frontend is now running at `http://localhost:3000`!**

## 🎯 Quick Test

### Test the API

```bash
# Check API health
curl http://localhost:8000/api/v1/health/

# Create a demo request
curl -X POST http://localhost:8000/api/v1/demo/ \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@testcompany.com",
    "message": "Interested in a demo"
  }'
```

### Login to Admin Panel

1. Open `http://localhost:8000/admin/`
2. Login with the superuser credentials created during seeding:
   - **Email:** `admin@clientiq.com`
   - **Password:** `admin123`

## 🏢 Multi-Tenant Testing

The seeded database includes sample tenants:

- **Tenant 1:** `sample1.localhost` 
- **Tenant 2:** `sample2.localhost`
- **Tenant 3:** `sample3.localhost`

To test multi-tenancy locally:

1. Add entries to your `/etc/hosts` file:
   ```
   127.0.0.1 sample1.localhost
   127.0.0.1 sample2.localhost
   127.0.0.1 sample3.localhost
   ```

2. Access tenant-specific URLs:
   - `http://sample1.localhost:8000/api/v1/`
   - `http://sample2.localhost:8000/api/v1/`

Each tenant has its own data and user base!

## 🛠️ Development Tools

### Useful Commands

```bash
# Create a new tenant
python manage.py create_tenant \
  --name "Your Company" \
  --domain your-company.localhost \
  --schema your_company

# Run tests
python manage.py test

# Check code style
flake8 .
black --check .

# Generate API documentation
python manage.py spectacular --file schema.yml
```

### Database Management

```bash
# Reset database (⚠️ DESTROYS ALL DATA)
python manage.py flush
python manage.py seed_db --mode development --force

# Backup database
pg_dump clientiq_db > backup.sql

# Restore database
psql clientiq_db < backup.sql
```

## 🔧 IDE Setup

### VS Code Extensions

Install these recommended extensions:

- Python
- Django
- GitLens
- REST Client
- Docker
- PostgreSQL

### PyCharm Setup

1. Open the project in PyCharm
2. Configure Python interpreter to use `.venv/bin/python`
3. Mark `apps` directory as Sources Root
4. Configure Django settings: `config.settings.local`

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error:**
- Ensure PostgreSQL is running: `sudo service postgresql start`
- Check database exists: `psql -l | grep clientiq`

**Migration Errors:**
- Reset migrations: `find . -path "*/migrations/*.py" -not -name "__init__.py" -delete`
- Recreate migrations: `python manage.py makemigrations`

**Import Errors:**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

**Redis Connection Error:**
- Start Redis: `sudo service redis-server start`
- Check Redis status: `redis-cli ping`

## 📚 Next Steps

Now that you have ClientIQ running, explore these resources:

- [📋 API Documentation](../03-api/overview.md) - Learn about all available endpoints
- [⚛️ React Integration](../04-frontend/react-typescript.md) - Build your frontend
- [🏛️ Architecture Overview](../02-architecture/system-architecture.md) - Understand the system design
- [🧪 Testing Guide](../05-development/testing.md) - Write comprehensive tests

## 💬 Need Help?

- 📖 Check the [FAQ](../07-reference/faq.md)
- 🐛 Report issues on [GitHub](https://github.com/your-org/clientiq/issues)
- 💬 Join our [Discord community](https://discord.gg/clientiq)

---

**⏱️ Setup Time:** ~5-10 minutes  
**✅ What's Next:** Start building your first feature!
