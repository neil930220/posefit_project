from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions
from .models import FoodEntry
from .serializers import FoodEntrySerializer
from django.views.generic import TemplateView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from datetime import timedelta
import django_filters


class FoodEntryFilter(django_filters.FilterSet):
    # Date range filters
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Predefined time periods
    period = django_filters.ChoiceFilter(
        choices=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
        ],
        method='filter_by_period'
    )
    
    # Calorie range filters
    calories_min = django_filters.NumberFilter(field_name='total_calories', lookup_expr='gte')
    calories_max = django_filters.NumberFilter(field_name='total_calories', lookup_expr='lte')

    class Meta:
        model = FoodEntry
        fields = ['date_from', 'date_to', 'period', 'calories_min', 'calories_max']

    def filter_by_period(self, queryset, name, value):
        now = timezone.now()
        today = now.date()
        
        if value == 'today':
            return queryset.filter(created_at__date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(created_at__date=yesterday)
        elif value == 'this_week':
            start_week = today - timedelta(days=today.weekday())
            return queryset.filter(created_at__date__gte=start_week)
        elif value == 'last_week':
            start_last_week = today - timedelta(days=today.weekday() + 7)
            end_last_week = today - timedelta(days=today.weekday() + 1)
            return queryset.filter(created_at__date__range=[start_last_week, end_last_week])
        elif value == 'this_month':
            start_month = today.replace(day=1)
            return queryset.filter(created_at__date__gte=start_month)
        elif value == 'last_month':
            first_this_month = today.replace(day=1)
            last_month = first_this_month - timedelta(days=1)
            first_last_month = last_month.replace(day=1)
            return queryset.filter(created_at__date__range=[first_last_month, last_month])
        
        return queryset


class HistoryPageView(TemplateView):
    template_name = "index.html"

class FoodEntryViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]      # ← 只接受 JWT
    permission_classes     = [IsAuthenticated]       # ← 一定要登入（JWT）
    serializer_class       = FoodEntrySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = FoodEntryFilter
    ordering_fields = ['created_at', 'total_calories']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        return FoodEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        meal_type = self.request.data.get('meal_type', '').strip()
        valid = {'breakfast', 'lunch', 'dinner'}
        payload = {}
        if meal_type in valid:
            payload['meal_type'] = meal_type
        serializer.save(user=self.request.user, **payload)
