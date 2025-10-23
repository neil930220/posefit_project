from django.urls import path
from . import views

app_name = 'exercise'

urlpatterns = [
    # 運動類型管理
    path('exercise-types/', views.ExerciseTypeListView.as_view(), name='exercise-types'),
    
    # 運動訓練記錄管理
    path('sessions/', views.ExerciseSessionViewSet.as_view({'get': 'list', 'post': 'create'}), name='sessions'),
    path('sessions/<int:pk>/', views.ExerciseSessionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='session-detail'),
    
    # 姿勢分析
    path('analyze-pose/', views.analyze_pose, name='analyze-pose'),
    path('pose-feedback/', views.get_pose_feedback, name='pose-feedback'),
    
    # 訓練記錄管理
    path('start-session/', views.start_exercise_session, name='start-session'),
    path('end-session/<int:session_id>/', views.end_exercise_session, name='end-session'),
    
    # 歷史記錄和統計
    path('history/', views.get_exercise_history, name='history'),
    path('session/<int:session_id>/analyses/', views.get_session_analyses, name='session-analyses'),
    path('statistics/', views.get_exercise_statistics, name='statistics'),
]
