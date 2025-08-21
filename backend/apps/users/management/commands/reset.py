import os
import sys
import shutil
from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line, call_command
from django.conf import settings
from django.db import connection
from django_tenants.utils import get_public_schema_name
from apps.tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Reset database: Drop all data, recreate tables, and run seed command'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        if not force:
            confirm = input(
                "⚠️  This will DELETE ALL DATA and recreate the database.\n"
                "Are you sure you want to continue? (yes/no): "
            )
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('❌ Reset cancelled.'))
                return

        self.stdout.write(self.style.WARNING('🗑️  Starting database reset...'))
        
        try:
            # Step 1: Delete all tenant schemas and data
            self.delete_tenant_data()
            
            # Step 2: Reset migrations
            self.reset_migrations()
            
            # Step 3: Recreate database structure
            self.recreate_database()
            
            # Step 4: Run migrations
            self.run_migrations()
            
            # Step 5: Run seed command
            self.run_seed()
            
            self.stdout.write(self.style.SUCCESS('🎉 Database reset and seed completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Reset failed: {str(e)}'))
            sys.exit(1)

    def delete_tenant_data(self):
        """Delete all tenant schemas and related data"""
        self.stdout.write('🧹 Cleaning tenant data...')
        
        try:
            # Get all tenants
            tenants = Tenant.objects.all()
            
            for tenant in tenants:
                if tenant.schema_name != get_public_schema_name():
                    self.stdout.write(f'   Dropping schema: {tenant.schema_name}')
                    
                    # Drop the schema
                    with connection.cursor() as cursor:
                        cursor.execute(f'DROP SCHEMA IF EXISTS "{tenant.schema_name}" CASCADE')
            
            # Delete tenant and domain records from public schema
            Domain.objects.all().delete()
            Tenant.objects.exclude(schema_name=get_public_schema_name()).delete()
            
            self.stdout.write('✅ Tenant data cleaned')
            
        except Exception as e:
            self.stdout.write(f'⚠️  Error cleaning tenant data: {str(e)}')

    def reset_migrations(self):
        """Reset migration files (keep initial migrations)"""
        self.stdout.write('🔄 Resetting migrations...')
        
        try:
            apps_dir = os.path.join(settings.BASE_DIR, 'apps')
            
            for app_name in os.listdir(apps_dir):
                app_path = os.path.join(apps_dir, app_name)
                if os.path.isdir(app_path):
                    migrations_path = os.path.join(app_path, 'migrations')
                    
                    if os.path.exists(migrations_path):
                        # Keep __init__.py and 0001_initial.py, remove others
                        for file in os.listdir(migrations_path):
                            file_path = os.path.join(migrations_path, file)
                            
                            if (file.endswith('.py') and 
                                file != '__init__.py' and 
                                not file.startswith('0001_initial')):
                                os.remove(file_path)
                                self.stdout.write(f'   Removed: {app_name}/migrations/{file}')
                        
                        # Remove __pycache__
                        pycache_path = os.path.join(migrations_path, '__pycache__')
                        if os.path.exists(pycache_path):
                            shutil.rmtree(pycache_path)
            
            self.stdout.write('✅ Migrations reset')
            
        except Exception as e:
            self.stdout.write(f'⚠️  Error resetting migrations: {str(e)}')

    def recreate_database(self):
        """Recreate database tables"""
        self.stdout.write('🏗️  Recreating database structure...')
        
        try:
            # Flush the database (this removes all data but keeps structure)
            call_command('flush', '--noinput', verbosity=0)
            
            # Drop all tables to ensure clean slate
            with connection.cursor() as cursor:
                # Get all table names
                cursor.execute("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename NOT LIKE 'pg_%' 
                    AND tablename NOT LIKE 'sql_%'
                """)
                
                tables = cursor.fetchall()
                
                if tables:
                    # Drop all tables
                    table_names = [table[0] for table in tables]
                    cursor.execute(f'DROP TABLE IF EXISTS {", ".join(table_names)} CASCADE')
                    self.stdout.write(f'   Dropped {len(table_names)} tables')
            
            self.stdout.write('✅ Database structure recreated')
            
        except Exception as e:
            self.stdout.write(f'⚠️  Error recreating database: {str(e)}')

    def run_migrations(self):
        """Run all migrations"""
        self.stdout.write('📦 Running migrations...')
        
        try:
            # Create migrations if needed
            call_command('makemigrations', verbosity=1)
            
            # Run migrations
            call_command('migrate', verbosity=1)
            
            self.stdout.write('✅ Migrations completed')
            
        except Exception as e:
            self.stdout.write(f'❌ Migration error: {str(e)}')
            raise

    def run_seed(self):
        """Run the seed command"""
        self.stdout.write('🌱 Running seed command...')
        
        try:
            call_command('seed', verbosity=1)
            self.stdout.write('✅ Seed completed')
            
        except Exception as e:
            self.stdout.write(f'❌ Seed error: {str(e)}')
            raise

    def get_database_info(self):
        """Get database connection info for display"""
        db_settings = settings.DATABASES['default']
        return {
            'engine': db_settings.get('ENGINE', 'Unknown'),
            'name': db_settings.get('NAME', 'Unknown'),
            'host': db_settings.get('HOST', 'localhost'),
            'port': db_settings.get('PORT', '5432'),
        }
