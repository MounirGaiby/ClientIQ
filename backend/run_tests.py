#!/usr/bin/env python
"""
Comprehensive test runner for ClientIQ backend.
Runs all tests with coverage reporting.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def run_tests():
    """Run all tests with coverage."""
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_test'
    django.setup()
    
    # Import after Django setup
    from django.core.management import execute_from_command_line
    
    # Test command arguments
    test_args = [
        'manage.py',
        'test',
        '--verbosity=2',
        '--failfast',
        '--keepdb',  # Keep test database for faster subsequent runs
    ]
    
    # Add specific test patterns if provided
    if len(sys.argv) > 1:
        test_args.extend(sys.argv[1:])
    else:
        # Run all app tests
        test_args.extend([
            'apps.platform.tests',
            'apps.tenants.tests',
            'apps.users.tests',
            'apps.demo.tests',
            'apps.authentication.tests',
            'apps.users.test_management_commands',
        ])
    
    print("🧪 Running ClientIQ Backend Tests")
    print("=" * 50)
    print(f"Django version: {django.get_version()}")
    print(f"Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"Test arguments: {' '.join(test_args[2:])}")
    print("=" * 50)
    
    # Execute tests
    execute_from_command_line(test_args)

def run_tests_with_coverage():
    """Run tests with coverage reporting."""
    try:
        import coverage
    except ImportError:
        print("❌ Coverage not installed. Install with: pip install coverage")
        print("Running tests without coverage...")
        run_tests()
        return
    
    # Start coverage
    cov = coverage.Coverage(
        source=['apps', 'config'],
        omit=[
            '*/migrations/*',
            '*/tests/*',
            '*/test_*.py',
            '*/venv/*',
            '*/env/*',
            '*/settings/*',
            'manage.py',
            '*/wsgi.py',
            '*/asgi.py',
        ]
    )
    cov.start()
    
    print("📊 Running tests with coverage...")
    
    try:
        run_tests()
    finally:
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\n" + "=" * 50)
        print("📈 COVERAGE REPORT")
        print("=" * 50)
        
        # Console report
        cov.report(show_missing=True)
        
        # HTML report
        html_dir = os.path.join(os.path.dirname(__file__), 'htmlcov')
        cov.html_report(directory=html_dir)
        print(f"\n📄 Detailed HTML report generated: {html_dir}/index.html")
        
        # XML report for CI/CD
        xml_file = os.path.join(os.path.dirname(__file__), 'coverage.xml')
        cov.xml_report(outfile=xml_file)
        print(f"📄 XML report generated: {xml_file}")

if __name__ == '__main__':
    if '--with-coverage' in sys.argv:
        sys.argv.remove('--with-coverage')
        run_tests_with_coverage()
    else:
        run_tests()
