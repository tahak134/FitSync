"""
WSGI config for imdb_clone project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'fitsync' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitSync.settings')

# Get the WSGI application
application = get_wsgi_application()
