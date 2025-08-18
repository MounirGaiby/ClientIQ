@echo off
REM ClientIQ - Development Startup Script for Windows
REM This script starts both the Django backend and Next.js frontend

echo 🚀 ClientIQ Development Startup
echo =================================

REM Get the current directory (should be project root)
set PROJECT_ROOT=%CD%

echo 📍 Starting from: %PROJECT_ROOT%

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found. Please run: python -m venv .venv
    pause
    exit /b 1
)

echo.
echo 🔧 Starting Django Backend...
cd /d "%PROJECT_ROOT%\backend"

REM Start Django in a new window
start "Django Backend" cmd /k "..\.venv\Scripts\activate && python manage.py migrate && echo ✅ Starting Django on http://localhost:8000 && python manage.py runserver 8000"

REM Wait a moment
timeout /t 3 /nobreak > nul

echo.
echo ⚛️ Starting Next.js Frontend...
cd /d "%PROJECT_ROOT%\frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    npm install
)

REM Start Next.js in a new window
start "Next.js Frontend" cmd /k "echo ✅ Starting Next.js on http://localhost:3000 && npm run dev"

echo.
echo 🎉 Both servers are starting in separate windows:
echo ==================================================
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000/api/v1/
echo Django Admin: http://localhost:8000/admin/
echo.
echo 📋 Acme Corporation Test Credentials:
echo =====================================
echo System Superuser: superadmin@clientiq.com / SuperAdmin123!
echo Tenant Admin: admin@acmecorp.com / AcmeAdmin123!
echo Regular User: mike.wilson@acmecorp.com / AcmeUser123!
echo.
echo Press any key to close this window...
pause > nul
