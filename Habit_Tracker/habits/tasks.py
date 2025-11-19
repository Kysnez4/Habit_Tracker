from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import requests
from django.conf import settings

from users.models import User
from .models import Habit


@shared_task
def send_telegram_reminder(habit_id):
    """
    Отправка напоминания о привычке через Telegram
    """
    try:
        habit = Habit.objects.get(id=habit_id)
        user = habit.user

        if not user.telegram_chat_id:
            print(f"У пользователя {user.username} не установлен Telegram chat ID")
            return

        message = create_reminder_message(habit)

        # Отправка сообщения через Telegram Bot API
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': user.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        print(f"Напоминание отправлено пользователю {user.username}")

    except Habit.DoesNotExist:
        print(f"Привычка с ID {habit_id} не найдена")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


@shared_task
def check_daily_habits():
    """
    Ежедневная проверка привычек для отправки напоминаний
    Запускается каждый день в 6:00 утра
    """
    now = timezone.now()

    # Получаем все активные привычки
    habits = Habit.objects.all()

    for habit in habits:
        # Проверяем, нужно ли отправлять напоминание сегодня
        if should_send_reminder_today(habit, now.date()):
            # Проверяем время привычки (в пределах 10 минут до времени выполнения)
            habit_time = habit.time
            time_diff = datetime.combine(now.date(), habit_time) - now
            if timedelta(minutes=0) <= time_diff <= timedelta(minutes=10):
                # Отправляем напоминание асинхронно
                send_telegram_reminder.delay(habit.id)


def create_reminder_message(habit):
    """
    Создание текста напоминания
    """
    base_message = (
        f"<b>Напоминание о привычке</b>\n\n"
        f"<b>Действие:</b> {habit.action}\n"
        f"<b>Место:</b> {habit.place}\n"
        f"<b>Время:</b> {habit.time.strftime('%H:%M')}\n"
        f"<b>Время на выполнение:</b> {habit.execution_time} секунд\n"
    )

    if habit.reward:
        base_message += "<b>Вознаграждение:</b> {habit.reward}\n"
    elif habit.related_habit:
        base_message += "<b>Связанная привычка:</b> {habit.related_habit.action}\n"

    base_message += "\nУдачи в выполнении!"

    return base_message


def should_send_reminder_today(habit, today):
    """
    Проверяет, нужно ли отправлять напоминание для привычки сегодня
    на основе периодичности и даты создания
    """
    if habit.periodicity == 1:  # Ежедневно
        return True

    # Для периодических привычек проверяем, подходит ли сегодняшний день
    days_since_creation = (today - habit.created_at.date()).days
    return days_since_creation % habit.periodicity == 0


@shared_task
def send_weekly_summary():
    """
    Отправка еженедельного отчета по привычкам
    """
    users_with_telegram = User.objects.exclude(telegram_chat_id__isnull=True).exclude(telegram_chat_id='')

    for user in users_with_telegram:
        user_habits = Habit.objects.filter(user=user)
        completed_habits_count = user_habits.count()  # Здесь можно добавить логику отслеживания выполнения

        message = (
            f"<b>Еженедельный отчет по привычкам</b>\n\n"
            f"<b>Пользователь:</b> {user.username}\n"
            f"<b>Всего привычек:</b> {user_habits.count()}\n"
            f"<b>Выполнено за неделю:</b> {completed_habits_count}\n"
            f"<b>Публичных привычек:</b> {user_habits.filter(is_public=True).count()}\n\n"
            "Продолжайте в том же духе! 🚀"
        )

        send_telegram_message.delay(user.telegram_chat_id, message)


@shared_task
def send_telegram_message(chat_id, message):
    """
    Универсальная задача для отправки сообщений в Telegram
    """
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        print(f"Сообщение отправлено в чат {chat_id}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
