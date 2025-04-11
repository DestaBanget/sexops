#!/usr/bin/env python
"""
Helper script to set up the database for the first time.
This will create all necessary tables and load initial data.
"""
import os
import sys
import subprocess
import django
from django.core.management import call_command

if __name__ == "__main__":
    # Set environment variable for local development
    os.environ.setdefault('DJANGO_ENVIRONMENT', 'local')
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoppet.settings')
    
    # Initialize Django
    django.setup()
    
    print("Creating migrations for each app...")
    apps = ['accounts', 'products', 'cart', 'orders', 'core']
    for app in apps:
        print(f"Creating migrations for {app}...")
        call_command('makemigrations', app)
    
    print("\nApplying all migrations...")
    call_command('migrate')
    
    print("\nCreating a superuser for the admin interface...")
    try:
        call_command('createsuperuser')
    except Exception as e:
        print(f"Error creating superuser: {e}")
        print("You can create a superuser later with: python manage.py createsuperuser")
    
    print("\nCollecting static files...")
    try:
        call_command('collectstatic', '--noinput')
    except Exception as e:
        print(f"Error collecting static files: {e}")
        print("You can collect static files later with: python manage.py collectstatic")
    
    print("\nDatabase setup complete!")
    print("You can now run the server with:")
    print("python manage.py runserver")
    print("or with SSL:")
    print("python manage.py runserver_plus --cert-file=cert.pem --key-file=key.pem")
