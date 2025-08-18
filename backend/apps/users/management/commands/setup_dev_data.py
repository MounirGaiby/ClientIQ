from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.demo.models import DemoRequest


class Command(BaseCommand):
    help = 'Setup initial data for ClientIQ development - Acme Corporation'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data for Acme Corporation...')
        
        # Create system superuser (global admin)
        if not User.objects.filter(username='superadmin').exists():
            super_admin = User.objects.create_superuser(
                username='superadmin',
                email='superadmin@clientiq.com',
                password='SuperAdmin123!',
                first_name='System',
                last_name='Administrator'
            )
            super_admin.profile.user_type = 'admin'
            super_admin.profile.is_tenant_admin = False
            super_admin.profile.department = 'IT'
            super_admin.profile.job_title = 'System Administrator'
            super_admin.profile.save()
            self.stdout.write(self.style.SUCCESS('✓ Created system superuser (superadmin@clientiq.com / SuperAdmin123!)'))
        
        # Create Acme Corporation tenant admin
        if not User.objects.filter(username='acme_admin').exists():
            tenant_admin = User.objects.create_user(
                username='acme_admin',
                email='admin@acmecorp.com',
                password='AcmeAdmin123!',
                first_name='John',
                last_name='Administrator',
                is_staff=True
            )
            tenant_admin.profile.user_type = 'admin'
            tenant_admin.profile.is_tenant_admin = True
            tenant_admin.profile.department = 'Management'
            tenant_admin.profile.job_title = 'IT Administrator'
            tenant_admin.profile.phone_number = '+1-555-0001'
            tenant_admin.profile.save()
            self.stdout.write(self.style.SUCCESS('✓ Created Acme Corp tenant admin (admin@acmecorp.com / AcmeAdmin123!)'))
        
        # Create Acme Corporation users
        acme_users = [
            {
                'username': 'sarah_manager',
                'email': 'sarah.johnson@acmecorp.com',
                'password': 'AcmeManager123!',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'user_type': 'manager',
                'department': 'Sales',
                'job_title': 'Sales Manager',
                'phone_number': '+1-555-0002'
            },
            {
                'username': 'mike_user',
                'email': 'mike.wilson@acmecorp.com', 
                'password': 'AcmeUser123!',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'user_type': 'user',
                'department': 'Marketing',
                'job_title': 'Marketing Specialist',
                'phone_number': '+1-555-0003'
            },
            {
                'username': 'emily_user',
                'email': 'emily.davis@acmecorp.com', 
                'password': 'AcmeUser123!',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'user_type': 'user',
                'department': 'Operations',
                'job_title': 'Operations Coordinator',
                'phone_number': '+1-555-0004'
            }
        ]
        
        for user_data in acme_users:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                user.profile.user_type = user_data['user_type']
                user.profile.department = user_data['department']
                user.profile.job_title = user_data['job_title']
                user.profile.phone_number = user_data['phone_number']
                user.profile.is_tenant_admin = False
                user.profile.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created Acme Corp user: {user_data["email"]}'))
        
        # Create sample demo requests for Acme Corp prospects
        demo_requests = [
            {
                'company_name': 'TechStart Solutions',
                'first_name': 'Jennifer',
                'last_name': 'Chen',
                'email': 'jennifer.chen@techstart.com',
                'phone': '+1-555-1001',
                'job_title': 'CEO',
                'company_size': '11-50',
                'industry': 'Technology',
                'message': 'Interested in ClientIQ for our growing tech startup. We need better client management.',
                'status': 'pending'
            },
            {
                'company_name': 'Global Manufacturing Inc',
                'first_name': 'Robert',
                'last_name': 'Anderson',
                'email': 'r.anderson@globalmfg.com',
                'phone': '+1-555-1002',
                'job_title': 'Operations Director',
                'company_size': '501-1000',
                'industry': 'Manufacturing',
                'message': 'Looking for a comprehensive solution to manage our client relationships across multiple regions.',
                'status': 'processing'
            },
            {
                'company_name': 'Creative Agency Pro',
                'first_name': 'Lisa',
                'last_name': 'Martinez',
                'email': 'lisa@creativeagencypro.com',
                'phone': '+1-555-1003',
                'job_title': 'Creative Director',
                'company_size': '11-50',
                'industry': 'Marketing & Advertising',
                'message': 'We need a client management system that integrates well with creative workflows.',
                'status': 'pending'
            }
        ]
        
        for demo_data in demo_requests:
            if not DemoRequest.objects.filter(email=demo_data['email']).exists():
                DemoRequest.objects.create(**demo_data)
                self.stdout.write(self.style.SUCCESS(f'✓ Created demo request from {demo_data["company_name"]}'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Setup Complete ==='))
        self.stdout.write(self.style.SUCCESS('System Superuser:'))
        self.stdout.write(self.style.SUCCESS('  Email: superadmin@clientiq.com'))
        self.stdout.write(self.style.SUCCESS('  Password: SuperAdmin123!'))
        self.stdout.write(self.style.SUCCESS('\nAcme Corporation Tenant Admin:'))
        self.stdout.write(self.style.SUCCESS('  Email: admin@acmecorp.com'))
        self.stdout.write(self.style.SUCCESS('  Password: AcmeAdmin123!'))
        self.stdout.write(self.style.SUCCESS('\nAcme Corporation Users:'))
        self.stdout.write(self.style.SUCCESS('  Manager: sarah.johnson@acmecorp.com / AcmeManager123!'))
        self.stdout.write(self.style.SUCCESS('  User 1: mike.wilson@acmecorp.com / AcmeUser123!'))
        self.stdout.write(self.style.SUCCESS('  User 2: emily.davis@acmecorp.com / AcmeUser123!'))
