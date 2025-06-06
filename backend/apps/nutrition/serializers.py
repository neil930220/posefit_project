from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, WeightRecord, GoalProgress

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    bmr = serializers.SerializerMethodField()
    tdee = serializers.SerializerMethodField()
    current_weight = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'age', 'gender', 'height', 'activity_level', 
            'goal', 'target_weight', 'bmr', 'tdee', 'current_weight',
            'created_at', 'updated_at'
        ]

    def get_bmr(self, obj):
        latest_record = obj.user.weight_records.first()
        if latest_record:
            return obj.calculate_bmr(latest_record.weight)
        return None

    def get_tdee(self, obj):
        latest_record = obj.user.weight_records.first()
        if latest_record:
            return obj.calculate_tdee(latest_record.weight)
        return None

    def get_current_weight(self, obj):
        latest_record = obj.user.weight_records.first()
        return latest_record.weight if latest_record else None


class WeightRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightRecord
        fields = ['id', 'weight', 'date', 'notes', 'bmr', 'tdee', 'created_at']
        read_only_fields = ['bmr', 'tdee']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class GoalProgressSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    remaining_weight = serializers.ReadOnlyField()

    class Meta:
        model = GoalProgress
        fields = [
            'id', 'start_weight', 'target_weight', 'current_weight',
            'start_date', 'target_date', 'progress_percentage', 
            'remaining_weight', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BMRTDEECalculationSerializer(serializers.Serializer):
    """Serializer for calculating BMR/TDEE without saving"""
    age = serializers.IntegerField(min_value=1, max_value=120)
    gender = serializers.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    height = serializers.FloatField(min_value=50, max_value=300)
    weight = serializers.FloatField(min_value=20, max_value=500)
    activity_level = serializers.ChoiceField(choices=UserProfile.ACTIVITY_LEVEL_CHOICES)

    def calculate(self):
        """Calculate BMR and TDEE based on input data"""
        data = self.validated_data
        
        # Calculate BMR using Mifflin-St Jeor Equation
        if data['gender'] == 'M':
            bmr = 88.362 + (13.397 * data['weight']) + (4.799 * data['height']) - (5.677 * data['age'])
        else:
            bmr = 447.593 + (9.247 * data['weight']) + (3.098 * data['height']) - (4.330 * data['age'])
        
        # Calculate TDEE
        tdee = bmr * data['activity_level']
        
        return {
            'bmr': round(bmr, 2),
            'tdee': round(tdee, 2),
            'input_data': data
        }


class WeightProgressSerializer(serializers.Serializer):
    """Serializer for weight progress analytics"""
    date_range = serializers.ChoiceField(
        choices=[
            ('7d', 'Last 7 days'),
            ('30d', 'Last 30 days'),
            ('90d', 'Last 90 days'),
            ('6m', 'Last 6 months'),
            ('1y', 'Last year'),
            ('all', 'All time')
        ],
        default='30d'
    ) 