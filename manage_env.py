#!/usr/bin/env python
"""
Helper script to set the Django environment variable before running Django commands.
Usage: python manage_env.py [local|production] [django_command]
Example: python manage_env.py local runserver
Example: python manage_env.py production migrate
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python manage_env.py [local|production] [django_command]")
        sys.exit(1)
    
    env = sys.argv[1]
    if env not in ['local', 'production']:
        print("Environment must be either 'local' or 'production'")
        sys.exit(1)
    
    # Set environment variable
    os.environ['DJANGO_ENVIRONMENT'] = env
    
    # Run Django command
    command = [sys.executable, 'manage.py'] + sys.argv[2:]
    subprocess.run(command)
