#!/usr/bin/env python
"""
Helper script to run Django development server with SSL support.
Usage: python run_with_ssl.py
"""
import os
import sys
import ssl
import django
from django.core.management import call_command

if __name__ == "__main__":
    # Set environment variable for local development
    os.environ.setdefault('DJANGO_ENVIRONMENT', 'local')
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoppet.settings')
    
    # Initialize Django
    django.setup()
    
    # Generate self-signed certificate if it doesn't exist
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        from OpenSSL import crypto
        
        # Create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)
        
        # Create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "US"
        cert.get_subject().ST = "State"
        cert.get_subject().L = "City"
        cert.get_subject().O = "Organization"
        cert.get_subject().OU = "Organizational Unit"
        cert.get_subject().CN = "localhost"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)  # 10 years
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')
        
        # Save the certificate
        with open("cert.pem", "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        
        # Save the private key
        with open("key.pem", "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
        
        print("Generated self-signed certificate (cert.pem) and key (key.pem)")
    
    # Run the server with SSL
    from django.core.servers.basehttp import WSGIServer
    
    # Monkey patch the WSGIServer to use SSL
    original_init = WSGIServer.__init__
    
    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.socket = ssl.wrap_socket(
            self.socket,
            certfile='cert.pem',
            keyfile='key.pem',
            server_side=True
        )
    
    WSGIServer.__init__ = __init__
    
    # Run the server
    print("Starting Django development server with SSL support...")
    print("Access your site at: https://localhost:8000/")
    call_command('runserver')
