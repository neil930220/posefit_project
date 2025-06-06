from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Weight record endpoints
    path('weight-records/', views.WeightRecordListCreateView.as_view(), name='weight-records'),
    path('weight-records/<int:pk>/', views.WeightRecordDetailView.as_view(), name='weight-record-detail'),
    
    # Goal progress endpoints
    path('goals/', views.GoalProgressListCreateView.as_view(), name='goals'),
    path('goals/<int:pk>/', views.GoalProgressDetailView.as_view(), name='goal-detail'),
    
    # Calculation endpoints
    path('calculate-bmr-tdee/', views.calculate_bmr_tdee, name='calculate-bmr-tdee'),
    
    # Analytics endpoints
    path('analytics/', views.weight_progress_analytics, name='weight-analytics'),
    path('dashboard/', views.dashboard_summary, name='dashboard-summary'),
] 