#!/bin/bash

# ClientIQ - Development Startup Script
# This script starts both the Django backend and Next.js frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="/root/projects/ClientIQ"

echo -e "${BLUE}🚀 ClientIQ Development Startup${NC}"
echo "================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}Killing existing processes on port $port...${NC}"
        kill -9 $pids 2>/dev/null || true
        sleep 2
    fi
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill_port 8000  # Django backend
    kill_port 3000  # Next.js frontend
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM

# Check if project directory exists
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_ROOT${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"

# Kill any existing processes on our ports
kill_port 8000
kill_port 3000

echo -e "${BLUE}📍 Starting from: $(pwd)${NC}"

# 1. Start Django Backend
echo -e "\n${BLUE}🔧 Starting Django Backend...${NC}"
cd "$PROJECT_ROOT/backend"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}❌ Virtual environment not found at $PROJECT_ROOT/.venv${NC}"
    exit 1
fi

# Activate virtual environment and start Django in background
(
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
    
    # Run migrations if needed
    echo -e "${YELLOW}🔄 Checking database migrations...${NC}"
    python manage.py migrate --verbosity=0
    
    echo -e "${GREEN}🌐 Starting Django server on http://localhost:8000${NC}"
    python manage.py runserver 8000
) &

BACKEND_PID=$!

# Wait a moment for Django to start
sleep 3

# Check if Django started successfully
if check_port 8000; then
    echo -e "${GREEN}✅ Django backend running on port 8000${NC}"
else
    echo -e "${RED}❌ Failed to start Django backend${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# 2. Start Next.js Frontend
echo -e "\n${BLUE}⚛️  Starting Next.js Frontend...${NC}"
cd "$PROJECT_ROOT/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
fi

# Start Next.js in background
(
    echo -e "${GREEN}🌐 Starting Next.js server on http://localhost:3000${NC}"
    npm run dev
) &

FRONTEND_PID=$!

# Wait a moment for Next.js to start
sleep 5

# Check if Next.js started successfully
if check_port 3000; then
    echo -e "${GREEN}✅ Next.js frontend running on port 3000${NC}"
else
    echo -e "${RED}❌ Failed to start Next.js frontend${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

# Display success message and credentials
echo -e "\n${GREEN}🎉 SUCCESS! Both servers are running:${NC}"
echo "=================================="
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}Backend API:${NC} http://localhost:8000/api/v1/"
echo -e "${BLUE}Django Admin:${NC} http://localhost:8000/admin/"

echo -e "\n${YELLOW}📋 Acme Corporation Test Credentials:${NC}"
echo "=================================="
echo -e "${BLUE}System Superuser:${NC}"
echo "  Email: superadmin@clientiq.com"
echo "  Password: SuperAdmin123!"
echo ""
echo -e "${BLUE}Acme Corp Tenant Admin:${NC}"
echo "  Email: admin@acmecorp.com"
echo "  Password: AcmeAdmin123!"
echo ""
echo -e "${BLUE}Acme Corp Users:${NC}"
echo "  Manager: sarah.johnson@acmecorp.com / AcmeManager123!"
echo "  User 1: mike.wilson@acmecorp.com / AcmeUser123!"
echo "  User 2: emily.davis@acmecorp.com / AcmeUser123!"

echo -e "\n${YELLOW}💡 Quick API Test:${NC}"
echo "curl -X POST -H \"Content-Type: application/json\" \\"
echo "  -d '{\"username\":\"acme_admin\",\"password\":\"AcmeAdmin123!\"}' \\"
echo "  http://localhost:8000/api/v1/auth/login/"

echo -e "\n${GREEN}🔄 Press Ctrl+C to stop both servers${NC}"
echo "Monitoring servers... (logs will appear below)"
echo "================================================"

# Wait for both processes and show their status
wait $BACKEND_PID $FRONTEND_PID
