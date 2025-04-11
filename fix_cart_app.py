#!/usr/bin/env python
"""
Helper script to fix the cart app migrations.
"""
import os
import sys
import django
from django.core.management import call_command

if __name__ == "__main__":
    # Set environment variable for local development
    os.environ.setdefault('DJANGO_ENVIRONMENT', 'local')
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoppet.settings')
    
    # Initialize Django
    django.setup()
    
    print("Creating migrations for cart app...")
    call_command('makemigrations', 'cart')
    
    print("\nApplying cart migrations...")
    call_command('migrate', 'cart')
    
    print("\nCart app fixed!")
