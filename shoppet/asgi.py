"""
ASGI config for shoppet project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoppet.settings')

application = get_asgi_application()