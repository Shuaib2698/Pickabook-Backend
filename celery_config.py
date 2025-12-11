import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('CELERY_CONFIG_MODULE', 'celeryconfig')

# Initialize Celery
celery_app = Celery('pickabook')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()

@celery_app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')