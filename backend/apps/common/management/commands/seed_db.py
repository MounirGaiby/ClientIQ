"""
Django management command to seed the database with initial data.
Usage: python manage.py seed_db [options]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_tenants.utils import schema_context
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seed the database with initial data for development and testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            default='development',
            choices=['development', 'production', 'demo'],
            help='Seeding mode: development (full sample data), production (minimal), demo (demo purposes)'
        )
        
        parser.add_argument(
            '--tenants',
            type=int,
            default=3,
            help='Number of sample tenants to create (development mode only)'
        )
        
        parser.add_argument(
            '--skip-superuser',
            action='store_true',
            help='Skip creating superuser'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force seeding even if data already exists'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        mode = options['mode']
        force = options['force']
        
        try:
            with transaction.atomic():
                # Check if data already exists
                if not force and self._data_exists():
                    raise CommandError(
                        'Database already contains data. Use --force to override.'
                    )
                
                # Create base data (languages, permissions, etc.)
                self._create_base_data()
                
                # Create subscription plans
                self._create_subscription_plans()
                
                # Create superuser if not skipped
                if not options['skip_superuser']:
                    self._create_superuser()
                
                # Mode-specific seeding
                if mode == 'development':
                    self._seed_development_data(options)
                elif mode == 'production':
                    self._seed_production_data(options)
                elif mode == 'demo':
                    self._seed_demo_data(options)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Database seeding completed successfully in {mode} mode!')
                )
                
                # Print summary
                self._print_summary()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during seeding: {str(e)}')
            )
            raise
    
    def _data_exists(self):
        """Check if database already contains seeded data."""
        try:
            from apps.tenants.models import Tenant
            from apps.subscriptions.models import SubscriptionPlan
            from apps.translations.models import Language
            
            return (
                Tenant.objects.filter(schema_name__startswith='sample_').exists() or
                SubscriptionPlan.objects.exists() or
                Language.objects.exists()
            )
        except ImportError:
            return False
    
    def _create_base_data(self):
        """Create base data needed for all modes."""
        from apps.translations.models import Language
        from apps.permissions.models import Permission, RoleGroup
        
        self.stdout.write('Creating base data...')
        
        # Create languages
        languages = [
            ('en', 'English', 'English', False),
            ('es', 'Spanish', 'Español', False),
            ('fr', 'French', 'Français', False),
            ('de', 'German', 'Deutsch', False),
            ('pt', 'Portuguese', 'Português', False),
        ]
        
        for code, name, native_name, is_rtl in languages:
            Language.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'native_name': native_name,
                    'is_rtl': is_rtl,
                    'is_active': True
                }
            )
        
        # Create basic permissions
        permissions = [
            ('view_dashboard', 'Can view dashboard'),
            ('manage_tenants', 'Can manage tenants'),
            ('manage_users', 'Can manage users'),
            ('manage_subscriptions', 'Can manage subscriptions'),
            ('view_analytics', 'Can view analytics'),
            ('manage_settings', 'Can manage settings'),
        ]
        
        for codename, name in permissions:
            Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': name}
            )
        
        # Create role groups
        admin_role, created = RoleGroup.objects.get_or_create(
            name='admin',
            defaults={
                'display_name': 'Administrator',
                'description': 'Full system access'
            }
        )
        
        if created:
            admin_permissions = Permission.objects.all()
            admin_role.permissions.set(admin_permissions)
    
    def _create_subscription_plans(self):
        """Create subscription plans."""
        from apps.subscriptions.models import SubscriptionPlan
        
        self.stdout.write('Creating subscription plans...')
        
        plans = [
            {
                'name': 'Starter',
                'description': 'Perfect for small teams getting started',
                'price_monthly': Decimal('29.99'),
                'price_yearly': Decimal('299.99'),
                'max_users': 5,
                'max_storage_gb': 10,
                'features': {
                    'api_access': True,
                    'basic_analytics': True,
                    'email_support': True,
                },
                'is_active': True
            },
            {
                'name': 'Professional',
                'description': 'Ideal for growing businesses',
                'price_monthly': Decimal('79.99'),
                'price_yearly': Decimal('799.99'),
                'max_users': 25,
                'max_storage_gb': 100,
                'features': {
                    'api_access': True,
                    'basic_analytics': True,
                    'email_support': True,
                    'custom_domain': True,
                },
                'is_active': True
            },
            {
                'name': 'Free Trial',
                'description': '14-day free trial with full features',
                'price_monthly': Decimal('0.00'),
                'price_yearly': Decimal('0.00'),
                'max_users': 3,
                'max_storage_gb': 5,
                'features': {
                    'api_access': True,
                    'basic_analytics': True,
                },
                'is_active': True
            }
        ]
        
        for plan_data in plans:
            SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
    
    def _create_superuser(self):
        """Create superuser account."""
        self.stdout.write('Creating superuser...')
        
        UserModel = get_user_model()
        
        if not UserModel.objects.filter(is_superuser=True).exists():
            superuser = UserModel.objects.create_superuser(
                email='admin@clientiq.com',
                password='admin123',
                first_name='System',
                last_name='Administrator'
            )
            self.stdout.write(f'Superuser created: {superuser.email} / admin123')
        else:
            self.stdout.write('Superuser already exists')
    
    def _seed_development_data(self, options):
        """Seed data for development environment."""
        from apps.tenants.models import Tenant, Domain
        from apps.subscriptions.models import SubscriptionPlan, Subscription
        
        self.stdout.write('Seeding development data...')
        
        num_tenants = options['tenants']
        
        # Get subscription plans
        plans = list(SubscriptionPlan.objects.all())
        if not plans:
            self.stdout.write(self.style.WARNING('No subscription plans found.'))
            return
        
        for i in range(num_tenants):
            tenant_name = f'Sample Company {i+1}'
            schema_name = f'sample_company_{i+1}'
            domain_name = f'sample{i+1}.localhost'
            
            # Create tenant
            tenant, created = Tenant.objects.get_or_create(
                schema_name=schema_name,
                defaults={
                    'name': tenant_name,
                    'description': f'Sample tenant for development - {tenant_name}',
                }
            )
            
            if created:
                # Create domain
                Domain.objects.create(
                    domain=domain_name,
                    tenant=tenant,
                    is_primary=True
                )
                
                # Create subscription
                plan = random.choice(plans)
                Subscription.objects.create(
                    tenant=tenant,
                    plan=plan,
                    billing_cycle=random.choice(['monthly', 'yearly']),
                    status='active'
                )
                
                self.stdout.write(f'Created tenant: {tenant_name}')
    
    def _seed_production_data(self, options):
        """Seed minimal data for production environment."""
        self.stdout.write('Seeding production data...')
        self.stdout.write('Production mode: Only essential data created.')
    
    def _seed_demo_data(self, options):
        """Seed data for demo purposes."""
        from apps.tenants.models import Tenant, Domain
        from apps.subscriptions.models import SubscriptionPlan, Subscription
        
        self.stdout.write('Seeding demo data...')
        
        # Create demo tenant
        demo_tenant, created = Tenant.objects.get_or_create(
            schema_name='demo_techcorp',
            defaults={
                'name': 'TechCorp Solutions',
                'description': 'Demo tenant showcasing ClientIQ capabilities',
            }
        )
        
        if created:
            Domain.objects.create(
                domain='demo.clientiq.com',
                tenant=demo_tenant,
                is_primary=True
            )
            
            # Create subscription
            try:
                pro_plan = SubscriptionPlan.objects.get(name='Professional')
                Subscription.objects.create(
                    tenant=demo_tenant,
                    plan=pro_plan,
                    billing_cycle='monthly',
                    status='active'
                )
            except SubscriptionPlan.DoesNotExist:
                self.stdout.write(self.style.WARNING('Professional plan not found for demo tenant'))
            
            self.stdout.write('Created demo tenant: TechCorp Solutions')
    
    def _print_summary(self):
        """Print a summary of seeded data."""
        from apps.tenants.models import Tenant
        from apps.subscriptions.models import SubscriptionPlan
        from apps.translations.models import Language
        from apps.permissions.models import Permission
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('SEEDING SUMMARY'))
        self.stdout.write('='*50)
        
        # Count created objects
        tenant_count = Tenant.objects.count()
        plan_count = SubscriptionPlan.objects.count()
        language_count = Language.objects.count()
        permission_count = Permission.objects.count()
        
        self.stdout.write(f'Tenants created: {tenant_count}')
        self.stdout.write(f'Subscription plans: {plan_count}')
        self.stdout.write(f'Languages: {language_count}')
        self.stdout.write(f'Permissions: {permission_count}')
        
        # List created tenants
        if tenant_count > 0:
            self.stdout.write('\nCreated tenants:')
            for tenant in Tenant.objects.all()[:5]:  # Show first 5
                domain = tenant.domains.filter(is_primary=True).first()
                domain_name = domain.domain if domain else 'No domain'
                self.stdout.write(f'  - {tenant.name} ({domain_name})')
        
        # Superuser info
        UserModel = get_user_model()
        if UserModel.objects.filter(is_superuser=True).exists():
            self.stdout.write('\nSuperuser login: admin@clientiq.com / admin123')
        
        self.stdout.write('\n' + '='*50)
