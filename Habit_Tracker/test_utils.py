from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


def create_authenticated_client(user=None):
    """
    Создает аутентифицированный API клиент
    """
    if user is None:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    return client, user


def create_test_habit(user, **kwargs):
    """
    Создает тестовую привычку
    """
    default_data = {
        'place': 'Тестовое место',
        'time': '10:00:00',
        'action': 'Тестовое действие',
        'is_pleasant': False,
        'periodicity': 1,
        'execution_time': 60,
        'is_public': True
    }
    default_data.update(kwargs)

    from habits.models import Habit
    return Habit.objects.create(user=user, **default_data)
