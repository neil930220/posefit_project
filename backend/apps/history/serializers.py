from rest_framework import serializers
from .models import FoodEntry

class FoodEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodEntry
        fields = [
            "id",
            "user",
            "session_key",
            "image",
            "detections",
            "total_calories",
            "meal_type",
            "created_at",
        ]
        read_only_fields = ["id", "user", "session_key", "created_at"]
