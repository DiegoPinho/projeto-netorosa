"""
WSGI config for Vercel deployment.
This module is used by Vercel to serve the Django application.
"""

from pmorganizer.wsgi import application

# Vercel uses this 'app' variable
app = application
