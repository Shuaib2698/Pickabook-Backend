import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('CELERY_CONFIG_MODULE', 'celeryconfig')

app = Celery('pickabook')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()