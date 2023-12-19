import os
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application 

os.environ['DJANGO_SECRET_KEY']='development'
os.environ['DJANGO_DEBUG']='1'
os.environ['ORS_API_KEY']='5b3ce3597851110001cf6248f1298dc6e61b40149c99e7261c0ab5da'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
application = get_wsgi_application()

call_command('runserver',  '127.0.0.1:8000')