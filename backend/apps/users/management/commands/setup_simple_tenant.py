from django.core.management.base import BaseCommand
from apps.users.models import CustomUser as User


class Command(BaseCommand):
    help = 'Create simplified tenant users (no superuser complexity)'

    def handle(self, *args, **options):
        from django.db import connection
        schema_name = connection.schema_name
        
        self.stdout.write(self.style.SUCCESS(f'🌱 Setting up {schema_name} tenant with simplified user structure'))
        
        # Create simple users without complex permissions
        self.create_users(schema_name)
        
        self.stdout.write(self.style.SUCCESS(f'🎉 Setup complete for {schema_name}!'))

    def create_users(self, schema_name):
        users_to_create = [
            {
                'email': f'admin@{schema_name}.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_admin': True,  # Simple admin flag - has all permissions
                'job_title': 'Administrator',
                'department': 'Management',
                'description': 'Tenant Admin (has all permissions via is_admin=True)'
            },
            {
                'email': f'manager@{schema_name}.com',
                'password': 'manager123',
                'first_name': 'Manager',
                'last_name': 'User',
                'is_admin': False,  # Regular user, specific permissions via groups/roles
                'job_title': 'Manager',
                'department': 'Operations',
                'description': 'Manager (specific permissions via groups)'
            },
            {
                'email': f'user@{schema_name}.com',
                'password': 'user123',
                'first_name': 'Regular',
                'last_name': 'User',
                'is_admin': False,  # Regular user
                'job_title': 'Employee',
                'department': 'Sales',
                'description': 'Regular User (basic permissions)'
            }
        ]

        for user_data in users_to_create:
            description = user_data.pop('description')
            
            if not User.objects.filter(email=user_data['email']).exists():
                user = User.objects.create_user(**user_data)
                
                self.stdout.write(f'✅ Created {user.email} - {description}')
            else:
                self.stdout.write(f'⏭️  User {user_data["email"]} already exists')

        self.stdout.write(self.style.SUCCESS('\n📋 User Summary:'))
        self.stdout.write(f'  🔑 Tenant Admin:  admin@{schema_name}.com / admin123 (is_admin=True)')
        self.stdout.write(f'  👤 Manager:       manager@{schema_name}.com / manager123') 
        self.stdout.write(f'  👤 Regular User:  user@{schema_name}.com / user123')
        self.stdout.write(f'\n🌐 Access via: http://{schema_name}.localhost:8000/')
        self.stdout.write(f'🔧 Platform Admin: http://localhost:8000/admin/ (admin@platform.com / platform123)')
