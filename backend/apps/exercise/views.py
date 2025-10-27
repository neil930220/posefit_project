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


class ExerciseTypeListView(generics.ListCreateAPIView):
    """運動類型列表和創建"""
    queryset = ExerciseType.objects.all()
    serializer_class = ExerciseTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


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
        
        # 執行姿勢檢測
        pose_detector = get_pose_detector()
        pose_result = pose_detector.detect_pose(frame)
        
        # 在影像上繪製姿勢骨架
        frame_with_pose = pose_detector.draw_pose(frame.copy(), pose_result['keypoints'])
        
        # 將影像轉換為 base64
        _, buffer = cv2.imencode('.jpg', frame_with_pose)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
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
        
        # 準備回應資料
        response_data = {
            'pose_analysis_id': pose_analysis.id if pose_analysis else None,
            'keypoints': pose_result['keypoints'],
            'pose_score': pose_result['pose_score'],
            'confidence': pose_result['confidence'],
            'detected_errors': pose_result['detected_errors'],
            'ai_feedback': feedback,
            'timestamp': pose_result['timestamp'],
            'frame_number': frame_number,
            'annotated_image': f'data:image/jpeg;base64,{frame_base64}'  # 帶有姿勢繪製的影像
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
