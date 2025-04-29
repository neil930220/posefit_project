from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import FoodEntry

@admin.register(FoodEntry)
class FoodEntryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "total_calories", "created_at")
    list_filter  = ("user", "created_at")
    readonly_fields = ("created_at",)
    search_fields   = ("user__username", "session_key", "detections")