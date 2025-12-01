from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Habit
from .serializers import HabitSerializer, PublicHabitSerializer
from .permissions import IsOwner


class HabitListCreateView(generics.ListCreateAPIView):
    """Список привычек текущего пользователя и создание новой"""
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['time', 'created_at']
    ordering = ['time']

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, обновление и удаление привычки"""
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class PublicHabitListView(generics.ListAPIView):
    """Список публичных привычек"""
    serializer_class = PublicHabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Habit.objects.filter(is_public=True)
    pagination_class = None  # Отключаем пагинацию для публичных привычек
