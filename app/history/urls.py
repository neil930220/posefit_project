# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodEntryViewSet, HistoryPageView

router = DefaultRouter()
router.register(r'foodentries', FoodEntryViewSet, basename='foodentry')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', HistoryPageView.as_view(), name='history'),
]