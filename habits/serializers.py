from rest_framework import serializers
from .models import Habit
from .validators import HabitValidator


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек"""

    class Meta:
        model = Habit
        fields = (
            'id', 'user', 'place', 'time', 'action', 'is_pleasant',
            'related_habit', 'periodicity', 'reward', 'execution_time',
            'is_public', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def validate(self, data):
        """Применяем кастомные валидаторы"""
        validator = HabitValidator()
        validator(data)
        return data

    def create(self, validated_data):
        """Автоматически устанавливаем текущего пользователя"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек (только для чтения)"""
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Habit
        fields = (
            'id', 'user', 'place', 'time', 'action', 'periodicity',
            'execution_time', 'created_at'
        )
        read_only_fields = fields
