from unittest.mock import patch, MagicMock
from django.test import TestCase
from users.models import User
from .models import Habit
from .tasks import send_telegram_reminder, check_daily_habits, create_reminder_message


class TaskTests(TestCase):
    """Тесты Celery задач"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            telegram_chat_id='123456'
        )

        self.habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Пить воду',
            is_pleasant=False,
            periodicity=1,
            reward='Кофе',
            execution_time=30
        )

    @patch('habits.tasks.requests.post')
    def test_send_telegram_reminder_success(self, mock_post):
        """Тест успешной отправки Telegram напоминания"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        send_telegram_reminder(self.habit.id)

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('sendMessage', call_args[0][0])
        self.assertEqual(call_args[1]['json']['chat_id'], '123456')

    @patch('habits.tasks.requests.post')
    def test_send_telegram_reminder_no_chat_id(self, mock_post):
        """Тест отправки напоминания пользователю без chat ID"""
        self.user.telegram_chat_id = None
        self.user.save()

        send_telegram_reminder(self.habit.id)

        mock_post.assert_not_called()

    def test_send_telegram_reminder_nonexistent_habit(self):
        """Тест отправки напоминания для несуществующей привычки"""
        send_telegram_reminder(999)  # Несуществующий ID

    def test_create_reminder_message(self):
        """Тест создания сообщения напоминания"""
        message = create_reminder_message(self.habit)

        self.assertIn('Пить воду', message)
        self.assertIn('Дом', message)
        self.assertIn('Кофе', message)
        self.assertIn('30 секунд', message)

    def test_create_reminder_message_with_related_habit(self):
        """Тест создания сообщения со связанной привычкой"""
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:30:00',
            action='Читать книгу',
            is_pleasant=True,
            periodicity=1,
            execution_time=60
        )

        self.habit.related_habit = pleasant_habit
        self.habit.reward = None
        self.habit.save()

        message = create_reminder_message(self.habit)

        self.assertIn('Читать книгу', message)
        self.assertNotIn('Вознаграждение', message)

    @patch('habits.tasks.send_telegram_reminder.delay')
    def test_check_daily_habits(self, mock_delay):
        """Тест ежедневной проверки привычек"""
        # Создаем привычку, которая должна быть проверена сегодня
        check_daily_habits()

        # Проверяем, что задача была вызвана
        mock_delay.assert_called()
