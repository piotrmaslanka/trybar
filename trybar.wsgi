import os
import sys

sys.path = ['/home/trybar/apps'] + sys.path
from django.core.handlers.wsgi import WSGIHandler

os.environ['DJANGO_SETTINGS_MODULE'] = 'trybar.settings'
application = WSGIHandler()