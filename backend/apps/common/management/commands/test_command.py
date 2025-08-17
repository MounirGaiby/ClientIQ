"""
Simple test management command
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Test command to verify management command system works'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Test command works!'))
