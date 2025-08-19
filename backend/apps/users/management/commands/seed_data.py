from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.demo.models import DemoRequest
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--demos',
            type=int,
            default=20,
            help='Number of demo requests to create (default: 20)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting database seeding...'))
        
        # Create sample users
        self.create_users(options['users'])
        
        # Create sample demo requests
        self.create_demo_requests(options['demos'])
        
        self.stdout.write(self.style.SUCCESS('🎉 Database seeding completed!'))

    def create_users(self, count):
        self.stdout.write(f'👥 Creating {count} sample users...')
        
        # Create admin user
        if not User.objects.filter(email='admin@clientiq.com').exists():
            admin_user = User.objects.create_user(
                email='admin@clientiq.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                user_type='admin',
                is_staff=True,
                is_superuser=True,
                department='IT',
                job_title='System Administrator'
            )
            self.stdout.write(f'✅ Created admin user: {admin_user.email}')

        # Sample data for users
        departments = ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations']
        job_titles = [
            'Sales Manager', 'Marketing Specialist', 'Software Engineer', 
            'HR Coordinator', 'Financial Analyst', 'Operations Manager',
            'Product Manager', 'UX Designer', 'DevOps Engineer', 'Data Analyst'
        ]
        
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 
            'Robert', 'Lisa', 'James', 'Maria', 'William', 'Jennifer'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
            'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez'
        ]

        # Create regular users
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f'{first_name.lower()}.{last_name.lower()}{i}@company.com'
            
            # Skip if user already exists
            if User.objects.filter(email=email).exists():
                continue
                
            user_type = random.choices(
                ['user', 'manager', 'admin'],
                weights=[70, 25, 5]  # 70% users, 25% managers, 5% admins
            )[0]
            
            user = User.objects.create_user(
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,
                department=random.choice(departments),
                job_title=random.choice(job_titles),
                phone_number=f'+1{random.randint(1000000000, 9999999999)}',
                is_tenant_admin=random.choice([True, False]) if user_type == 'admin' else False,
                preferences={
                    'theme': random.choice(['light', 'dark']),
                    'notifications': random.choice([True, False]),
                    'language': random.choice(['en', 'es', 'fr'])
                }
            )
            self.stdout.write(f'✅ Created user: {user.email} ({user.user_type})')

    def create_demo_requests(self, count):
        self.stdout.write(f'📋 Creating {count} sample demo requests...')
        
        companies = [
            'TechCorp Inc', 'Global Solutions Ltd', 'InnovateCo', 'DataDriven LLC',
            'CloudFirst Technologies', 'NextGen Systems', 'SmartBusiness Co',
            'Digital Transform Inc', 'FutureTech Solutions', 'AgileWorks Ltd'
        ]
        
        industries = [
            'Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing',
            'Education', 'Real Estate', 'Consulting', 'Media', 'Transportation'
        ]
        
        use_cases = [
            'Customer Analytics', 'Sales Intelligence', 'Market Research',
            'Competitive Analysis', 'Lead Generation', 'Customer Segmentation',
            'Performance Tracking', 'Business Intelligence', 'Data Visualization',
            'Predictive Analytics'
        ]

        for i in range(count):
            # Random demo request date (last 30 days)
            request_date = timezone.now() - timedelta(days=random.randint(0, 30))
            
            first_name = random.choice(['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery'])
            last_name = random.choice(['Brown', 'Smith', 'Johnson', 'Davis', 'Wilson', 'Garcia', 'Miller'])
            
            demo_request = DemoRequest.objects.create(
                company_name=random.choice(companies),
                first_name=first_name,
                last_name=last_name,
                email=f'{first_name.lower()}.{last_name.lower()}{i}@{random.choice(companies).lower().replace(" ", "").replace("inc", "").replace("ltd", "").replace("llc", "").replace("co", "")}.com',
                phone=f'+1{random.randint(1000000000, 9999999999)}',
                job_title=random.choice(['CEO', 'CTO', 'VP Sales', 'Marketing Director', 'Operations Manager', 'Business Analyst']),
                industry=random.choice(industries),
                company_size=random.choice(['1-10', '11-50', '51-200', '201-500', '500+']),
                message=f'Interested in implementing {random.choice(use_cases).lower()} solution for our {random.choice(industries).lower()} business.',
                status=random.choices(
                    ['pending', 'processing', 'approved', 'converted', 'failed', 'rejected'],
                    weights=[40, 20, 15, 15, 5, 5]
                )[0],
                created_at=request_date
            )
            self.stdout.write(f'✅ Created demo request: {demo_request.company_name} - {demo_request.first_name} {demo_request.last_name}')

        self.stdout.write(f'📊 Demo request status summary:')
        for status, _ in DemoRequest.STATUS_CHOICES:
            count = DemoRequest.objects.filter(status=status).count()
            self.stdout.write(f'   {status.title()}: {count}')
