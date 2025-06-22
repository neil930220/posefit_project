from django.contrib import admin
from .models import UserProfile, WeightRecord, GoalProgress


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'height', 'activity_level', 'goal', 'created_at']
    list_filter = ['gender', 'activity_level', 'goal', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'age', 'gender', 'height')
        }),
        ('Health Goals', {
            'fields': ('activity_level', 'goal', 'target_weight')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WeightRecord)
class WeightRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'weight', 'date', 'bmr', 'tdee', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['bmr', 'tdee', 'created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Weight Information', {
            'fields': ('user', 'weight', 'date', 'notes')
        }),
        ('Calculated Values', {
            'fields': ('bmr', 'tdee'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GoalProgress)
class GoalProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_weight', 'current_weight', 'target_weight', 'progress_percentage', 'start_date', 'target_date']
    list_filter = ['start_date', 'target_date', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['progress_percentage', 'remaining_weight', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Goal Information', {
            'fields': ('user', 'start_weight', 'current_weight', 'target_weight')
        }),
        ('Timeline', {
            'fields': ('start_date', 'target_date')
        }),
        ('Progress', {
            'fields': ('progress_percentage', 'remaining_weight'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 