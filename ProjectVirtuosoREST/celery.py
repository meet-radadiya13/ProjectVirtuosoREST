import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjectVirtuosoREST.settings')

app = Celery('ProjectVirtuosoREST')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
