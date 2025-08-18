from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.demo.models import DemoRequest


class Command(BaseCommand):
    help = 'Setup initial data for ClientIQ development'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@testcorp.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            admin_user.profile.user_type = 'admin'
            admin_user.profile.is_tenant_admin = True
            admin_user.profile.save()
            self.stdout.write(self.style.SUCCESS('✓ Created admin user (admin@testcorp.com / admin123)'))
        
        # Create test users
        test_users = [
            {
                'username': 'manager',
                'email': 'manager@testcorp.com',
                'password': 'manager123',
                'first_name': 'Manager',
                'last_name': 'User',
                'user_type': 'manager',
                'department': 'Sales',
                'job_title': 'Sales Manager'
            },
            {
                'username': 'user1',
                'email': 'user1@testcorp.com', 
                'password': 'user123',
                'first_name': 'Regular',
                'last_name': 'User',
                'user_type': 'user',
                'department': 'Marketing',
                'job_title': 'Marketing Specialist'
            }
        ]
        
        for user_data in test_users:
            if not User.objects.filter(username=user_data['username']).exists():
                profile_data = {
                    'user_type': user_data.pop('user_type'),
                    'department': user_data.pop('department', ''),
                    'job_title': user_data.pop('job_title', '')
                }
                
                user = User.objects.create_user(**user_data)
                
                # Update profile
                for key, value in profile_data.items():
                    setattr(user.profile, key, value)
                user.profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created {profile_data["user_type"]} user ({user.email})')
                )
        
        # Create sample demo requests
        sample_requests = [
            {
                'company_name': 'Test Corporation',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@testcorp.com',
                'phone': '+1-555-0123',
                'job_title': 'CEO',
                'company_size': '51-200',
                'industry': 'Technology',
                'message': 'Interested in learning more about your multi-tenant solutions.'
            },
            {
                'company_name': 'Sample Industries',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@sampleind.com',
                'phone': '+1-555-0456',
                'job_title': 'CTO',
                'company_size': '201-1000',
                'industry': 'Finance',
                'message': 'Need a demo for our enterprise requirements.'
            }
        ]
        
        for req_data in sample_requests:
            if not DemoRequest.objects.filter(email=req_data['email']).exists():
                DemoRequest.objects.create(**req_data)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created demo request from {req_data["company_name"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Setup complete! You can now:')
        )
        self.stdout.write('   • Login as admin: admin@testcorp.com / admin123')
        self.stdout.write('   • Login as manager: manager@testcorp.com / manager123') 
        self.stdout.write('   • Login as user: user1@testcorp.com / user123')
        self.stdout.write('   • View demo requests in Django admin')
        self.stdout.write('   • Test the API endpoints\n')
