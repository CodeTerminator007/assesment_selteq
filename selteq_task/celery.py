import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selteq_task.settings')

app = Celery('selteq_task')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'print-user1-tasks-every-minute': {
        'task': 'tasks.tasks.print_user1_tasks',
        'schedule': 60.0,  # Every minute
    },
}

app.autodiscover_tasks()