# ClientIQ Development Scripts

This directory contains scripts to easily start both the Django backend and Next.js frontend for development.

## 🚀 Quick Start

### Option 1: Bash Script (Linux/macOS/WSL)
```bash
./start-dev.sh
```

### Option 2: Batch Script (Windows)
```batch
start-dev.bat
```

### Option 3: NPM Scripts (Cross-platform)
```bash
# Install concurrently (one time setup)
npm install

# Run both servers
npm run dev
```

## 📋 Available Scripts

### Bash Script (`start-dev.sh`)
- ✅ Automatically activates Python virtual environment
- ✅ Runs Django migrations
- ✅ Starts Django backend on port 8000
- ✅ Installs frontend dependencies if needed
- ✅ Starts Next.js frontend on port 3000
- ✅ Graceful shutdown with Ctrl+C
- ✅ Shows all test credentials
- ✅ Port conflict detection and cleanup

### Windows Batch (`start-dev.bat`)
- ✅ Opens Django and Next.js in separate command windows
- ✅ Automatic dependency installation
- ✅ Shows test credentials
- ✅ Windows-friendly commands

### NPM Scripts (`package.json`)
- `npm run dev` - Start both servers with concurrently
- `npm run dev:backend` - Start only Django backend
- `npm run dev:frontend` - Start only Next.js frontend
- `npm run setup` - Initial project setup
- `npm run migrate` - Run Django migrations
- `npm run seed` - Seed database with test data
- `npm run test:backend` - Run Django tests
- `npm run test:frontend` - Run Next.js tests

## 🌐 Server URLs

After starting, the following services will be available:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/
- **Django Admin**: http://localhost:8000/admin/

## 🔐 Test Credentials (Acme Corporation)

### System Superuser
- **Email**: `superadmin@clientiq.com`
- **Password**: `SuperAdmin123!`

### Tenant Admin
- **Email**: `admin@acmecorp.com`
- **Password**: `AcmeAdmin123!`

### Regular Users
- **Manager**: `sarah.johnson@acmecorp.com` / `AcmeManager123!`
- **User 1**: `mike.wilson@acmecorp.com` / `AcmeUser123!`
- **User 2**: `emily.davis@acmecorp.com` / `AcmeUser123!`

## 🧪 Quick API Test

Test authentication:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"acme_admin","password":"AcmeAdmin123!"}' \
  http://localhost:8000/api/v1/auth/login/
```

## 🛠 Prerequisites

### Backend
- Python 3.8+
- Virtual environment at `.venv/`
- Django and dependencies installed

### Frontend
- Node.js 18+
- NPM or Yarn

## 📁 Project Structure
```
ClientIQ/
├── start-dev.sh       # Linux/macOS startup script
├── start-dev.bat      # Windows startup script
├── package.json       # NPM scripts
├── backend/           # Django backend
│   ├── manage.py
│   └── requirements.txt
├── frontend/          # Next.js frontend
│   ├── package.json
│   └── next.config.ts
└── .venv/            # Python virtual environment
```

## 🔧 Troubleshooting

### Port Already in Use
The bash script automatically detects and kills processes on ports 8000 and 3000.

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Issues
```bash
cd backend
source ../.venv/bin/activate
python manage.py migrate
python manage.py setup_dev_data
```
