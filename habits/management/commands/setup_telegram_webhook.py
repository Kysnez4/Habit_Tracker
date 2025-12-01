from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup Telegram webhook'

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN не установлен в настройках')
            )
            return

        self.stdout.write(
            self.style.SUCCESS('Настройка Telegram завершена (режим polling)')
        )
