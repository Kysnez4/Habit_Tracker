import requests
from django.conf import settings


def get_telegram_bot_info():
    """Получение информации о боте"""
    if not settings.TELEGRAM_BOT_TOKEN:
        return None

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def send_test_message(chat_id, message="Тестовое сообщение от бота привычек"):
    """Отправка тестового сообщения"""
    from habits.tasks import send_telegram_message
    send_telegram_message.delay(chat_id, message)
