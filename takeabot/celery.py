import os
from datetime import timedelta

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'takeabot.settings')
celery_app = Celery('takeabot')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.conf.beat_schedule = {
    'collect_data': {
        'task': 'mybot.parser.parse_all',
        'schedule': timedelta(seconds=86400),
    },
    'compare_prices_task': {
        'task': 'core.tasks.compare_prices_task',
        'schedule': timedelta(seconds=120),
    },
    'sales_update_task': {
        'task': 'core.tasks.sales_update_task',
        'schedule': timedelta(seconds=3600),
    },

}
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
