# history/models.py

from django.conf import settings
from django.db import models

class FoodEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="The logged‐in user (blank if anonymous)"
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text="Fallback identifier for anonymous users"
    )
    image = models.ImageField(
        upload_to="history/%Y/%m/%d/",
        help_text="Uploaded food image"
    )
    detections = models.JSONField(
        help_text="List of detected items and their calories"
    )
    total_calories = models.IntegerField(
        help_text="Sum of calories for this entry"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this scan was performed"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        owner = self.user or f"anon[{self.session_key}]"
        return f"{owner} @ {self.created_at:%Y-%m-%d %H:%M}"
