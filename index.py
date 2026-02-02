"""
Vercel Serverless Handler for Django
"""
from pmorganizer.wsgi import application

# Export the WSGI application as 'app' for Vercel
app = application
