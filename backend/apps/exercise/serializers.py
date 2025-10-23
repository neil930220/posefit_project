"""
Exercise and Pose Detection Serializers
"""

from rest_framework import serializers
from .models import (
    ExerciseType, ExerciseSession, PoseAnalysis, 
    ExerciseTemplate, PoseKeypoint
)


class ExerciseTypeSerializer(serializers.ModelSerializer):
    """運動類型序列化器"""
    
    class Meta:
        model = ExerciseType
        fields = [
            'id', 'name', 'description', 'difficulty_level',
            'target_muscles', 'instructions', 'created_at', 'updated_at'
        ]


class PoseKeypointSerializer(serializers.ModelSerializer):
    """姿勢關鍵點序列化器"""
    
    class Meta:
        model = PoseKeypoint
        fields = ['id', 'name', 'index', 'description']


class ExerciseTemplateSerializer(serializers.ModelSerializer):
    """運動模板序列化器"""
    exercise_type = ExerciseTypeSerializer(read_only=True)
    
    class Meta:
        model = ExerciseTemplate
        fields = [
            'id', 'exercise_type', 'name', 'description',
            'standard_keypoints', 'scoring_criteria', 
            'error_detection_rules', 'created_at', 'updated_at'
        ]


class PoseAnalysisSerializer(serializers.ModelSerializer):
    """姿勢分析序列化器"""
    
    class Meta:
        model = PoseAnalysis
        fields = [
            'id', 'session', 'frame_number', 'timestamp',
            'keypoints', 'pose_score', 'confidence_score',
            'detected_errors', 'ai_feedback', 'image'
        ]
        read_only_fields = ['id', 'timestamp']


class ExerciseSessionSerializer(serializers.ModelSerializer):
    """運動訓練記錄序列化器"""
    exercise_type = ExerciseTypeSerializer(read_only=True)
    exercise_type_id = serializers.IntegerField(write_only=True)
    user = serializers.StringRelatedField(read_only=True)
    pose_analyses = PoseAnalysisSerializer(many=True, read_only=True)
    
    class Meta:
        model = ExerciseSession
        fields = [
            'id', 'user', 'exercise_type', 'exercise_type_id',
            'session_name', 'start_time', 'end_time', 
            'total_duration', 'total_reps', 'average_score',
            'notes', 'pose_analyses', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'start_time', 'total_duration',
            'average_score', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        exercise_type_id = validated_data.pop('exercise_type_id')
        try:
            exercise_type = ExerciseType.objects.get(id=exercise_type_id)
        except ExerciseType.DoesNotExist:
            raise serializers.ValidationError("Exercise type not found")
        
        validated_data['exercise_type'] = exercise_type
        return super().create(validated_data)


class PoseAnalysisCreateSerializer(serializers.Serializer):
    """姿勢分析創建序列化器"""
    session_id = serializers.IntegerField()
    frame_number = serializers.IntegerField(default=0)
    keypoints = serializers.JSONField()
    pose_score = serializers.FloatField()
    confidence_score = serializers.FloatField()
    detected_errors = serializers.ListField(
        child=serializers.CharField(),
        default=list
    )
    ai_feedback = serializers.CharField(default="")
    
    def validate_session_id(self, value):
        """驗證訓練記錄是否存在"""
        try:
            ExerciseSession.objects.get(id=value)
        except ExerciseSession.DoesNotExist:
            raise serializers.ValidationError("Session not found")
        return value


class ExerciseStatisticsSerializer(serializers.Serializer):
    """運動統計序列化器"""
    total_sessions = serializers.IntegerField()
    total_duration_seconds = serializers.FloatField()
    total_reps = serializers.IntegerField()
    overall_average_score = serializers.FloatField()
    exercise_breakdown = serializers.DictField()


class PoseFeedbackSerializer(serializers.Serializer):
    """姿勢回饋序列化器"""
    keypoints = serializers.JSONField()
    exercise_type = serializers.CharField(default='general')
    feedback = serializers.CharField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
