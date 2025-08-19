# ClientIQ Wiki

Welcome to the comprehensive documentation for **ClientIQ** - an enterprise multi-tenant SaaS platform.

## 📚 Documentation Overview

### Quick Start
- [⚡ README](../README.md) - Fast setup and overview
- [🚀 Development Workflow](development.md) - 5-minute setup guide

### Architecture & Design
- [🏗️ Architecture Deep Dive](architecture.md) - Multi-tenant design patterns
- [🧪 Testing Strategy](testing.md) - Progressive testing approach
- [🏢 Multi-Tenant Setup](multi-tenant.md) - Schema isolation guide

### Development & Deployment
- [⚡ Development Workflow](development.md) - Daily development practices
- [🔌 API Documentation](api.md) - REST API reference
- [🚀 Deployment Guide](deployment.md) - Production deployment

## 🎯 Quick Navigation

### For New Developers
1. **Start Here**: [README Quick Start](../README.md#quick-start-for-developers)
2. **Understand Architecture**: [Architecture Overview](architecture.md#overview)
3. **Learn Testing**: [Working Tests Philosophy](testing.md#the-working-tests-approach)
4. **Daily Workflow**: [Development Guide](development.md#daily-development-workflow)

### For System Administrators
1. **Deployment**: [Production Setup](deployment.md#quick-production-deployment)
2. **Multi-Tenant Config**: [Tenant Management](multi-tenant.md#setting-up-multi-tenancy)
3. **Security**: [Production Security](deployment.md#security-hardening)
4. **Monitoring**: [Health Checks](deployment.md#monitoring-and-logging)

### For API Consumers
1. **Authentication**: [JWT Setup](api.md#authentication)
2. **User Management**: [User API](api.md#user-management-api)
3. **Error Handling**: [Error Responses](api.md#error-handling)
4. **SDKs**: [Code Examples](api.md#sdk-examples)

## 🔧 Key Concepts

### Multi-Tenant Architecture
ClientIQ uses **schema-based isolation** where each tenant gets a completely separate PostgreSQL schema. This provides:
- ✅ **Complete data isolation**
- ✅ **Automatic tenant routing** 
- ✅ **Scalable performance**
- ✅ **Security by design**

### Progressive Testing
The **Working Tests** approach ensures:
- ✅ **43 reliable tests** with 100% success rate
- ✅ **Fast feedback loop** (~4.5 seconds)
- ✅ **CI/CD stability** 
- ✅ **Developer confidence**

### Production Ready
Built for enterprise deployment with:
- ✅ **Docker containerization**
- ✅ **Horizontal scaling**
- ✅ **SSL/TLS security**
- ✅ **Automated backups**

## 🛠️ Development Tools

### Essential Commands
```bash
# Setup development environment
python manage.py setup_simple     # Create ACME tenant
python manage.py simple_seed      # Seed sample users
python run_working_tests.py       # Validate setup

# Daily development
python manage.py runserver        # Backend server
npm run dev                       # Frontend server (in frontend/)
python run_working_tests.py       # Quick validation
```

### Project Structure
```text
ClientIQ/
├── backend/
│   ├── apps/                    # Django applications
│   ├── config/                  # Settings & configuration
│   ├── run_working_tests.py     # Curated test runner
│   └── manage.py
├── frontend/
│   ├── src/                     # Next.js application
│   └── package.json
├── docs/                        # This documentation
├── docker-compose.yml           # Development stack
└── README.md                    # Quick start guide
```

## 📊 Testing Overview

### Working Tests (Daily Use)
```bash
python run_working_tests.py  # 43 tests, 100% reliable
```
- **Platform Management**: 14 tests
- **User Management**: 11 tests  
- **Authentication**: 6 tests
- **Management Commands**: 12 tests

### Comprehensive Tests (Full Coverage)
```bash
python -m pytest  # All tests including experimental
```

## 🔗 External Resources

### Framework Documentation
- [Django](https://docs.djangoproject.com/) - Backend framework
- [django-tenants](https://django-tenants.readthedocs.io/) - Multi-tenancy
- [Next.js](https://nextjs.org/docs) - Frontend framework
- [Tailwind CSS](https://tailwindcss.com/docs) - Styling

### Production Tools
- [Docker](https://docs.docker.com/) - Containerization
- [PostgreSQL](https://www.postgresql.org/docs/) - Database
- [Nginx](https://nginx.org/en/docs/) - Reverse proxy
- [Let's Encrypt](https://letsencrypt.org/docs/) - SSL certificates

## 💡 Best Practices

### Development
1. **Always run working tests** before committing
2. **Use working tests for CI/CD** pipeline validation
3. **Follow multi-tenant patterns** for new features
4. **Test across tenant boundaries** to ensure isolation

### Testing
1. **Working tests must be 100% reliable**
2. **Comprehensive tests can be experimental**
3. **Test core functionality first**
4. **Keep tests fast and focused**

### Deployment
1. **Use Docker for consistency**
2. **Always backup before migrations**
3. **Monitor health endpoints**
4. **Implement gradual rollouts**

## 🆘 Getting Help

### Common Issues
- **Tests failing?** Check [Testing Troubleshooting](testing.md#debugging-test-failures)
- **Multi-tenant issues?** See [Tenant Troubleshooting](multi-tenant.md#troubleshooting)
- **Deployment problems?** Review [Deployment Issues](deployment.md#deployment-workflow)

### Support Channels
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive guides in this wiki
- **Code Examples**: Working implementations in the test suite

---

**Happy developing with ClientIQ!** 🚀

*This documentation is maintained alongside the codebase to ensure accuracy and completeness.*
