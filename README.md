# ClientIQ 🚀

**Modern Full-Stack Multi-Tenant SaaS Platform**

ClientIQ is a sophisticated full-stack platform with Django backend and Next.js frontend, designed for managing client relationships with enterprise-grade features including multi-tenancy, advanced permissions, and modern React UI.

## 🏗️ Monorepo Structure

This repository contains both backend and frontend applications:

- **Backend** (`/backend/`): Django 4.2.7 with PostgreSQL and multi-tenant architecture
- **Frontend** (`/frontend/`): Next.js 14 with TypeScript, Tailwind CSS, and shadcn/ui

## ✨ Key Features

- 🏢 **Multi-Tenant Architecture** - Schema-based tenant isolation
- 🔐 **Advanced Authentication** - JWT with MFA support
- 👥 **User Management** - Comprehensive user roles and permissions
- 💳 **Subscription Management** - Flexible billing and payment processing
- 🌍 **Internationalization** - Multi-language translation support
- 📊 **Rich API** - RESTful API with React TypeScript integration
- 🐳 **Docker Ready** - Complete containerization support

## 🚀 Quick Start

Get ClientIQ running in under 10 minutes:

```bash
# Clone the repository
git clone https://github.com/your-org/clientiq.git
cd clientiq

# Backend Setup
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_db  # Optional: Add sample data
python manage.py runserver &  # Runs on :8000

# Frontend Setup (in new terminal)
cd ../frontend
npm install
npm run dev  # Runs on :3000

# Or use Docker for everything
docker-compose up -d
```

**🎯 Ready to go!** 
- Frontend: `http://localhost:3000` (Next.js landing page)
- Backend API: `http://localhost:8000/api/` (Django REST API)
- Admin: `http://localhost:8000/admin/` (Django admin interface)

## 📚 Documentation

**👉 [Complete Documentation Wiki](./docs/README.md)** - Everything you need to know about ClientIQ

### Quick Links

| Resource | Description |
|----------|-------------|
| [🚀 Quick Start Guide](./docs/01-getting-started/quick-start.md) | Get up and running in 10 minutes |
| [🏗️ System Architecture](./docs/02-architecture/system-architecture.md) | Technical architecture and design |
| [📡 API Documentation](./docs/03-api/overview.md) | Complete API reference |
| [⚛️ React Integration](./docs/04-frontend/react-typescript.md) | Frontend integration guide |
| [🛠️ Development Guide](./docs/05-development/development.md) | Development best practices |
| [🚀 Deployment Guide](./docs/06-deployment/deployment.md) | Production deployment |
| [📖 Reference](./docs/07-reference/configuration.md) | Configuration and reference |

## 🛠️ Technology Stack

- **Backend:** Django 4.2.7, PostgreSQL, Redis, Celery
- **Frontend:** React, TypeScript, Modern JS
- **Authentication:** JWT with refresh tokens, MFA support
- **Infrastructure:** Docker, Nginx, Docker Compose
- **APIs:** RESTful APIs with comprehensive documentation

## 🏗️ Project Structure

```bash
clientiq/
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

We welcome contributions! Please see our [Development Guide](./docs/05-development/development.md) for:

- 🔧 Development setup
- 📝 Coding standards
- 🧪 Testing guidelines
- 📋 Contribution process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📚 **Documentation:** [Complete Wiki](./docs/README.md)
- 🐛 **Issues:** [GitHub Issues](https://github.com/your-org/clientiq/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/your-org/clientiq/discussions)

---

**Get started now!** 👉 [Quick Start Guide](./docs/01-getting-started/quick-start.md)
