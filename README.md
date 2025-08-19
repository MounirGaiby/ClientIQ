# ClientIQ 🚀

**Enterprise Multi-Tenant SaaS Platform** built with Django backend and Next.js frontend. Complete tenant isolation, secure authentication, and production-ready testing infrastructure.

> 🎯 **Status**: Core functionality validated with 43 working tests (100% success rate)

## ⚡ Quick Start for Developers

```bash
# 1. Clone and setup
git clone <repo-url> && cd ClientIQ
python -m venv venv && source venv/bin/activate  # Linux/Mac
pip install -r backend/requirements.txt

# 2. Database setup  
cd backend
python manage.py migrate

# 3. Create ACME tenant with sample users
python manage.py setup_simple     # Creates tenant + domain
python manage.py simple_seed      # Seeds 4 users

# 4. Run tests (recommended for validation)
python run_working_tests.py       # 43 tests, ~4.5 seconds

# 5. Start development
python manage.py runserver        # Backend on :8000
# In another terminal:
cd ../frontend && npm install && npm run dev  # Frontend on :3000
```

**Access URLs:**
- Platform Admin: `http://localhost:8000/admin/` (superuser@acme.com / admin123)
- ACME Tenant: `http://acme.localhost:8000/` (admin@acme.com / admin123)
- Frontend: `http://localhost:3000`

## 🏗️ Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    ClientIQ Platform                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js 14)          │  Backend (Django 4.2.7)   │
│  ├─ TypeScript + Tailwind      │  ├─ Multi-tenant postgres  │
│  ├─ shadcn/ui components       │  ├─ Domain-based routing   │
│  ├─ JWT Authentication         │  ├─ Schema isolation       │
│  └─ Responsive design          │  └─ 43 tested core APIs    │
└─────────────────────────────────────────────────────────────┘

Public Schema (shared):           Tenant Schemas (isolated):
├─ Platform SuperUsers           ├─ CustomUsers (tenant-specific)
├─ Tenant Management             ├─ Business Data & Logic  
├─ Demo Requests                 ├─ Tenant Admin Interface
└─ Global Admin Interface        └─ User Permissions & Groups
```

## 🔧 Core Features

### 🏢 Multi-Tenant Architecture
- **Schema Isolation**: Complete PostgreSQL schema per tenant
- **Domain Routing**: `tenant.localhost` automatically routes to tenant schema
- **Auto-Migration**: New tenants get full database structure instantly
- **Demo-to-Tenant**: Seamless conversion from demo request to full tenant

### 🔐 Security & Authentication  
- **JWT Authentication**: Stateless, secure token-based auth
- **Tenant-Only Login**: Users can only authenticate within their tenant domain
- **Permission Filtering**: Tenants only see business-relevant permissions (10 vs 100+)
- **Admin Isolation**: Platform admins separate from tenant admins

### 👥 User Management
- **Platform SuperUsers**: Global platform administration via Django admin
- **Tenant Admins**: Full tenant control with `is_admin=True` flag  
- **Regular Users**: Role-based permissions via Django groups
- **Guest Access**: Demo requests without authentication

### 🧪 Testing Strategy
- **Working Tests**: Curated 43 tests with 100% reliability (`run_working_tests.py`)
- **Comprehensive Tests**: Full test suite including experimental/development tests
- **Fast Validation**: SQLite in-memory testing for rapid development cycles
- **Real-world Testing**: PostgreSQL integration tests for production validation

### Demo Conversion

- **Demo requests**: Stored in public schema for prospects
- **One-command conversion**: `convert_demo_to_tenant`
- **Auto-provisioning**: Creates tenant + domain + admin user
- **Permission filtering**: Excludes platform-level permissions

## Project Structure

```text
ClientIQ/
├── backend/                     # Django backend
│   ├── apps/
│   │   ├── platform/           # Platform super users (public schema)
│   │   ├── tenants/            # Tenant management
│   │   ├── demo/               # Demo requests (shared)
│   │   ├── users/              # Tenant users (per schema)
│   │   └── authentication/     # Auth middleware
│   ├── config/                 # Django settings
│   └── manage.py
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/                # App router pages
│   │   ├── components/         # Reusable components
│   │   └── lib/                # Utilities
│   └── package.json
└── README.md
```

## Setup

### Requirements

- Python 3.12+
- Node.js 18+
- PostgreSQL 13+

### Backend Installation

```bash
# Clone and setup
git clone <repository-url>
cd ClientIQ/backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Database setup
createdb clientiq_db
python manage.py migrate_schemas --shared

# Create platform admin
python manage.py shell -c "
from apps.platform.models import SuperUser
SuperUser.objects.create_superuser('admin@platform.com', 'platform123', 'Platform', 'Admin')
"

# Create demo tenant
python manage.py shell -c "
from apps.tenants.models import Tenant, Domain
tenant = Tenant.objects.create(schema_name='acme', name='ACME Corp', contact_email='admin@acme.com')
Domain.objects.create(domain='acme.localhost', tenant=tenant, is_primary=True)
"

# Setup tenant users
python manage.py tenant_command setup_simple_tenant --schema=acme
python manage.py tenant_command clean_tenant_permissions --schema=acme

# Run server
python manage.py runserver
```

### Frontend Installation

```bash
cd frontend
npm install
npm run dev
```

## Access URLs

| URL | Purpose | Users |
|-----|---------|-------|
| `http://localhost:8000/admin/` | Platform Admin | Platform SuperUsers |
| `http://localhost:8000/` | Public Schema | Demo requests, tenant management |
| `http://acme.localhost:8000/` | ACME Tenant | ACME tenant users only |
| `http://localhost:3000/` | Frontend App | All users (domain-aware) |

## Default Credentials

### Platform Access (Public Schema)

**Platform Admin**: admin@platform.com / platform123

- Django admin access
- Tenant management
- Platform configuration

### Tenant Access (ACME Schema)

**Admin**: admin@acme.com / admin123 (is_admin=True)

**Manager**: manager@acme.com / manager123

**User**: user@acme.com / user123

## Management Commands

### Tenant Operations

```bash
# Create tenant with users
python manage.py tenant_command setup_simple_tenant --schema=<schema>

# Clean tenant permissions  
python manage.py tenant_command clean_tenant_permissions --schema=<schema>

# Convert demo to tenant
python manage.py convert_demo_to_tenant <demo_id> <schema> <domain>
```

### Permission Operations

```bash
# View tenant permissions
python manage.py tenant_command shell --schema=<schema> -c "
from django.contrib.auth.models import Permission
for p in Permission.objects.all(): print(f'{p.content_type.app_label}.{p.codename}')
"
```

## Multi-Tenant Workflow

1. **Demo Request**: Prospect submits demo form → stored in public schema
2. **Demo Approval**: Platform admin reviews in Django admin
3. **Tenant Creation**: `convert_demo_to_tenant` command creates:
   - New tenant schema with all tables
   - Domain mapping (`company.localhost`)
   - Admin user with `is_admin=True`
   - Cleaned permission set (only 10 business permissions)
4. **User Access**: Tenant users access via `company.localhost:8000`

## Permission Architecture

### Public Schema (40+ permissions)

- Platform super user management
- Tenant CRUD operations
- Demo request management
- Django admin access
- System configuration

### Tenant Schema (10 permissions)

- `auth.add_group`, `auth.change_group`, `auth.delete_group`, `auth.view_group`
- `users.add_customuser`, `users.change_customuser`, `users.delete_customuser`, `users.view_customuser`
- `auth.view_permission`
- `contenttypes.view_contenttype`

### Permission Logic

```python
# Tenant admin check
if user.is_admin:
    return True  # Has all tenant permissions

# Regular permission check
return user.has_perm(permission)
```

## Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests  
cd frontend
npm test

# Coverage report
npm run test:coverage
```

## Development Workflow

1. **Database Changes**: Create migrations for both shared and tenant schemas
2. **Permission Updates**: Run `clean_tenant_permissions` after app changes
3. **New Tenants**: Use management commands for consistent setup
4. **Testing**: Validate both platform and tenant-level functionality

## Production Considerations

- **Database**: Use separate PostgreSQL instances for better isolation
- **Domains**: Configure real domains instead of `.localhost`
- **SSL**: Enable HTTPS for all tenant domains
- **Monitoring**: Track per-tenant resource usage
- **Backups**: Schema-aware backup strategy

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `python manage.py test` and `npm test`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for scalable multi-tenant applications**terprise Multi-Tenant SaaS Platform**

ClientIQ is a production-ready multi-tenant SaaS platform built with Django backend and Next.js frontend. It provides complete tenant isolation, clean permission architecture, and scalable demo-to-tenant conversion workflow.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ClientIQ Platform                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js 14)          │  Backend (Django 4.2.7)   │
│  ├─ TypeScript + Tailwind      │  ├─ Multi-tenant postgres  │
│  ├─ shadcn/ui components       │  ├─ Domain-based routing   │
│  └─ Responsive design          │  └─ Clean permissions     │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### 🏢 **Multi-Tenant Architecture**
- **Schema-based isolation**: Complete database separation per tenant
- **Domain routing**: `tenant.localhost` → tenant schema
- **Auto-migration**: New tenants get complete database structure
- **Demo conversion**: Seamless demo-to-tenant workflow

### 🔐 **Clean Permission System**
- **Platform level**: SuperUser model for platform administration
- **Tenant level**: Simple `is_admin` flag for tenant admins
- **Filtered permissions**: Only business-relevant permissions in tenant schemas
- **No complexity**: Removed redundant superuser/staff fields

### 👥 **User Management**
- **Platform admins**: Full platform control via Django admin
- **Tenant admins**: Complete control within their tenant (`is_admin=True`)
- **Regular users**: Role-based permissions via groups
- **Readonly users**: View-only platform access for auditing

### 🔄 **Demo-to-Tenant Conversion**
- **Demo requests**: Stored in public schema for prospects
- **One-command conversion**: `convert_demo_to_tenant`
- **Auto-provisioning**: Creates tenant + domain + admin user
- **Permission filtering**: Excludes platform-level permissions

## 🏗️ Project Structure

```
ClientIQ/
├── backend/                     # Django backend
│   ├── apps/
│   │   ├── platform/           # Platform super users (public schema)
│   │   ├── tenants/            # Tenant management
│   │   ├── demo/               # Demo requests (shared)
│   │   ├── users/              # Tenant users (per schema)
│   │   └── authentication/     # Auth middleware
│   ├── config/                 # Django settings
│   └── manage.py
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/                # App router pages
│   │   ├── components/         # Reusable components
│   │   └── lib/                # Utilities
│   └── package.json
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 13+

### Backend Setup

```bash
# Clone and setup
git clone <repository-url>
cd ClientIQ/backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Database setup
createdb clientiq_db
python manage.py migrate_schemas --shared

# Create platform admin
python manage.py shell -c "
from apps.platform.models import SuperUser
SuperUser.objects.create_superuser('admin@platform.com', 'platform123', 'Platform', 'Admin')
"

# Create demo tenant
python manage.py shell -c "
from apps.tenants.models import Tenant, Domain
tenant = Tenant.objects.create(schema_name='acme', name='ACME Corp', contact_email='admin@acme.com')
Domain.objects.create(domain='acme.localhost', tenant=tenant, is_primary=True)
"

# Setup tenant users
python manage.py tenant_command setup_simple_tenant --schema=acme
python manage.py tenant_command clean_tenant_permissions --schema=acme

# Run server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access Points

| URL | Purpose | Users |
|-----|---------|-------|
| `http://localhost:8000/admin/` | Platform Admin | Platform SuperUsers |
| `http://localhost:8000/` | Public Schema | Demo requests, tenant management |
| `http://acme.localhost:8000/` | ACME Tenant | ACME tenant users only |
| `http://localhost:3000/` | Frontend App | All users (domain-aware) |

## 👤 Default Users

### Platform Level (Public Schema)
```
🔧 Platform Admin: admin@platform.com / platform123
   - Django admin access
   - Tenant management
   - Platform configuration
```

### Tenant Level (ACME Schema)
```
🔑 Admin:    admin@acme.com / admin123    (is_admin=True)
👤 Manager:  manager@acme.com / manager123
👤 User:     user@acme.com / user123
```

## 🔧 Management Commands

### Tenant Management
```bash
# Create tenant with users
python manage.py tenant_command setup_simple_tenant --schema=<schema>

# Clean tenant permissions  
python manage.py tenant_command clean_tenant_permissions --schema=<schema>

# Convert demo to tenant
python manage.py convert_demo_to_tenant <demo_id> <schema> <domain>
```

### Permission Management
```bash
# View tenant permissions
python manage.py tenant_command shell --schema=<schema> -c "
from django.contrib.auth.models import Permission
for p in Permission.objects.all(): print(f'{p.content_type.app_label}.{p.codename}')
"
```

## 🏢 Multi-Tenant Flow

1. **Demo Request**: Prospect submits demo form → stored in public schema
2. **Demo Approval**: Platform admin reviews in Django admin
3. **Tenant Creation**: `convert_demo_to_tenant` command creates:
   - New tenant schema with all tables
   - Domain mapping (`company.localhost`)
   - Admin user with `is_admin=True`
   - Cleaned permission set (only 10 business permissions)
4. **User Access**: Tenant users access via `company.localhost:8000`

## 🔒 Permission Architecture

### Public Schema (40+ permissions)
- Platform super user management
- Tenant CRUD operations
- Demo request management
- Django admin access
- System configuration

### Tenant Schema (10 permissions)
- `auth.add_group`, `auth.change_group`, `auth.delete_group`, `auth.view_group`
- `users.add_customuser`, `users.change_customuser`, `users.delete_customuser`, `users.view_customuser`
- `auth.view_permission`
- `contenttypes.view_contenttype`

### Permission Logic
```python
# Tenant admin check
if user.is_admin:
    return True  # Has all tenant permissions

# Regular permission check
return user.has_perm(permission)
```

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests  
cd frontend
npm test

# Coverage report
npm run test:coverage
```

## � Development Workflow

1. **Database Changes**: Create migrations for both shared and tenant schemas
2. **Permission Updates**: Run `clean_tenant_permissions` after app changes
3. **New Tenants**: Use management commands for consistent setup
4. **Testing**: Validate both platform and tenant-level functionality

## 📊 Production Considerations

- **Database**: Use separate PostgreSQL instances for better isolation
- **Domains**: Configure real domains instead of `.localhost`
- **SSL**: Enable HTTPS for all tenant domains
- **Monitoring**: Track per-tenant resource usage
- **Backups**: Schema-aware backup strategy

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `python manage.py test` and `npm test`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for scalable multi-tenant applications**
- 📊 **Rich API** - RESTful API with React TypeScript integration
- 🐳 **Docker Ready** - Complete containerization support

## 🚀 Quick Start

Get ClientIQ running in under 10 minutes:

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/MounirGaiby/ClientIQ.git
cd ClientIQ

# Start with Docker
docker compose up --build

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser (optional)
docker compose exec backend python manage.py createsuperuser
```

### Option 2: Local Development

```bash
# Backend Setup
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver &  # Runs on :8000

# Frontend Setup (in new terminal)
cd ../frontend
npm install
npm run dev  # Runs on :3000
```

**🎯 Ready to go!** 
- Frontend: `http://localhost:3000` (Next.js application)
- Backend API: `http://localhost:8000` (Django API)
- Admin Panel: `http://localhost:8000/admin` (Django admin)

📖 **For detailed setup instructions, see [Deployment Guide](./docs/deployment.md)**
- Backend API: `http://localhost:8000/api/` (Django REST API)
- Admin: `http://localhost:8000/admin/` (Django admin interface)

## 📚 Documentation

**👉 [Complete Documentation](./docs/README.md)** - Everything you need to know about ClientIQ

### Quick Links

| Resource | Description |
|----------|-------------|
| [🏗️ Architecture](./docs/architecture.md) | System architecture and design patterns |
| [📡 API Documentation](./docs/api.md) | Complete API reference and examples |
| [🏢 Multi-Tenant Guide](./docs/multi-tenant.md) | Multi-tenancy implementation details |
| [🛠️ Development Guide](./docs/development.md) | Development setup and best practices |
| [🧪 Testing Guide](./docs/testing.md) | Testing strategies and implementation |
| [� Deployment Guide](./docs/deployment.md) | Production deployment instructions |

## 🛠️ Technology Stack

- **Backend:** Django 4.2.7, PostgreSQL, Redis, Celery
- **Frontend:** React, TypeScript, Modern JS
- **Authentication:** JWT with refresh tokens, MFA support
- **Infrastructure:** Docker, Nginx, Docker Compose
- **APIs:** RESTful APIs with comprehensive documentation

## 🏗️ Project Structure

```bash
ClientIQ/
├── backend/                # Django backend application
│   ├── apps/              # Django applications
│   │   ├── authentication/ # Auth system
│   │   ├── users/         # User management  
│   │   ├── tenants/       # Multi-tenancy
│   │   ├── permissions/   # RBAC system
│   │   ├── subscriptions/ # Billing & subscriptions
│   │   └── translations/  # i18n support
│   ├── config/            # Django configuration
│   └── manage.py          # Django management
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── app/          # Next.js App Router
│   │   ├── components/   # React components
│   │   └── lib/          # Frontend utilities
│   ├── public/           # Static assets
│   └── package.json      # Frontend dependencies
├── .workspace/           # Development documentation
├── docs/                 # 📚 Complete documentation
├── requirements.txt      # Python dependencies
└── docker-compose.yml   # Docker setup
```

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](./docs/development.md) for:

- 🔧 Development setup
- 📝 Coding standards
- 🧪 Testing guidelines
- 📋 Contribution process

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- 📚 **Documentation:** [Complete Documentation](./docs/README.md)
- 🐛 **Issues:** [GitHub Issues](https://github.com/MounirGaiby/ClientIQ/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/MounirGaiby/ClientIQ/discussions)

---

**Get started now!** 👉 [Development Guide](./docs/development.md)
