import os
# from _future_ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "events_app.settings")

app = Celery('events_app')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()