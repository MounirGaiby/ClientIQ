#!/usr/bin/env python3
"""
Basic Test Infrastructure Validation
=====================================
Simple script to validate our comprehensive test infrastructure works.
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configure Django settings for testing  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_comprehensive_test')

# Setup Django
django.setup()

# Override database to SQLite in-memory after Django setup
from django.conf import settings
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}

def main():
    """Run basic validation tests."""
    print("🚀 BASIC TEST INFRASTRUCTURE VALIDATION")
    print("="*60)
    
    # Test 1: Can we import our models?
    try:
        from apps.platform.models import SuperUser
        from apps.users.models import CustomUser
        print("✅ Model imports successful")
    except ImportError as e:
        print(f"❌ Model import failed: {e}")
        return False
    
    # Test 2: Can we run migrations in memory?
    try:
        from django.core.management import call_command
        call_command('migrate', verbosity=0, interactive=False)
        print("✅ In-memory database migrations successful")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    # Test 3: Can we create basic models?
    try:
        # Test SuperUser creation
        user = SuperUser.objects.create_user(
            email='test@platform.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"✅ SuperUser creation successful: {user}")
        
        # Test CustomUser creation  
        custom_user = CustomUser.objects.create_user(
            email='test@client.com',
            password='testpass123',
            first_name='Test',
            last_name='Client'
        )
        print(f"✅ CustomUser creation successful: {custom_user}")
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False
    
    # Test 4: Can we run a simple unit test?
    try:
        import unittest
        from apps.platform.tests_simple import SuperUserModelTest
        
        suite = unittest.TestSuite()
        suite.addTest(SuperUserModelTest('test_create_superuser'))
        
        runner = unittest.TextTestRunner(verbosity=0)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("✅ Basic unit test execution successful")
        else:
            print(f"❌ Basic unit test failed: {result.failures} {result.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Unit test execution failed: {e}")
        return False
    
    print("\n🎉 ALL BASIC VALIDATIONS PASSED!")
    print("Test infrastructure is ready for comprehensive coverage!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
