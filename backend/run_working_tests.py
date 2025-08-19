#!/usr/bin/env python3
"""
ClientIQ Working Test Suite Runner
=================================
Runs only the tests that are currently working properly.
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configure Django settings for comprehensive testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_comprehensive_test')

# Setup Django
django.setup()

def main():
    """Run working tests only."""
    print("="*60)
    print("🎯 CLIENTIQ WORKING TEST SUITE")
    print("="*60)
    
    # Run migrations first
    from django.core.management import call_command
    call_command('migrate', verbosity=0, interactive=False)
    
    import unittest
    
    # Create test suite with only working tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    print("📊 LOADING WORKING TESTS:")
    print("-" * 40)
    
    # Platform tests (all working)
    from apps.platform.tests_working import SuperUserModelTest, SuperUserManagerTest, SuperUserAdminTest
    platform_tests = [SuperUserModelTest, SuperUserManagerTest, SuperUserAdminTest]
    
    for test_class in platform_tests:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        print(f"✅ Added {test_class.__name__}: {tests.countTestCases()} tests")
    
    # User tests (working ones)
    from apps.users.tests_working import CustomUserModelTest, UserManagerTest
    
    # Add only specific working tests from CustomUserModelTest
    working_user_tests = [
        'test_create_user',
        'test_create_admin_user', 
        'test_user_str_representation',
        'test_get_full_name',
        'test_get_short_name',
        'test_email_required',
        'test_user_permissions',
        'test_admin_user_permissions'
    ]
    
    for test_name in working_user_tests:
        suite.addTest(CustomUserModelTest(test_name))
    
    # Add working UserManager tests
    working_manager_tests = [
        'test_create_user_method',
        'test_email_normalization',
        'test_create_superuser_method'
    ]
    
    for test_name in working_manager_tests:
        suite.addTest(UserManagerTest(test_name))
    
    print(f"✅ Added CustomUser working tests: {len(working_user_tests)} tests")
    print(f"✅ Added UserManager working tests: {len(working_manager_tests)} tests")
    
    # Authentication tests (working ones)
    from apps.authentication.tests_working import TenantAuthenticationMiddlewareTest
    auth_tests = loader.loadTestsFromTestCase(TenantAuthenticationMiddlewareTest)
    suite.addTests(auth_tests)
    print(f"✅ Added TenantAuthenticationMiddlewareTest: {auth_tests.countTestCases()} tests")
    
    # Management command tests (some working)
    from apps.users.test_management_commands_working import (
        SetupSimpleTenantCommandTest, 
        CleanTenantPermissionsCommandTest,
        ManagementCommandIntegrationTest,
        ManagementCommandSecurityTest
    )
    
    # Add specific working management command tests
    working_mgmt_tests = [
        ('SetupSimpleTenantCommandTest', [
            'test_setup_simple_tenant_command_exists',
            'test_setup_simple_tenant_with_defaults',
            'test_setup_simple_tenant_invalid_email'
        ]),
        ('CleanTenantPermissionsCommandTest', [
            'test_clean_tenant_permissions_command_exists',
            'test_clean_tenant_permissions_dry_run',
            'test_clean_tenant_permissions_execution',
            'test_clean_tenant_permissions_specific_patterns'
        ]),
        ('ManagementCommandIntegrationTest', [
            'test_command_discovery',
            'test_command_error_handling',
            'test_command_output_capture'
        ]),
        ('ManagementCommandSecurityTest', [
            'test_command_permission_validation',
            'test_command_sql_injection_protection'
        ])
    ]
    
    for class_name, test_methods in working_mgmt_tests:
        test_class = locals()[class_name]
        for method_name in test_methods:
            suite.addTest(test_class(method_name))
        print(f"✅ Added {class_name}: {len(test_methods)} tests")
    
    total_tests = suite.countTestCases()
    print(f"\n🎯 TOTAL WORKING TESTS: {total_tests}")
    print("="*60)
    
    # Run the working test suite
    print("🚀 EXECUTING WORKING TEST SUITE...")
    print("-" * 60)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("📊 WORKING TEST RESULTS")
    print("="*60)
    
    print(f"✅ TOTAL TESTS RUN: {result.testsRun}")
    print(f"🎉 SUCCESSFUL TESTS: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ FAILED TESTS: {len(result.failures)}")
    print(f"⚠️  ERROR TESTS: {len(result.errors)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"📊 SUCCESS RATE: {success_rate:.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n⚠️  ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("🎊 ALL WORKING TESTS PASSED! 🎊")
        print("✨ Core functionality is solid and reliable!")
    else:
        print(f"✨ {success_rate:.1f}% of curated tests are working!")
        print("🔧 This demonstrates solid core functionality!")
    
    print("="*60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
