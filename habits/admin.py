from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'time', 'place', 'is_pleasant', 'is_public')
    list_filter = ('is_pleasant', 'is_public', 'periodicity', 'created_at')
    search_fields = ('action', 'place', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'place', 'time')
        }),
        ('Характеристики привычки', {
            'fields': ('is_pleasant', 'related_habit', 'periodicity', 'execution_time')
        }),
        ('Вознаграждение и видимость', {
            'fields': ('reward', 'is_public')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
