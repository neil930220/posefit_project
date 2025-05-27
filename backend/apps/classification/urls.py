from django.urls import path
from .views import UploadAndAnalyze

urlpatterns = [
    path('api/upload/', UploadAndAnalyze.as_view(), name='api_upload_analyze'),
]