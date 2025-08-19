# Deployment Guide

## Overview

ClientIQ is designed for **production deployment** with Docker, supporting both single-server and distributed architectures. This guide covers deployment options from development to enterprise scale.

## Quick Production Deployment

### Docker Compose (Recommended)

**Complete production stack in minutes:**

```bash
# 1. Clone and configure
git clone <repo-url> && cd ClientIQ
cp .env.prod.example .env.prod

# 2. Configure environment
# Edit .env.prod with your production values

# 3. Deploy with SSL and production database
docker-compose -f docker-compose.prod.yml up -d

# 4. Setup initial data
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py setup_simple

# 5. Verify deployment
curl https://your-domain.com/api/v1/health/
```

**Production Access:**

- Platform Admin: `https://your-domain.com/admin/`
- Tenant Example: `https://acme.your-domain.com/`
- API Root: `https://your-domain.com/api/v1/`

## Environment Configuration

### Production Environment Variables

**Backend Configuration (.env.prod):**

```bash
# Django Core
SECRET_KEY=your-super-secret-production-key-min-50-chars
DEBUG=False
ALLOWED_HOSTS=your-domain.com,*.your-domain.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://clientiq:secure_password@db:5432/clientiq_prod
DATABASE_HOST=your-db-host.com
DATABASE_NAME=clientiq_prod
DATABASE_USER=clientiq_prod_user
DATABASE_PASSWORD=super_secure_db_password

# Redis (Caching & Sessions)
REDIS_URL=redis://redis:6379/0
CACHE_URL=redis://redis:6379/1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@your-domain.com
EMAIL_HOST_PASSWORD=email_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=ClientIQ <noreply@your-domain.com>

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Multi-tenant domains
TENANT_DOMAIN_SUFFIX=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://*.your-domain.com

# Media & Static Files (AWS S3)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=clientiq-prod-media
AWS_S3_REGION_NAME=us-east-1

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
LOG_LEVEL=INFO
```

**Frontend Configuration (.env.prod):**

```bash
# Next.js Production
NODE_ENV=production
NEXTAUTH_URL=https://your-domain.com
NEXTAUTH_SECRET=your-nextauth-secret-key

# API Configuration
NEXT_PUBLIC_API_URL=https://your-domain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://your-domain.com/ws

# Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=https://your-frontend-sentry-dsn
```

## Docker Production Setup

### Production Docker Compose

**docker-compose.prod.yml:**

```yaml
version: '3.8'

services:
  # Nginx Reverse Proxy with SSL
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    env_file: .env.prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USER}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  # Django Backend
  backend:
    build:
      context: .
      target: backend-prod
    env_file: .env.prod
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      target: production
    env_file: .env.prod
    depends_on:
      - backend
    restart: unless-stopped

  # Celery Workers (Background Tasks)
  worker:
    build:
      context: .
      target: backend-prod
    env_file: .env.prod
    command: celery -A config worker -l info
    volumes:
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    restart: unless-stopped

  # Celery Beat (Scheduled Tasks)
  beat:
    build:
      context: .
      target: backend-prod
    env_file: .env.prod
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### Production Dockerfile

**Dockerfile (Multi-stage):**

```dockerfile
# Backend Production Stage
FROM python:3.11-slim as backend-prod

# System dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY backend/ .

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]
```

**Frontend Dockerfile:**

```dockerfile
# Frontend Production
FROM node:18-alpine as frontend-build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ .
RUN npm run build

FROM node:18-alpine as production
WORKDIR /app
COPY --from=frontend-build /app/.next ./.next
COPY --from=frontend-build /app/public ./public
COPY --from=frontend-build /app/package*.json ./
COPY --from=frontend-build /app/node_modules ./node_modules

EXPOSE 3000
CMD ["npm", "start"]
```

## Nginx Configuration

### Production Nginx Config

**nginx/prod.conf:**

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name your-domain.com *.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# Main application server
server {
    listen 443 ssl http2;
    server_name your-domain.com *.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/media/;
        expires 1y;
    }

    # API routes
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend application
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health checks
    location /health/ {
        proxy_pass http://backend;
        access_log off;
    }
}
```

## Database Setup

### PostgreSQL Production

**Database Configuration:**

```sql
-- Create production database
CREATE DATABASE clientiq_prod;
CREATE USER clientiq_prod_user WITH PASSWORD 'super_secure_password';
GRANT ALL PRIVILEGES ON DATABASE clientiq_prod TO clientiq_prod_user;

-- Required for django-tenants
ALTER USER clientiq_prod_user CREATEDB;
```

**Initial Data Setup:**

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create platform superuser
docker-compose exec backend python manage.py createsuperuser

# Setup sample tenant (optional)
docker-compose exec backend python manage.py setup_simple
```

### Database Migrations

**Production Migration Strategy:**

```bash
# 1. Backup database before migrations
docker-compose exec db pg_dump -U clientiq_prod_user clientiq_prod > backup_$(date +%Y%m%d).sql

# 2. Run shared schema migrations
docker-compose exec backend python manage.py migrate_schemas --shared

# 3. Run tenant schema migrations  
docker-compose exec backend python manage.py migrate_schemas --tenant

# 4. Verify working tests in production
docker-compose exec backend python run_working_tests.py
```

## SSL/TLS Configuration

### Let's Encrypt SSL (Automated)

**Certbot Setup:**

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificates
sudo certbot --nginx -d your-domain.com -d *.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

**Docker Certbot Integration:**

```yaml
# Add to docker-compose.prod.yml
certbot:
  image: certbot/certbot
  volumes:
    - ./ssl:/etc/letsencrypt
    - ./ssl-challenge:/var/www/certbot
  command: certonly --webroot --webroot-path=/var/www/certbot --email admin@your-domain.com --agree-tos --no-eff-email -d your-domain.com -d *.your-domain.com
```

## Monitoring and Logging

### Application Monitoring

**Health Check Endpoints:**

```python
# config/urls.py
urlpatterns = [
    path('health/', health_check_view),
    path('health/db/', db_health_check),
    path('health/cache/', cache_health_check),
]

def health_check_view(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })
```

**Prometheus Metrics:**

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'clientiq-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics/'
    
  - job_name: 'clientiq-postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']
```

### Centralized Logging

**Docker Logging Configuration:**

```yaml
# In docker-compose.prod.yml
logging:
  driver: "json-file"
  options:
    max-size: "200k"
    max-file: "10"
```

**ELK Stack Integration:**

```yaml
# logging/docker-compose.logging.yml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
  environment:
    - discovery.type=single-node
  ports:
    - "9200:9200"

kibana:
  image: docker.elastic.co/kibana/kibana:7.15.0
  ports:
    - "5601:5601"
  depends_on:
    - elasticsearch

logstash:
  image: docker.elastic.co/logstash/logstash:7.15.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  depends_on:
    - elasticsearch
```

## Backup Strategy

### Automated Database Backups

**Backup Script:**

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="clientiq_prod"
DB_USER="clientiq_prod_user"

# Create backup
docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/database/
```

**Automated Backup Cron:**

```bash
# Add to crontab
0 2 * * * /path/to/backup.sh
```

### Application Data Backup

**Media Files Backup:**

```bash
# Sync to S3
aws s3 sync /var/www/media/ s3://your-backup-bucket/media/ --delete

# Or rsync to backup server
rsync -avz /var/www/media/ backup-server:/backups/media/
```

## Scaling Considerations

### Horizontal Scaling

**Load Balancer Configuration:**

```nginx
upstream backend_servers {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

upstream frontend_servers {
    server frontend1:3000;
    server frontend2:3000;
}
```

**Docker Swarm/Kubernetes:**

```yaml
# docker-compose.swarm.yml
deploy:
  replicas: 3
  placement:
    constraints:
      - node.role == worker
  resources:
    limits:
      cpus: '1'
      memory: 1G
```

### Database Scaling

**Read Replicas:**

```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'clientiq_prod',
        'HOST': 'db-master.example.com',
    },
    'replica': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'clientiq_prod',
        'HOST': 'db-replica.example.com',
    }
}

DATABASE_ROUTERS = ['path.to.ReplicaRouter']
```

## Security Hardening

### Production Security Checklist

**Django Security:**

```python
# settings/production.py

# Security middleware
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# CSRF protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
```

**System Security:**

```bash
# Firewall configuration
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# Fail2ban configuration
apt install fail2ban
systemctl enable fail2ban
```

## Deployment Workflow

### CI/CD Pipeline

**GitHub Actions (.github/workflows/deploy.yml):**

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      
      - name: Run working tests
        run: |
          cd backend
          python run_working_tests.py
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/clientiq
            git pull origin main
            docker-compose -f docker-compose.prod.yml down
            docker-compose -f docker-compose.prod.yml up -d --build
            docker-compose exec backend python manage.py migrate
            docker-compose exec backend python run_working_tests.py
```

### Zero-Downtime Deployment

**Blue-Green Deployment:**

```bash
# Deploy to staging environment
docker-compose -f docker-compose.blue.yml up -d

# Run tests on staging
docker-compose -f docker-compose.blue.yml exec backend python run_working_tests.py

# Switch traffic to new version
./switch-traffic.sh blue

# Keep old version running for rollback
sleep 300

# Remove old version
docker-compose -f docker-compose.green.yml down
```

This deployment strategy ensures **enterprise-grade reliability** with **automated scaling** and **comprehensive monitoring** for production workloads.
