from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class Command(BaseCommand):
    help = 'Setup periodic tasks for habit reminders'

    def handle(self, *args, **options):
        # Создаем расписание для ежедневной проверки в 6:00
        schedule, created = CrontabSchedule.objects.get_or_create(
            hour=6,
            minute=0,
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        # Задача для ежедневной проверки привычек
        daily_check_task, created = PeriodicTask.objects.get_or_create(
            name='Check daily habits',
            task='habits.tasks.check_daily_habits',
            defaults={
                'crontab': schedule,
                'description': 'Ежедневная проверка привычек для отправки напоминаний',
            }
        )

        # Создаем расписание для еженедельных отчетов (понедельник, 9:00)
        weekly_schedule, created = CrontabSchedule.objects.get_or_create(
            hour=9,
            minute=0,
            day_of_week=1,  # Понедельник
            day_of_month='*',
            month_of_year='*',
        )

        # Задача для еженедельных отчетов
        weekly_summary_task, created = PeriodicTask.objects.get_or_create(
            name='Send weekly habit summary',
            task='habits.tasks.send_weekly_summary',
            defaults={
                'crontab': weekly_schedule,
                'description': 'Еженедельный отчет по привычкам',
            }
        )

        self.stdout.write(
            self.style.SUCCESS('Периодические задачи успешно настроены')
        )
