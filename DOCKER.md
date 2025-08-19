# Docker Setup Guide

## Prerequisites

Make sure you have Docker and Docker Compose installed:

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose-plugin

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
```

## Development Setup

1. **Create environment file:**
   ```bash
   cp .env.docker .env
   ```
   Edit `.env` with your development settings if needed.

2. **Start development environment:**
   ```bash
   docker compose up --build
   ```

3. **Run database migrations:**
   ```bash
   docker compose exec backend python manage.py migrate
   ```

4. **Create superuser (optional):**
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin

## Production Setup

1. **Create production environment file:**
   ```bash
   cp .env.prod.example .env.prod
   ```
   Edit `.env.prod` with your production settings:
   - Set `DEBUG=False`
   - Use a strong `SECRET_KEY`
   - Set proper `DATABASE_URL`
   - Configure `ALLOWED_HOSTS`

2. **Start production environment:**
   ```bash
   docker compose -f docker-compose.prod.yml up --build -d
   ```

3. **Run database migrations:**
   ```bash
   docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
   ```

4. **Collect static files:**
   ```bash
   docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
   ```

5. **Create superuser:**
   ```bash
   docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
   ```

## Environment Variables

### Development (.env.docker)
- `DEBUG=True` - Enable Django debug mode
- `SECRET_KEY=dev-secret-key` - Django secret key (change for production)
- `DATABASE_URL=postgresql://postgres:postgres@db:5432/clientiq` - Database connection
- `ALLOWED_HOSTS=localhost,127.0.0.1,backend` - Allowed hosts
- `POSTGRES_DB=clientiq` - PostgreSQL database name
- `POSTGRES_USER=postgres` - PostgreSQL username
- `POSTGRES_PASSWORD=postgres` - PostgreSQL password

### Production (.env.prod)
- `DEBUG=False` - Disable debug mode for security
- `SECRET_KEY=your-very-secure-secret-key` - Strong secret key
- `DATABASE_URL=postgresql://user:password@db:5432/clientiq` - Production database
- `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com` - Your domain
- Plus all database variables

## Common Commands

### Development
```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs

# Rebuild containers
docker compose up --build

# Execute commands in backend
docker compose exec backend python manage.py <command>

# Execute commands in frontend
docker compose exec frontend npm run <command>
```

### Production
```bash
# Start production services
docker compose -f docker-compose.prod.yml up -d

# Stop production services
docker compose -f docker-compose.prod.yml down

# View production logs
docker compose -f docker-compose.prod.yml logs

# Execute production commands
docker compose -f docker-compose.prod.yml exec backend python manage.py <command>
```

## Health Checks

The containers include health checks:
- **Backend**: Checks Django server response
- **Frontend**: Checks Next.js server response
- **Database**: Checks PostgreSQL connection

Monitor health with:
```bash
docker compose ps
```

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Frontend
  - "8001:8000"  # Backend
```

### Database Connection Issues
1. Ensure PostgreSQL container is healthy
2. Check database environment variables
3. Verify `DATABASE_URL` format

### Permission Issues
If you encounter permission issues, ensure your user is in the docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Clean Start
To completely reset the environment:
```bash
docker compose down -v  # Remove volumes
docker system prune -a  # Clean up images
docker compose up --build
```

## Security Notes

1. **Never use default credentials in production**
2. **Use strong SECRET_KEY in production**
3. **Set DEBUG=False in production**
4. **Use HTTPS in production**
5. **Regularly update dependencies**
6. **Use proper database backups**

## File Structure

```
├── docker-compose.yml          # Development setup
├── docker-compose.prod.yml     # Production setup
├── Dockerfile                  # Backend container
├── .env.docker                 # Development environment
├── .env.prod.example          # Production template
├── backend/
│   ├── Dockerfile             # If using separate backend image
│   ├── requirements.txt       # Python dependencies
│   └── config/
│       └── settings_docker.py # Docker-specific settings
└── frontend/
    ├── Dockerfile             # Frontend container
    └── next.config.ts         # Next.js configuration
```
