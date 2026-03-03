from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from .models import Habit
from .validators import HabitValidator


class HabitModelTest(TestCase):
    """Тесты модели привычки"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Пить кофе',
            is_pleasant=True,
            periodicity=1,
            execution_time=60,
            is_public=True
        )

        self.useful_habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='09:00:00',
            action='Бегать',
            is_pleasant=False,
            periodicity=1,
            reward='Кофе',
            execution_time=120,
            is_public=False
        )

    def test_habit_creation(self):
        """Тест создания привычки"""
        self.assertEqual(self.useful_habit.action, 'Бегать')
        self.assertEqual(self.useful_habit.place, 'Парк')
        self.assertEqual(self.useful_habit.reward, 'Кофе')
        self.assertFalse(self.useful_habit.is_pleasant)
        self.assertTrue(self.useful_habit.is_public)

    def test_habit_str(self):
        """Тест строкового представления"""
        self.assertIn('Бегать', str(self.useful_habit))
        self.assertIn('09:00', str(self.useful_habit))

    def test_pleasant_habit_creation(self):
        """Тест создания приятной привычки"""
        self.assertTrue(self.pleasant_habit.is_pleasant)
        self.assertIsNone(self.pleasant_habit.reward)
        self.assertIsNone(self.pleasant_habit.related_habit)


class HabitValidatorTest(TestCase):
    """Тесты валидаторов привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Пить кофе',
            is_pleasant=True,
            periodicity=1,
            execution_time=60
        )

        self.validator = HabitValidator()

    def test_related_habit_and_reward_validation(self):
        """Тест валидации одновременного указания связанной привычки и вознаграждения"""
        data = {
            'related_habit': self.pleasant_habit,
            'reward': 'Награда',
            'is_pleasant': False
        }

        with self.assertRaises(Exception) as context:
            self.validator(data)

        self.assertIn('Нельзя одновременно указывать', str(context.exception))

    def test_execution_time_validation(self):
        """Тест валидации времени выполнения"""
        data = {
            'execution_time': 150,
            'is_pleasant': False
        }

        with self.assertRaises(Exception) as context:
            self.validator(data)

        self.assertIn('Время выполнения не должно превышать', str(context.exception))

    def test_related_habit_validation(self):
        """Тест валидации связанной привычки"""
        useful_habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='09:00:00',
            action='Бегать',
            is_pleasant=False,
            periodicity=1,
            execution_time=120
        )

        data = {
            'related_habit': useful_habit,
            'is_pleasant': False
        }

        with self.assertRaises(Exception) as context:
            self.validator(data)

        self.assertIn('Связанная привычка должна быть приятной', str(context.exception))

    def test_pleasant_habit_with_reward_validation(self):
        """Тест валидации приятной привычки с вознаграждением"""
        data = {
            'is_pleasant': True,
            'reward': 'Награда'
        }

        with self.assertRaises(Exception) as context:
            self.validator(data)

        self.assertIn('У приятной привычки не может быть вознаграждения', str(context.exception))

    def test_pleasant_habit_with_related_habit_validation(self):
        """Тест валидации приятной привычки со связанной привычкой"""
        data = {
            'is_pleasant': True,
            'related_habit': self.pleasant_habit
        }

        with self.assertRaises(Exception) as context:
            self.validator(data)

        self.assertIn('У приятной привычки не может быть связанной привычки', str(context.exception))

    def test_periodicity_validation(self):
        """Тест валидации периодичности"""
        data = {
            'periodicity': 10,
            'is_pleasant': False
        }

        with self.assertRaises(Exception) as context:
            self.validator(data)

        self.assertIn('Нельзя выполнять привычку реже', str(context.exception))


class HabitAPITest(APITestCase):
    """Тесты API привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Пить кофе',
            is_pleasant=True,
            periodicity=1,
            execution_time=60,
            is_public=True
        )

        self.useful_habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='09:00:00',
            action='Бегать',
            is_pleasant=False,
            periodicity=1,
            reward='Кофе',
            execution_time=120,
            is_public=False
        )

        self.public_habit = Habit.objects.create(
            user=self.other_user,
            place='Спортзал',
            time='10:00:00',
            action='Тренировка',
            is_pleasant=False,
            periodicity=2,
            execution_time=90,
            is_public=True
        )

        self.habit_list_url = reverse('habit-list-create')
        self.habit_detail_url = reverse('habit-detail', kwargs={'pk': self.useful_habit.pk})
        self.public_habits_url = reverse('public-habits')

        self.client.force_authenticate(user=self.user)

    def test_habit_list_authenticated(self):
        """Тест получения списка привычек аутентифицированным пользователем"""
        response = self.client.get(self.habit_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Пагинация

    def test_habit_list_unauthenticated(self):
        """Тест получения списка привычек неаутентифицированным пользователем"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.habit_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_habit_creation(self):
        """Тест создания привычки"""
        data = {
            'place': 'Офис',
            'time': '12:00:00',
            'action': 'Обед',
            'is_pleasant': False,
            'periodicity': 1,
            'reward': 'Десерт',
            'execution_time': 30,
            'is_public': True
        }

        response = self.client.post(self.habit_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 4)
        self.assertEqual(response.data['action'], 'Обед')
        self.assertEqual(response.data['user'], self.user.id)

    def test_habit_creation_invalid_data(self):
        """Тест создания привычки с невалидными данными"""
        data = {
            'place': 'Офис',
            'time': '12:00:00',
            'action': 'Обед',
            'is_pleasant': False,
            'periodicity': 1,
            'reward': 'Десерт',
            'related_habit': self.pleasant_habit.id,  # Нельзя одновременно reward и related_habit
            'execution_time': 150,  # Превышает 120 секунд
            'is_public': True
        }

        response = self.client.post(self.habit_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('execution_time', response.data)

    def test_habit_retrieve(self):
        """Тест получения привычки"""
        response = self.client.get(self.habit_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'Бегать')

    def test_habit_retrieve_other_user(self):
        """Тест получения чужой привычки"""
        other_habit = Habit.objects.create(
            user=self.other_user,
            place='Библиотека',
            time='15:00:00',
            action='Читать',
            is_pleasant=False,
            periodicity=1,
            execution_time=60,
            is_public=False
        )

        url = reverse('habit-detail', kwargs={'pk': other_habit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_habit_update(self):
        """Тест обновления привычки"""
        data = {
            'action': 'Бегать в парке',
            'reward': 'Смузи'
        }

        response = self.client.patch(self.habit_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.useful_habit.refresh_from_db()
        self.assertEqual(self.useful_habit.action, 'Бегать в парке')
        self.assertEqual(self.useful_habit.reward, 'Смузи')

    def test_habit_delete(self):
        """Тест удаления привычки"""
        response = self.client.delete(self.habit_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 2)  # Остаются привычки других пользователей

    def test_public_habits_list(self):
        """Тест получения списка публичных привычек"""
        response = self.client.get(self.public_habits_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны видеть публичные привычки всех пользователей
        public_habits_count = Habit.objects.filter(is_public=True).count()
        self.assertEqual(len(response.data), public_habits_count)

    def test_pagination(self):
        """Тест пагинации"""
        # Создаем дополнительные привычки для тестирования пагинации
        for i in range(10):
            Habit.objects.create(
                user=self.user,
                place=f'Место {i}',
                time='10:00:00',
                action=f'Действие {i}',
                is_pleasant=False,
                periodicity=1,
                execution_time=60
            )

        response = self.client.get(self.habit_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 5)  # PAGE_SIZE = 5
