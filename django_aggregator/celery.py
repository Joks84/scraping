from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_aggregator.settings')

app = Celery('django_aggregator')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# We have to be careful regarding the task's path.
# If we don't provide a proper path, Celery won't be able to recognize the task and it will throw error.
app.conf.beat_schedule = {
    'scraping-remote-co': {
        'task': 'django_jobs.tasks.scrape_content_from_remote_co',
        # Execute on Mondays and Fridays.
        'schedule': crontab(0, 0, day_of_week=[1, 5]),
    },
    'scraping-we-work-remotely': {
        'task': 'django_jobs.tasks.scrape_weworkremotely',
        # Execute on Tuesdays and Saturdays.
        'schedule': crontab(0, 0, day_of_week=[2, 5]),
    },
    'scraping-remotive': {
        'task': 'django_jobs.tasks.scrape_remotive',
        # Execute on Wednesdays and Sundays.
        'schedule': crontab(0, 0, day_of_week=[3, 6]),
    },

}