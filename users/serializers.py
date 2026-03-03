# users/serializers.py
from rest_framework import serializers
from django.core.validators import MinValueValidator
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'telegram_chat_id')
        extra_kwargs = {
            'email': {'required': True},
            'telegram_chat_id': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            telegram_chat_id=validated_data.get('telegram_chat_id'),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации о пользователе"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'telegram_chat_id')
        read_only_fields = ('id', 'username', 'email')


class UserTelegramSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления Telegram chat_id"""
    telegram_chat_id = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[MinValueValidator(1, message="Telegram chat_id должен быть положительным числом.")]
    )

    class Meta:
        model = User
        fields = ('telegram_chat_id',)

    def validate_telegram_chat_id(self, value):
        try:
            chat_id = int(value)
            if chat_id <= 0:
                raise serializers.ValidationError("Telegram chat_id должен быть положительным числом.")
            return str(chat_id)
        except (ValueError, TypeError):
            raise serializers.ValidationError("Telegram chat_id должен быть валидным числом.")

    def update(self, instance, validated_data):
        instance.telegram_chat_id = validated_data['telegram_chat_id']
        instance.save(update_fields=['telegram_chat_id'])
        return instance