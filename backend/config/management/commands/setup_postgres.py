"""
Management command to setup PostgreSQL database and run migrations.
This command will:
1. Create the database if it doesn't exist
2. Run all migrations
3. Handle errors gracefully
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.conf import settings
from decouple import config


class Command(BaseCommand):
    help = 'Setup PostgreSQL database and run migrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running migrations after database creation'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting PostgreSQL database setup...')
        )

        # Get database configuration from environment
        db_config = self.get_db_config()
        
        if not db_config:
            self.stdout.write(
                self.style.ERROR('❌ PostgreSQL configuration not found in environment')
            )
            return

        # Create database if it doesn't exist
        if self.create_database_if_not_exists(db_config):
            self.stdout.write(
                self.style.SUCCESS(f'✅ Database "{db_config["NAME"]}" is ready')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Failed to setup database')
            )
            return

        # Run migrations unless skipped
        if not options['skip_migrations']:
            self.run_migrations()

        self.stdout.write(
            self.style.SUCCESS('🎉 Database setup complete!')
        )

    def get_db_config(self):
        """Extract PostgreSQL configuration from environment variables."""
        database_url = config('DATABASE_URL', default='')
        
        if not database_url.startswith('postgresql'):
            self.stdout.write(
                self.style.WARNING('⚠️ DATABASE_URL does not specify PostgreSQL')
            )
            return None

        # Parse database URL or use individual environment variables
        try:
            import dj_database_url
            db_config = dj_database_url.parse(database_url)
            
            return {
                'NAME': db_config['NAME'],
                'USER': db_config['USER'],
                'PASSWORD': db_config['PASSWORD'],
                'HOST': db_config['HOST'],
                'PORT': db_config['PORT'],
            }
        except ImportError:
            self.stdout.write(
                self.style.WARNING('⚠️ dj_database_url not available, using individual env vars')
            )
            
            return {
                'NAME': config('DATABASE_NAME', default='clientiq_db'),
                'USER': config('DATABASE_USER', default='postgres'),
                'PASSWORD': config('DATABASE_PASSWORD', default=''),
                'HOST': config('DATABASE_HOST', default='localhost'),
                'PORT': config('DATABASE_PORT', default='5432'),
            }

    def create_database_if_not_exists(self, db_config):
        """Create PostgreSQL database if it doesn't exist."""
        try:
            # Connect to PostgreSQL server (not specific database)
            conn = psycopg2.connect(
                host=db_config['HOST'],
                port=db_config['PORT'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                database='postgres'  # Connect to default postgres database
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                (db_config['NAME'],)
            )
            
            if cursor.fetchone():
                self.stdout.write(
                    self.style.SUCCESS(f'📊 Database "{db_config["NAME"]}" already exists')
                )
            else:
                # Create database
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_config['NAME'])
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(f'🆕 Created database "{db_config["NAME"]}"')
                )

            cursor.close()
            conn.close()
            return True

        except psycopg2.Error as e:
            self.stdout.write(
                self.style.ERROR(f'❌ PostgreSQL error: {e}')
            )
            return False
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error: {e}')
            )
            return False

    def run_migrations(self):
        """Run Django migrations."""
        try:
            self.stdout.write(
                self.style.SUCCESS('🔄 Running migrations...')
            )
            
            # Run migrations
            execute_from_command_line(['manage.py', 'migrate'])
            
            self.stdout.write(
                self.style.SUCCESS('✅ Migrations completed successfully')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Migration error: {e}')
            )
            raise
