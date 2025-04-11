#!/usr/bin/env python
"""
Helper script to check the database status.
"""
import os
import sys
import django
from django.db import connection

if __name__ == "__main__":
    # Set environment variable for local development
    os.environ.setdefault('DJANGO_ENVIRONMENT', 'local')
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoppet.settings')
    
    # Initialize Django
    django.setup()
    
    # Get all tables in the database
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
    
    print("Database tables:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Check if specific tables exist
    required_tables = [
        'accounts_profile',
        'products_category',
        'products_product',
        'products_review',
        'cart_cartitem',
        'orders_order',
        'orders_orderitem'
    ]
    
    print("\nChecking required tables:")
    table_names = [table[0] for table in tables]
    for table in required_tables:
        if table in table_names:
            print(f"✓ {table} exists")
        else:
            print(f"✗ {table} does not exist")
