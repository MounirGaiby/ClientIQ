#!/usr/bin/env python
"""
Simple test runner script that bypasses Django's test framework issues.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project directory to the path
sys.path.insert(0, '/root/projects/ClientIQ/backend')

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_simple')

# Setup Django
django.setup()

# Import and run tests manually
def run_simple_tests():
    """Run basic tests without complex tenant setup."""
    
    # Import test modules
    from apps.platform.tests_simple import SuperUserModelTest
    
    # Run tests
    import unittest
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTest(SuperUserModelTest('test_create_superuser'))
    suite.addTest(SuperUserModelTest('test_create_readonly_superuser'))
    suite.addTest(SuperUserModelTest('test_superuser_str_representation'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_simple_tests()
    sys.exit(0 if success else 1)
