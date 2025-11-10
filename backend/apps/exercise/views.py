"""
Exercise and Pose Detection API Views
"""

import cv2
import numpy as np
import json
import base64
from io import BytesIO
from PIL import Image
from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import (
    ExerciseType, ExerciseSession, PoseAnalysis, 
    ExerciseTemplate, PoseKeypoint
)
from .serializers import (
    ExerciseTypeSerializer, ExerciseSessionSerializer,
    PoseAnalysisSerializer, ExerciseTemplateSerializer
)
from ml_models.pose_detector import get_pose_detector


# 預設運動類型（確保資料存在）
DEFAULT_EXERCISE_TYPES = [
    {
        'name': '深蹲',
        'description': '深蹲是下半身基礎訓練動作，主要鍛鍊大腿前側、臀部和核心肌群。',
        'difficulty_level': 2,
        'target_muscles': ['大腿前側', '臀部', '核心肌群', '腿後肌'],
        'instructions': [
            '雙腳與肩同寬站立',
            '手臂向前伸直或抱胸',
            '臀部向後坐下',
            '膝蓋彎曲至90度',
            '膝蓋保持與腳尖同方向',
            '站起時用腳跟發力'
        ]
    },
    {
        'name': '伏地挺身',
        'description': '伏地挺身是鍛鍊胸部、三頭肌和核心肌群的基本動作。',
        'difficulty_level': 2,
        'target_muscles': ['胸部', '手臂', '肩膀', '核心肌群'],
        'instructions': [
            '雙手撐地，與肩同寬',
            '身體保持一直線',
            '下放胸部接近地面',
            '手肘保持45度角',
            '用手掌推回起始位置',
            '避免腰部下垂'
        ]
    },
    {
        'name': '平板支撐',
        'description': '平板支撐是鍛鍊核心肌群的靜態動作，主要訓練腹部、背部和肩膀穩定性。',
        'difficulty_level': 1,
        'target_muscles': ['腹部', '背部', '肩膀', '核心肌群'],
        'instructions': [
            '俯臥撐姿勢，但用前臂支撐',
            '保持身體成一直線',
            '核心收緊',
            '保持正常呼吸',
            '避免臀部過高或過低',
            '保持姿勢穩定'
        ]
    },
    {
        'name': '弓箭步',
        'description': '弓箭步是單側下肢訓練動作，主要鍛鍊大腿前側、後側和臀部肌群。',
        'difficulty_level': 2,
        'target_muscles': ['大腿前側', '大腿後側', '臀部', '核心肌群'],
        'instructions': [
            '雙腳與肩同寬站立',
            '向前跨一大步',
            '後腳保持穩定',
            '前腳膝蓋彎曲至90度',
            '後腳膝蓋接近地面',
            '用前腳發力回到起始位置'
        ]
    },
    {
        'name': '引體向上',
        'description': '引體向上是鍛鍊上半身拉力的動作，主要訓練背部、手臂和肩膀肌群。',
        'difficulty_level': 3,
        'target_muscles': ['背部', '手臂', '肩膀', '核心肌群'],
        'instructions': [
            '雙手正握單槓，與肩同寬',
            '身體懸垂',
            '肩胛骨收緊',
            '用背部肌群拉起身體',
            '下巴超過單槓',
            '控制速度下降'
        ]
    },
    {
        'name': '舉重',
        'description': '舉重是鍛鍊上半身肌群的動作，重點是保持手臂垂直角度，主要訓練肩膀、手臂和核心肌群。',
        'difficulty_level': 2,
        'target_muscles': ['肩膀', '手臂', '核心肌群', '背部'],
        'instructions': [
            '雙腳與肩同寬站立',
            '雙手握住槓鈴或啞鈴',
            '保持上半身手垂直角度（肩膀到手腕）',
            '手臂應該垂直於地面',
            '保持核心收緊',
            '避免手臂過度前傾或後傾'
        ]
    }
]


def ensure_default_exercise_types():
    """確保預設運動類型存在於資料庫中"""
    for exercise_data in DEFAULT_EXERCISE_TYPES:
        ExerciseType.objects.get_or_create(
            name=exercise_data['name'],
            defaults=exercise_data
        )


class ExerciseTypeListView(generics.ListCreateAPIView):
    """運動類型列表和創建"""
    serializer_class = ExerciseTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ensure_default_exercise_types()
        return ExerciseType.objects.all()


class ExerciseSessionViewSet(viewsets.ModelViewSet):
    """運動訓練記錄管理"""
    serializer_class = ExerciseSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return ExerciseSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_pose(request):
    """
    分析姿勢 - 支援實時攝影鏡頭輸入
    """
    try:
        # 獲取輸入資料
        image_data = request.data.get('image')
        exercise_type = request.data.get('exercise_type', 'general')
        session_id = request.data.get('session_id')
        frame_number = request.data.get('frame_number', 0)
        
        if not image_data:
            return Response(
                {'error': 'No image data provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 處理影像資料
        if isinstance(image_data, str):
            # Base64 編碼的影像
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
        else:
            # 檔案上傳
            image = Image.open(image_data)
        
        # 轉換為 OpenCV 格式
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 執行姿勢檢測（傳入運動類型以計算動作接近程度的分數）
        pose_detector = get_pose_detector()
        pose_result = pose_detector.detect_pose(frame, exercise_type=exercise_type)
        
        # 生成回饋建議
        feedback = pose_detector.get_pose_feedback(
            pose_result['keypoints'], 
            exercise_type
        )
        
        # 如果有訓練記錄，儲存分析結果
        pose_analysis = None
        if session_id:
            try:
                session = ExerciseSession.objects.get(
                    id=session_id, 
                    user=request.user
                )
                
                pose_analysis = PoseAnalysis.objects.create(
                    session=session,
                    frame_number=frame_number,
                    keypoints=pose_result['keypoints'],
                    pose_score=pose_result['pose_score'],
                    confidence_score=pose_result['confidence'],
                    detected_errors=pose_result['detected_errors'],
                    ai_feedback=feedback
                )
                
                # 更新訓練記錄
                session.total_reps += 1
                if session.average_score is None:
                    session.average_score = pose_result['pose_score']
                else:
                    # 計算移動平均
                    session.average_score = (
                        session.average_score * (session.total_reps - 1) + 
                        pose_result['pose_score']
                    ) / session.total_reps
                session.save()
                
            except ExerciseSession.DoesNotExist:
                pass
        
        # 準備回應資料（只返回關鍵點，不返回圖片）
        response_data = {
            'pose_analysis_id': pose_analysis.id if pose_analysis else None,
            'keypoints': pose_result['keypoints'],
            'pose_score': pose_result['pose_score'],
            'confidence': pose_result['confidence'],
            'detected_errors': pose_result['detected_errors'],
            'ai_feedback': feedback,
            'timestamp': pose_result['timestamp'],
            'frame_number': frame_number
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Pose analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_exercise_session(request):
    """開始新的運動訓練"""
    try:
        exercise_type_id = request.data.get('exercise_type_id')
        session_name = request.data.get('session_name', '')
        
        if not exercise_type_id:
            return Response(
                {'error': 'Exercise type ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            exercise_type = ExerciseType.objects.get(id=exercise_type_id)
        except ExerciseType.DoesNotExist:
            return Response(
                {'error': 'Exercise type not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 創建新的訓練記錄
        session = ExerciseSession.objects.create(
            user=request.user,
            exercise_type=exercise_type,
            session_name=session_name or f"{exercise_type.name} 訓練"
        )
        
        serializer = ExerciseSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to start session: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def end_exercise_session(request, session_id):
    """結束運動訓練"""
    try:
        session = ExerciseSession.objects.get(
            id=session_id, 
            user=request.user
        )
        
        session.end_time = timezone.now()
        if session.start_time:
            session.total_duration = session.end_time - session.start_time
        session.save()
        
        serializer = ExerciseSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except ExerciseSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to end session: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_exercise_history(request):
    """獲取運動歷史記錄"""
    try:
        sessions = ExerciseSession.objects.filter(
            user=request.user
        ).order_by('-start_time')
        
        serializer = ExerciseSessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get history: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_session_analyses(request, session_id):
    """獲取特定訓練的姿勢分析記錄"""
    try:
        session = ExerciseSession.objects.get(
            id=session_id, 
            user=request.user
        )
        
        analyses = PoseAnalysis.objects.filter(
            session=session
        ).order_by('frame_number')
        
        serializer = PoseAnalysisSerializer(analyses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except ExerciseSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to get analyses: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def get_pose_feedback(request):
    """獲取姿勢回饋建議"""
    try:
        keypoints = request.data.get('keypoints', [])
        exercise_type = request.data.get('exercise_type', 'general')
        
        pose_detector = get_pose_detector()
        feedback = pose_detector.get_pose_feedback(keypoints, exercise_type)
        
        return Response({
            'feedback': feedback,
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get feedback: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_exercise_statistics(request):
    """獲取運動統計資料"""
    try:
        user_sessions = ExerciseSession.objects.filter(user=request.user)
        
        # 計算統計資料
        total_sessions = user_sessions.count()
        total_duration = sum(
            (s.total_duration.total_seconds() if s.total_duration else 0) 
            for s in user_sessions
        )
        total_reps = sum(s.total_reps for s in user_sessions)
        average_score = sum(
            s.average_score for s in user_sessions if s.average_score
        ) / max(1, len([s for s in user_sessions if s.average_score]))
        
        # 按運動類型分組
        exercise_stats = {}
        for session in user_sessions:
            exercise_name = session.exercise_type.name
            if exercise_name not in exercise_stats:
                exercise_stats[exercise_name] = {
                    'sessions': 0,
                    'total_reps': 0,
                    'average_score': 0
                }
            exercise_stats[exercise_name]['sessions'] += 1
            exercise_stats[exercise_name]['total_reps'] += session.total_reps
            if session.average_score:
                exercise_stats[exercise_name]['average_score'] += session.average_score
        
        # 計算平均值
        for exercise_name in exercise_stats:
            stats = exercise_stats[exercise_name]
            if stats['sessions'] > 0:
                stats['average_score'] /= stats['sessions']
        
        return Response({
            'total_sessions': total_sessions,
            'total_duration_seconds': total_duration,
            'total_reps': total_reps,
            'overall_average_score': average_score,
            'exercise_breakdown': exercise_stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get statistics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
