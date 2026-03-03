# Habit Tracker API

Сервис для отслеживания полезных привычек с интеграцией Telegram-уведомлений. Проект помогает формировать полезные привычки по методике из книги "Атомные привычки" Джеймса Клира.

## Содержание
- [О проекте](#о-проекте)
- [Модели данных](#модели-данных)
- [Функциональность](#функциональность)
- [API Endpoints](#api-endpoints)
  - [Пользователи](#пользователи)
  - [Привычки](#привычки)
- [Интеграция с Telegram](#интеграция-с-telegram)
- [Технологии](#технологии)
- [Установка и запуск](#установка-и-запуск)

## О проекте

Habit Tracker позволяет пользователям создавать полезные привычки, отслеживать их выполнение и получать напоминания в Telegram. Сервис реализует правила формирования привычек:

- **Полезная привычка** — действие, которое пользователь совершает регулярно
- **Приятная привычка** — вознаграждение за выполнение полезной привычки
- Каждая привычка описывается формулой: "я буду [ДЕЙСТВИЕ] в [ВРЕМЯ] в [МЕСТО]"
- Время выполнения привычки не должно превышать 120 секунд
- Периодичность выполнения — от 1 до 7 дней

## Модели данных

### Habit (Привычка)

| Поле | Тип | Описание |
|------|-----|----------|
| user | ForeignKey(User) | Создатель привычки |
| place | CharField | Место выполнения |
| time | TimeField | Время выполнения |
| action | CharField | Действие |
| is_pleasant | BooleanField | Признак приятной привычки |
| related_habit | ForeignKey(Habit) | Связанная привычка (для полезных) |
| periodicity | PositiveIntegerField | Периодичность (дни, 1-7) |
| reward | CharField | Вознаграждение |
| execution_time | PositiveIntegerField | Время на выполнение (сек, ≤120) |
| is_public | BooleanField | Публичность |
| created_at | DateTimeField | Дата создания |
| updated_at | DateTimeField | Дата обновления |

## Функциональность

- 🔐 Регистрация и JWT-авторизация
- 📝 CRUD операций с привычками
- 👀 Просмотр публичных привычек других пользователей
- ✅ Валидация правил формирования привычек
- 🔔 Telegram-уведомления о необходимости выполнить привычку
- 📄 Пагинация (5 привычек на страницу)
- 🔒 Разграничение прав доступа

## API Endpoints

Базовый URL: `/api/`

### Пользователи

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/users/register/` | Регистрация нового пользователя | Public |
| POST | `/users/login/` | Авторизация, получение JWT токенов | Public |
| POST | `/users/token/refresh/` | Обновление access токена | Public |
| GET | `/users/profile/` | Получение профиля | Authenticated |
| PATCH | `/users/profile/` | Обновление профиля | Authenticated |
| PATCH | `/users/profile/telegram/` | Привязка Telegram chat ID | Authenticated |

#### Пример запроса на регистрацию:
POST /api/users/register/
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "telegram_chat_id": "123456789"
}
```

#### Пример ответа при регистрации/авторизации:
```json
{
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "telegram_chat_id": "123456789"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Привычки

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/habits/habits/` | Список привычек текущего пользователя (с пагинацией) | Authenticated |
| POST | `/habits/habits/` | Создание новой привычки | Authenticated |
| GET | `/habits/habits/<id>/` | Детальная информация о привычке | Owner |
| PUT | `/habits/habits/<id>/` | Полное обновление привычки | Owner |
| PATCH | `/habits/habits/<id>/` | Частичное обновление привычки | Owner |
| DELETE | `/habits/habits/<id>/` | Удаление привычки | Owner |
| GET | `/habits/habits/public/` | Список публичных привычек | Authenticated |

#### Пример создания привычки:
POST /api/habits/habits/
```json
{
    "place": "парк",
    "time": "19:00:00",
    "action": "прогулка вокруг квартала",
    "is_pleasant": false,
    "related_habit": null,
    "periodicity": 1,
    "reward": "десерт",
    "execution_time": 60,
    "is_public": true
}
```

#### Пример ответа:
```json
{
    "id": 1,
    "user": 1,
    "place": "парк",
    "time": "19:00:00",
    "action": "прогулка вокруг квартала",
    "is_pleasant": false,
    "related_habit": null,
    "periodicity": 1,
    "reward": "десерт",
    "execution_time": 60,
    "is_public": true,
    "created_at": "2024-01-20T10:00:00Z",
    "updated_at": "2024-01-20T10:00:00Z"
}
```

#### Пагинация
Список привычек возвращается с пагинацией по 5 элементов:
```json
{
    "count": 15,
    "next": "http://localhost:8000/api/habits/habits/?page=2",
    "previous": null,
    "results": [...]
}
```

## Интеграция с Telegram

Сервис автоматически отправляет напоминания о привычках в Telegram. Для получения уведомлений необходимо:

1. Найти бота `@habits_tracker_bot` в Telegram
2. Отправить боту любое сообщение (для получения `chat_id`)
3. Привязать `chat_id` к профилю через API:
PATCH /api/users/profile/telegram/
```json
{
    "telegram_chat_id": "123456789"
}
```

### Telegram-утилиты

Проект включает функции для работы с Telegram API:
- `get_telegram_bot_info()` — проверка статуса бота
- `send_test_message(chat_id, message)` — отправка тестового сообщения через Celery

## Технологии

- **Backend**: Django 4.2, Django REST Framework
- **База данных**: PostgreSQL
- **Аутентификация**: JWT (djangorestframework-simplejwt)
- **Фоновые задачи**: Celery, Redis
- **Документация**: drf-yasg / OpenAPI
- **CORS**: django-cors-headers
- **Фильтрация**: django-filter

## Установка и запуск

### Требования
- Python 3.10+
- PostgreSQL
- Redis
- Telegram Bot Token (получить у @BotFather)

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/habit-tracker.git
cd habit-tracker
```

### 2. Настройка окружения
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows

pip install -r requirements.txt
```

### 3. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=habit_tracker
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 4. Создание базы данных
```bash
createdb habit_tracker
```

### 5. Применение миграций
```bash
python manage.py migrate
```

### 6. Запуск сервера
```bash
python manage.py runserver
```

### 7. Запуск Celery (для уведомлений)
```bash
# В отдельном терминале
celery -A config worker --loglevel=info

# Для периодических задач
celery -A config beat --loglevel=info
```

### 8. Документация API
После запуска сервера документация доступна по адресам:
- Swagger: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Валидация привычек

API включает следующие правила валидации:

1. **Нельзя одновременно указать вознаграждение и связанную привычку**
2. **Время выполнения не должно превышать 120 секунд**
3. **Связанной привычкой может быть только приятная привычка**
4. **У приятной привычки не может быть вознаграждения или связанной привычки**
5. **Периодичность должна быть от 1 до 7 дней**

## Права доступа

- Пользователи имеют доступ только к своим привычкам
- Публичные привычки доступны для просмотра всем авторизованным пользователям
- Изменение/удаление доступно только владельцу привычки