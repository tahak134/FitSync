"""
ASGI config for imdb_clone project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Set the default settings module for the 'fitsync' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FittSync.settings')

# Get the ASGI application
application = get_asgi_application()
