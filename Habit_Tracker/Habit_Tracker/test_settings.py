DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Отключаем Celery в тестах
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Отключаем отправку Telegram сообщений в тестах
TELEGRAM_BOT_TOKEN = 'test-token'

# Ускоряем тесты
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Отключаем валидацию паролей в тестах
AUTH_PASSWORD_VALIDATORS = []
