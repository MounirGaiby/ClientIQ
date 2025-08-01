# 🚀 Deployment Guide

Complete guide for deploying ClientIQ to production environments, including Docker, cloud platforms, and infrastructure setup.

## 🎯 Deployment Overview

ClientIQ supports multiple deployment strategies:

- **🐳 Docker Deployment** - Containerized deployment with Docker Compose
- **☁️ Cloud Platforms** - AWS, GCP, Azure, DigitalOcean
- **🔧 Traditional VPS** - Ubuntu/CentOS server deployment
- **🚀 Platform-as-a-Service** - Heroku, Railway, Render

## 📋 Pre-Deployment Checklist

### ✅ Essential Requirements

- [ ] **Domain & SSL Certificate** configured
- [ ] **PostgreSQL Database** provisioned
- [ ] **Redis Instance** provisioned  
- [ ] **SMTP Server** configured for emails
- [ ] **File Storage** configured (S3/CloudFlare R2)
- [ ] **Environment Variables** documented
- [ ] **Database Migrations** tested
- [ ] **Static Files** collection working
- [ ] **Security Settings** reviewed

### 🔧 Infrastructure Requirements

| Component | Minimum | Recommended | Production |
|-----------|---------|-------------|------------|
| **CPU** | 1 vCPU | 2 vCPU | 4+ vCPU |
| **RAM** | 2GB | 4GB | 8GB+ |
| **Storage** | 20GB SSD | 50GB SSD | 100GB+ SSD |
| **Database** | PostgreSQL 13+ | PostgreSQL 14+ | PostgreSQL 15+ |
| **Redis** | 6.0+ | 6.2+ | 7.0+ |

## 🐳 Docker Deployment

### Quick Docker Setup

1. **Clone and Configure**
```bash
git clone https://github.com/your-org/clientiq.git
cd clientiq

# Copy and configure environment
cp .env.example .env
nano .env  # Configure your settings
```

2. **Build and Start Services**
```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Seed database (optional)
docker-compose exec web python manage.py seed_db --mode production
```

3. **Verify Deployment**
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs web

# Test API
curl http://localhost:8000/api/v1/health/
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    expose:
      - 8000
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx:/etc/nginx/conf.d
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/ssl/certs
    depends_on:
      - web
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  celery:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A config worker -l info
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
    depends_on:
      - db
      - redis
    volumes:
      - media_volume:/app/media
    restart: unless-stopped

  celery-beat:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A config beat -l info
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
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

Create `Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
```

## ☁️ AWS Deployment

### Using AWS ECS with Fargate

1. **Setup Infrastructure**
```bash
# Install AWS CLI and configure
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name clientiq-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

2. **Task Definition** (`task-definition.json`):
```json
{
  "family": "clientiq-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::YOUR-ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::YOUR-ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "clientiq-web",
      "image": "your-registry/clientiq:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DJANGO_SETTINGS_MODULE",
          "value": "config.settings.production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:ssm:region:account:parameter/clientiq/database-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:ssm:region:account:parameter/clientiq/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/clientiq",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create RDS Database**
```bash
# Create PostgreSQL RDS instance
aws rds create-db-instance \
    --db-instance-identifier clientiq-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.4 \
    --master-username clientiq \
    --master-user-password YOUR-PASSWORD \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids sg-xxxxxxxxx
```

4. **Deploy with Terraform** (Optional):

Create `main.tf`:
```hcl
provider "aws" {
  region = "us-east-1"
}

# VPC and networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "clientiq-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["us-east-1a", "us-east-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
}

# ECS Cluster
resource "aws_ecs_cluster" "clientiq" {
  name = "clientiq-cluster"
}

# RDS Database
resource "aws_db_instance" "clientiq" {
  identifier             = "clientiq-db"
  instance_class         = "db.t3.micro"
  engine                 = "postgres"
  engine_version         = "15.4"
  allocated_storage      = 20
  storage_type           = "gp2"
  
  db_name  = "clientiq"
  username = "clientiq"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.clientiq.name
  
  skip_final_snapshot = true
}

# Application Load Balancer
resource "aws_lb" "clientiq" {
  name               = "clientiq-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
}
```

## 🔧 Traditional VPS Deployment

### Ubuntu 22.04 Setup

1. **System Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx redis-server git

# Install Node.js (for frontend assets)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

2. **Database Setup**
```bash
# Setup PostgreSQL
sudo -u postgres createuser --interactive clientiq
sudo -u postgres createdb clientiq_production -O clientiq

# Set password for database user
sudo -u postgres psql -c "ALTER USER clientiq PASSWORD 'your-secure-password';"
```

3. **Application Setup**
```bash
# Create application user
sudo adduser --disabled-password --gecos '' clientiq
sudo usermod -aG sudo clientiq

# Switch to app user
sudo su - clientiq

# Clone repository
git clone https://github.com/your-org/clientiq.git
cd clientiq

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Configure production settings
```

4. **Environment Configuration** (`.env`):
```bash
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://clientiq:password@localhost:5432/clientiq_production

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True

# Storage (AWS S3)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

5. **Database Migration and Setup**
```bash
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Seed database
python manage.py seed_db --mode production
```

6. **Systemd Service Setup**

Create `/etc/systemd/system/clientiq.service`:
```ini
[Unit]
Description=ClientIQ Django Application
After=network.target

[Service]
Type=exec
User=clientiq
Group=clientiq
WorkingDirectory=/home/clientiq/clientiq
Environment=PATH=/home/clientiq/clientiq/venv/bin
EnvironmentFile=/home/clientiq/clientiq/.env
ExecStart=/home/clientiq/clientiq/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/clientiq-celery.service`:
```ini
[Unit]
Description=ClientIQ Celery Worker
After=network.target

[Service]
Type=exec
User=clientiq
Group=clientiq
WorkingDirectory=/home/clientiq/clientiq
Environment=PATH=/home/clientiq/clientiq/venv/bin
EnvironmentFile=/home/clientiq/clientiq/.env
ExecStart=/home/clientiq/clientiq/venv/bin/celery -A config worker -l info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

7. **Start Services**
```bash
# Enable and start services
sudo systemctl enable clientiq clientiq-celery
sudo systemctl start clientiq clientiq-celery

# Check status
sudo systemctl status clientiq
sudo systemctl status clientiq-celery
```

8. **Nginx Configuration**

Create `/etc/nginx/sites-available/clientiq`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Client max body size
    client_max_body_size 50M;

    # Static files
    location /static/ {
        alias /home/clientiq/clientiq/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/clientiq/clientiq/media/;
        expires 30d;
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_redirect off;
    }
}
```

9. **SSL Certificate Setup**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Enable nginx site
sudo ln -s /etc/nginx/sites-available/clientiq /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔐 Environment Configuration

### Production Settings

Create `config/settings/production.py`:

```python
from .base import *
import os
from decouple import config

# Security
DEBUG = False
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='5432'),
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)

# Static/Media files (AWS S3)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Celery configuration
CELERY_BROKER_URL = config('REDIS_URL')
CELERY_RESULT_BACKEND = config('REDIS_URL')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/clientiq/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## 📊 Monitoring & Health Checks

### Health Check Endpoint

The application includes a health check endpoint at `/api/v1/health/`:

```python
# apps/common/views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis

def health_check(request):
    """System health check endpoint"""
    status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        connection.ensure_connection()
        status['checks']['database'] = 'healthy'
    except Exception as e:
        status['checks']['database'] = f'unhealthy: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Redis check
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        status['checks']['cache'] = 'healthy'
    except Exception as e:
        status['checks']['cache'] = f'unhealthy: {str(e)}'
        status['status'] = 'unhealthy'
    
    return JsonResponse(status)
```

### Monitoring Setup

1. **Application Performance Monitoring**
```bash
# Install Sentry for error tracking
pip install sentry-sdk[django]

# Add to settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True
)
```

2. **System Monitoring with Prometheus**

Create `docker-compose.monitoring.yml`:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

## 🔄 Continuous Deployment

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
      env:
        DJANGO_SETTINGS_MODULE: config.settings.testing
    
    - name: Build Docker image
      run: |
        docker build -t clientiq:${{ github.sha }} -f Dockerfile.prod .
        docker tag clientiq:${{ github.sha }} clientiq:latest
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /home/clientiq/clientiq
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          python manage.py migrate
          python manage.py collectstatic --noinput
          sudo systemctl restart clientiq clientiq-celery
```

## 🆘 Troubleshooting

### Common Issues

**Permission Denied Errors:**
```bash
# Fix file permissions
sudo chown -R clientiq:clientiq /home/clientiq/clientiq
sudo chmod -R 755 /home/clientiq/clientiq
```

**Database Connection Issues:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
sudo -u postgres psql -c "SELECT version();"

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

**Static Files Not Loading:**
```bash
# Recollect static files
python manage.py collectstatic --clear --noinput

# Check nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

**Memory Issues:**
```bash
# Check memory usage
free -h
htop

# Optimize Gunicorn workers
# In systemd service file: --workers = (2 * CPU cores) + 1
```

## 📚 Next Steps

After successful deployment:

1. **Setup Monitoring** - Configure alerting and monitoring
2. **Performance Tuning** - Optimize database queries and caching
3. **Security Hardening** - Regular security audits and updates
4. **Backup Strategy** - Automated database and file backups
5. **Scaling Plan** - Horizontal scaling with load balancers

### Related Documentation

- [🔒 Security Best Practices](./security.md)
- [📊 Monitoring & Logging](./monitoring.md)
- [⚡ Performance Optimization](./performance.md)
- [🔧 Configuration Reference](../07-reference/configuration.md)

---

**Deployment complete!** 🎉 Your ClientIQ instance is now running in production.
