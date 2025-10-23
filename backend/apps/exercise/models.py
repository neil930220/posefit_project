"""
Exercise and Pose Detection Models
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.common.models import BaseModel


class ExerciseType(models.Model):
    """運動類型定義"""
    name = models.CharField(max_length=100, help_text="運動名稱")
    description = models.TextField(blank=True, help_text="運動描述")
    difficulty_level = models.IntegerField(
        choices=[(1, '初級'), (2, '中級'), (3, '高級')],
        default=1,
        help_text="難度等級"
    )
    target_muscles = models.JSONField(
        default=list,
        help_text="目標肌群列表"
    )
    instructions = models.JSONField(
        default=list,
        help_text="動作要領說明"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PoseKeypoint(models.Model):
    """姿勢關鍵點定義"""
    name = models.CharField(max_length=50, unique=True, help_text="關鍵點名稱")
    index = models.IntegerField(unique=True, help_text="OpenPose 關鍵點索引")
    description = models.TextField(blank=True, help_text="關鍵點描述")
    
    class Meta:
        ordering = ['index']

    def __str__(self):
        return f"{self.name} ({self.index})"


class ExerciseSession(BaseModel):
    """運動訓練記錄"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exercise_sessions'
    )
    exercise_type = models.ForeignKey(
        ExerciseType,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_name = models.CharField(max_length=200, help_text="訓練名稱")
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_duration = models.DurationField(null=True, blank=True)
    total_reps = models.IntegerField(default=0, help_text="總次數")
    average_score = models.FloatField(null=True, blank=True, help_text="平均分數")
    notes = models.TextField(blank=True, help_text="訓練備註")
    
    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.user.username} - {self.exercise_type.name} ({self.start_time})"


class PoseAnalysis(BaseModel):
    """姿勢分析記錄"""
    session = models.ForeignKey(
        ExerciseSession,
        on_delete=models.CASCADE,
        related_name='pose_analyses'
    )
    frame_number = models.IntegerField(help_text="幀數")
    timestamp = models.DateTimeField(default=timezone.now)
    
    # OpenPose 關鍵點數據
    keypoints = models.JSONField(help_text="關鍵點座標和信心度")
    
    # 姿勢分析結果
    pose_score = models.FloatField(help_text="姿勢分數 (0-100)")
    confidence_score = models.FloatField(help_text="信心度分數 (0-1)")
    
    # 錯誤檢測
    detected_errors = models.JSONField(
        default=list,
        help_text="檢測到的姿勢錯誤"
    )
    
    # AI 建議
    ai_feedback = models.TextField(blank=True, help_text="AI 生成的建議")
    
    # 原始影像 (可選)
    image = models.ImageField(
        upload_to="pose_analysis/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="分析時的影像截圖"
    )

    class Meta:
        ordering = ['session', 'frame_number']

    def __str__(self):
        return f"{self.session} - Frame {self.frame_number} (Score: {self.pose_score})"


class ExerciseTemplate(models.Model):
    """運動模板定義"""
    exercise_type = models.ForeignKey(
        ExerciseType,
        on_delete=models.CASCADE,
        related_name='templates'
    )
    name = models.CharField(max_length=200, help_text="模板名稱")
    description = models.TextField(blank=True, help_text="模板描述")
    
    # 標準姿勢關鍵點 (用於比較)
    standard_keypoints = models.JSONField(help_text="標準姿勢關鍵點")
    
    # 評分標準
    scoring_criteria = models.JSONField(
        default=dict,
        help_text="評分標準和權重"
    )
    
    # 錯誤檢測規則
    error_detection_rules = models.JSONField(
        default=list,
        help_text="錯誤檢測規則"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['exercise_type', 'name']

    def __str__(self):
        return f"{self.exercise_type.name} - {self.name}"
