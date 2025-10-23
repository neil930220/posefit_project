from django.contrib import admin
from .models import (
    ExerciseType, ExerciseSession, PoseAnalysis, 
    ExerciseTemplate, PoseKeypoint
)


@admin.register(ExerciseType)
class ExerciseTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty_level', 'created_at']
    list_filter = ['difficulty_level', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PoseKeypoint)
class PoseKeypointAdmin(admin.ModelAdmin):
    list_display = ['name', 'index', 'description']
    list_filter = ['index']
    search_fields = ['name', 'description']
    ordering = ['index']


@admin.register(ExerciseTemplate)
class ExerciseTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'exercise_type', 'created_at']
    list_filter = ['exercise_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExerciseSession)
class ExerciseSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise_type', 'session_name', 'start_time', 'total_reps', 'average_score']
    list_filter = ['exercise_type', 'start_time', 'user']
    search_fields = ['user__username', 'session_name', 'notes']
    readonly_fields = ['start_time', 'total_duration', 'average_score', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'exercise_type')


@admin.register(PoseAnalysis)
class PoseAnalysisAdmin(admin.ModelAdmin):
    list_display = ['session', 'frame_number', 'pose_score', 'confidence_score', 'timestamp']
    list_filter = ['session__exercise_type', 'timestamp']
    search_fields = ['session__user__username', 'ai_feedback']
    readonly_fields = ['timestamp', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session__user', 'session__exercise_type')
