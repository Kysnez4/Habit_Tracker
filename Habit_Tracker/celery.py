import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Habit_Tracker.settings')

app = Celery('Habit_Tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Периодические задачи
app.conf.beat_schedule = {
    'check-daily-habits': {
        'task': 'habits.tasks.check_daily_habits',
        'schedule': crontab(hour=6, minute=0),  # Ежедневно в 6:00
    },
    'send-weekly-summary': {
        'task': 'habits.tasks.send_weekly_summary',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Каждый понедельник в 9:00
    },
}

app.conf.timezone = 'Europe/Moscow'
