from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
import pytz

User = get_user_model()


def get_today_date():
    """Get today's date in the configured timezone"""
    # Get the configured timezone
    tz = pytz.timezone(settings.TIME_ZONE)
    # Get current time in that timezone
    now_in_tz = timezone.now().astimezone(tz)
    return now_in_tz.date()


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        (1.2, 'Sedentary (little/no exercise)'),
        (1.375, 'Light activity (light exercise 1-3 days/week)'),
        (1.55, 'Moderate activity (moderate exercise 3-5 days/week)'),
        (1.725, 'Very active (hard exercise 6-7 days/week)'),
        (1.9, 'Extra active (very hard exercise, physical job)'),
    ]
    
    GOAL_CHOICES = [
        ('maintain', 'Maintain Weight'),
        ('lose', 'Lose Weight'),
        ('gain', 'Gain Weight'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    height = models.FloatField(help_text="Height in cm")
    activity_level = models.FloatField(choices=ACTIVITY_LEVEL_CHOICES)
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES, default='maintain')
    target_weight = models.FloatField(help_text="Target weight in kg", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def calculate_bmr(self, weight):
        """Calculate BMR using Mifflin-St Jeor Equation"""
        if self.gender == 'M':
            # Men: BMR = 88.362 + (13.397 × weight in kg) + (4.799 × height in cm) - (5.677 × age in years)
            bmr = 88.362 + (13.397 * weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            # Women: BMR = 447.593 + (9.247 × weight in kg) + (3.098 × height in cm) - (4.330 × age in years)
            bmr = 447.593 + (9.247 * weight) + (3.098 * self.height) - (4.330 * self.age)
        return round(bmr, 2)
    
    def calculate_tdee(self, weight):
        """Calculate TDEE by multiplying BMR with activity level"""
        bmr = self.calculate_bmr(weight)
        tdee = bmr * self.activity_level
        return round(tdee, 2)


class WeightRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weight_records')
    weight = models.FloatField(help_text="Weight in kg")
    date = models.DateField(default=get_today_date)
    notes = models.TextField(blank=True, null=True)
    bmr = models.FloatField(null=True, blank=True, help_text="BMR calculated at this weight")
    tdee = models.FloatField(null=True, blank=True, help_text="TDEE calculated at this weight")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.weight}kg on {self.date}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate BMR and TDEE when saving
        try:
            profile = self.user.userprofile
            self.bmr = profile.calculate_bmr(self.weight)
            self.tdee = profile.calculate_tdee(self.weight)
        except UserProfile.DoesNotExist:
            pass
        super().save(*args, **kwargs)


class GoalProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goal_progress')
    start_weight = models.FloatField(help_text="Starting weight in kg")
    target_weight = models.FloatField(help_text="Target weight in kg")
    current_weight = models.FloatField(help_text="Current weight in kg")
    start_date = models.DateField()
    target_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Goal: {self.start_weight}kg → {self.target_weight}kg"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.start_weight == self.target_weight:
            return 100
        
        weight_change = abs(self.current_weight - self.start_weight)
        total_change = abs(self.target_weight - self.start_weight)
        
        if total_change == 0:
            return 100
        
        progress = (weight_change / total_change) * 100
        return min(100, round(progress, 2))
    
    @property
    def remaining_weight(self):
        """Calculate remaining weight to reach goal"""
        return abs(self.target_weight - self.current_weight) 