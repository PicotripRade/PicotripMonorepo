from celery import Celery
import os

from backend.settings import url, redis_port

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
#CELERY_RESULT_EXPIRES = 1800
# Create a Celery instance
app = Celery('backend')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Specify Redis as the message broker and result backend
app.conf.broker_url = f'redis://{url}:{redis_port}/0'
app.conf.result_backend = f'redis://{url}:{redis_port}/0'

# If you have defined tasks in a separate file, you can autodiscover them
# by adding the following line:
# app.autodiscover_tasks()
# In your Celery configuration file (celery.py or settings.py), add or update the following line:
broker_connection_retry_on_startup = False