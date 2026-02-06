"""
Celery Configuration and Task Scheduler.

This module initializes the Celery application and configures the Redis broker.
It defines a periodic task schedule (Celery Beat) to automate data fetching.
- Task: create_all_prices
- Interval: Every 60 seconds
"""

from celery import Celery

from app_deribit.core.config_env_variable import settings

# Initialize Celery app with Redis as the message broker
app = Celery('tasks', broker=f'redis://{settings.redis_host}:6379/0')

# Define where the worker should look for tasks
app.conf.imports = ['app_deribit.worker.tasks']

# Configure the periodic execution schedule (Celery Beat)
app.conf.beat_schedule = {
    'parse-site-every-minute': {
        'task': 'app_deribit.worker.tasks.create_all_prices',
        'schedule': 60.0,
    },
}