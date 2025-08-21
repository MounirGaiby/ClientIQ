# 🚀 Deployment

Production deployment guide for ClientIQ.

## Production Setup

### Prerequisites

- **Server:** Ubuntu 20.04+ or similar
- **Database:** PostgreSQL 13+
- **Web Server:** Nginx
- **Process Manager:** Supervisor or systemd
- **Domain:** Wildcard DNS for subdomains

### Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/clientiq
DATABASE_HOST=localhost
DATABASE_NAME=clientiq
DATABASE_USER=clientiq_user
DATABASE_PASSWORD=secure_password

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,*.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com

# Email (optional)
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=email_password
EMAIL_USE_TLS=True

# Redis (optional for caching)
REDIS_URL=redis://localhost:6379/0
```

## Docker Deployment

### Quick Docker Setup

```bash
# Clone repository
git clone <repo-url>
cd ClientIQ

# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Run migrations and seed
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yml exec backend python manage.py seed
```

### Docker Configuration

**docker-compose.prod.yml:**
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: clientiq
      POSTGRES_USER: clientiq_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://clientiq_user:secure_password@db:5432/clientiq
      - DEBUG=False
    depends_on:
      - db
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## Manual Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Create user
sudo adduser clientiq
sudo usermod -aG www-data clientiq
```

### 2. Database Setup

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE clientiq;
CREATE USER clientiq_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE clientiq TO clientiq_user;
\q
```

### 3. Application Setup

```bash
# Clone and setup
sudo -u clientiq -i
git clone <repo-url> /home/clientiq/app
cd /home/clientiq/app

# Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with production values

# Database migration
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed
```

### 4. Frontend Build

```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Build frontend
cd /home/clientiq/app/frontend
npm install
npm run build
```

### 5. Nginx Configuration

```nginx
# /etc/nginx/sites-available/clientiq
server {
    listen 80;
    server_name yourdomain.com *.yourdomain.com;
    
    # Frontend
    location / {
        root /home/clientiq/app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /home/clientiq/app/backend/staticfiles/;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/clientiq /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Process Management

**Supervisor configuration:**
```ini
# /etc/supervisor/conf.d/clientiq.conf
[program:clientiq]
command=/home/clientiq/app/venv/bin/gunicorn config.wsgi:application
directory=/home/clientiq/app/backend
user=clientiq
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/clientiq.log
environment=PATH="/home/clientiq/app/venv/bin"
```

```bash
# Start service
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start clientiq
```

## SSL Configuration

### Let's Encrypt Setup

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get wildcard certificate
sudo certbot certonly --manual --preferred-challenges=dns -d yourdomain.com -d "*.yourdomain.com"

# Update nginx configuration
sudo certbot --nginx -d yourdomain.com -d "*.yourdomain.com"
```

### SSL Nginx Config

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com *.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Rest of configuration...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com *.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl https://yourdomain.com/api/v1/auth/me/

# Database connection
sudo -u postgres psql -d clientiq -c "SELECT 1;"

# Service status
sudo supervisorctl status clientiq
sudo systemctl status nginx
```

### Log Monitoring

```bash
# Application logs
sudo tail -f /var/log/clientiq.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Database logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
sudo -u postgres pg_dump clientiq > /backups/db_$DATE.sql

# Application files backup
tar -czf /backups/app_$DATE.tar.gz /home/clientiq/app

# Keep only last 7 days
find /backups -name "*.sql" -mtime +7 -delete
find /backups -name "*.tar.gz" -mtime +7 -delete
```

### Updates

```bash
# Update application
cd /home/clientiq/app
git pull origin main

# Backend updates
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python manage.py migrate
python manage.py collectstatic --noinput

# Frontend updates
cd ../frontend
npm install
npm run build

# Restart services
sudo supervisorctl restart clientiq
sudo systemctl reload nginx
```

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_contacts_email ON contacts_contact(email);
CREATE INDEX idx_contacts_company ON contacts_contact(company_id);
CREATE INDEX idx_contacts_score ON contacts_contact(score);
```

### Caching Setup

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### CDN Setup

Configure CloudFlare or AWS CloudFront for static assets:

```nginx
# Cache static files
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
sudo -u postgres psql -l
```

**Permission errors:**
```bash
# Fix file permissions
sudo chown -R clientiq:www-data /home/clientiq/app
sudo chmod -R 755 /home/clientiq/app
```

**SSL certificate issues:**
```bash
# Renew certificates
sudo certbot renew --dry-run
sudo certbot renew
```

### Rollback Procedure

```bash
# Rollback to previous version
git checkout previous-stable-tag
# Run update procedure
# Test functionality
```
