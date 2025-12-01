from django.core.exceptions import ValidationError
from rest_framework.serializers import ValidationError as DRFValidationError


class HabitValidator:
    """Валидатор для проверки бизнес-логики привычек"""

    def __call__(self, data):
        related_habit = data.get('related_habit')
        reward = data.get('reward')
        is_pleasant = data.get('is_pleasant', False)
        execution_time = data.get('execution_time')
        periodicity = data.get('periodicity', 1)

        # 1. Исключить одновременный выбор связанной привычки и указания вознаграждения
        if related_habit and reward:
            raise DRFValidationError({
                'non_field_errors': ['Нельзя одновременно указывать связанную привычку и вознаграждение']
            })

        # 2. Время выполнения должно быть не больше 120 секунд
        if execution_time and execution_time > 120:
            raise DRFValidationError({
                'execution_time': ['Время выполнения не должно превышать 120 секунд']
            })

        # 3. В связанные привычки могут попадать только привычки с признаком приятной привычки
        if related_habit and not related_habit.is_pleasant:
            raise DRFValidationError({
                'related_habit': ['Связанная привычка должна быть приятной']
            })

        # 4. У приятной привычки не может быть вознаграждения или связанной привычки
        if is_pleasant:
            if reward:
                raise DRFValidationError({
                    'reward': ['У приятной привычки не может быть вознаграждения']
                })
            if related_habit:
                raise DRFValidationError({
                    'related_habit': ['У приятной привычки не может быть связанной привычки']
                })

        # 5. Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if periodicity and periodicity > 7:
            raise DRFValidationError({
                'periodicity': ['Нельзя выполнять привычку реже, чем 1 раз в 7 дней']
            })


def validate_execution_time(value):
    """Валидатор времени выполнения"""
    if value > 120:
        raise ValidationError('Время выполнения не должно превышать 120 секунд')
    return value


def validate_periodicity(value):
    """Валидатор периодичности"""
    if value > 7:
        raise ValidationError('Периодичность не может быть больше 7 дней')
    return value


def validate_related_habit(value):
    """Валидатор связанной привычки"""
    if value and not value.is_pleasant:
        raise ValidationError('Связанная привычка должна быть приятной')
    return value
