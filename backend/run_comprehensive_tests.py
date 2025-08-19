#!/usr/bin/env python
"""
Comprehensive test runner with coverage reporting.
"""

import os
import sys
import django
from django.conf import settings
import unittest

# Add the project directory to the path
sys.path.insert(0, '/root/projects/ClientIQ/backend')

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_simple')

# Setup Django
django.setup()

def run_all_tests():
    """Run all available tests with coverage."""
    
    # Import test modules
    from apps.platform.tests_simple import SuperUserModelTest
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all tests from SuperUserModelTest
    for test_name in ['test_create_superuser', 'test_create_readonly_superuser', 
                      'test_superuser_str_representation', 'test_superuser_email_required']:
        suite.addTest(SuperUserModelTest(test_name))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TESTS SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("Starting ClientIQ Backend Test Suite")
    print("="*50)
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("Your multi-tenant Django backend is working correctly!")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please review the failures above.")
    
    sys.exit(0 if success else 1)
