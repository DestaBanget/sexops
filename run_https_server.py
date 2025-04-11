#!/usr/bin/env python
"""
Simple script to run Django with HTTPS support.
Usage: python run_https_server.py
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    # Set environment variable for local development
    os.environ['DJANGO_ENVIRONMENT'] = 'local'
    
    # Check if OpenSSL is available
    try:
        # Generate self-signed certificate if it doesn't exist
        if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
            print("Generating self-signed certificate...")
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:2048', 
                '-keyout', 'key.pem', '-out', 'cert.pem', '-days', '365',
                '-nodes', '-subj', '/CN=localhost'
            ], check=True)
            print("Certificate generated successfully.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Warning: OpenSSL not found or error generating certificate.")
        print("You may need to generate certificates manually.")
    
    # Run Django with SSL
    print("Starting Django development server with SSL...")
    print("Access your site at: https://localhost:8000/")
    
    # Use Python's built-in SSL server
    command = [
        sys.executable, 'manage.py', 'runserver', 
        '--insecure', '--cert-file=cert.pem', '--key-file=key.pem'
    ]
    
    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nServer stopped.")
