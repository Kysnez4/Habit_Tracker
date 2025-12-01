from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Habit(models.Model):
    """Модель привычки"""

    PERIODICITY_CHOICES = [
        (1, 'Ежедневно'),
        (2, 'Раз в 2 дня'),
        (3, 'Раз в 3 дня'),
        (4, 'Раз в 4 дня'),
        (5, 'Раз в 5 дней'),
        (6, 'Раз в 6 дней'),
        (7, 'Раз в неделю'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )
    place = models.CharField(
        max_length=255,
        verbose_name='Место',
        help_text='Место, в котором необходимо выполнять привычку'
    )
    time = models.TimeField(
        verbose_name='Время',
        help_text='Время, когда необходимо выполнять привычку'
    )
    action = models.CharField(
        max_length=255,
        verbose_name='Действие',
        help_text='Действие, которое представляет собой привычка'
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Признак приятной привычки'
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_habits',
        verbose_name='Связанная привычка',
        help_text='Привычка, которая связана с другой привычкой'
    )
    periodicity = models.PositiveSmallIntegerField(
        choices=PERIODICITY_CHOICES,
        default=1,
        verbose_name='Периодичность',
        help_text='Периодичность выполнения привычки в днях',
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Вознаграждение',
        help_text='Чем пользователь должен себя вознаградить после выполнения'
    )
    execution_time = models.PositiveSmallIntegerField(
        verbose_name='Время на выполнение',
        help_text='Время в секундах, которое потратит пользователь на выполнение привычки',
        validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Признак публичности'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.action} в {self.time}"


class HabitCompletion(models.Model):
    """Модель для отслеживания выполнения привычек"""
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='completions',
        verbose_name='Привычка'
    )
    completion_date = models.DateField(
        verbose_name='Дата выполнения',
        auto_now_add=True
    )
    completed_at = models.DateTimeField(
        verbose_name='Время выполнения',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Выполнение привычки'
        verbose_name_plural = 'Выполнения привычек'
        unique_together = ('habit', 'completion_date')

    def __str__(self):
        return f"{self.habit.action} - {self.completion_date}"
