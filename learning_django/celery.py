# learning_django/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings module for 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_django.settings')

# Create Celery instance
app = Celery('learning_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))
