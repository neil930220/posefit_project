from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import UserProfile, WeightRecord, GoalProgress
from .serializers import (
    UserProfileSerializer, WeightRecordSerializer, GoalProgressSerializer,
    BMRTDEECalculationSerializer, WeightProgressSerializer
)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class WeightRecordListCreateView(generics.ListCreateAPIView):
    """List weight records or create new one"""
    serializer_class = WeightRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WeightRecord.objects.filter(user=self.request.user)


class WeightRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete specific weight record"""
    serializer_class = WeightRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WeightRecord.objects.filter(user=self.request.user)


class GoalProgressListCreateView(generics.ListCreateAPIView):
    """List goal progress or create new goal"""
    serializer_class = GoalProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalProgress.objects.filter(user=self.request.user)


class GoalProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete specific goal"""
    serializer_class = GoalProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalProgress.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def calculate_bmr_tdee(request):
    """Calculate BMR and TDEE without saving to database"""
    serializer = BMRTDEECalculationSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.calculate()
        return Response(result, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def weight_progress_analytics(request):
    """Get weight progress analytics and charts data"""
    date_range = request.GET.get('range', '30d')
    
    # Calculate date filtering
    end_date = timezone.now().date()
    if date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    elif date_range == '90d':
        start_date = end_date - timedelta(days=90)
    elif date_range == '6m':
        start_date = end_date - timedelta(days=180)
    elif date_range == '1y':
        start_date = end_date - timedelta(days=365)
    else:  # 'all'
        start_date = None
    
    # Get weight records
    queryset = WeightRecord.objects.filter(user=request.user)
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    
    records = queryset.order_by('date')
    
    # Prepare chart data
    weight_data = []
    bmr_data = []
    tdee_data = []
    dates = []
    
    for record in records:
        weight_data.append(record.weight)
        bmr_data.append(record.bmr)
        tdee_data.append(record.tdee)
        dates.append(record.date.strftime('%Y-%m-%d'))
    
    # Calculate statistics
    current_weight = records.last().weight if records else None
    starting_weight = records.first().weight if records else None
    weight_change = (current_weight - starting_weight) if (current_weight and starting_weight) else 0
    
    # Get goal progress
    goal_progress = None
    current_goal = GoalProgress.objects.filter(user=request.user).last()
    if current_goal:
        current_goal.current_weight = current_weight or current_goal.current_weight
        current_goal.save()
        goal_progress = GoalProgressSerializer(current_goal).data
    
    return Response({
        'analytics': {
            'current_weight': current_weight,
            'starting_weight': starting_weight,
            'weight_change': round(weight_change, 2) if weight_change else 0,
            'total_records': records.count(),
        },
        'chart_data': {
            'dates': dates,
            'weight': weight_data,
            'bmr': bmr_data,
            'tdee': tdee_data,
        },
        'goal_progress': goal_progress,
        'date_range': date_range
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_summary(request):
    """Get dashboard summary data"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        latest_record = WeightRecord.objects.filter(user=request.user).first()
        current_goal = GoalProgress.objects.filter(user=request.user).last()
        
        summary = {
            'profile': UserProfileSerializer(profile).data,
            'latest_weight': WeightRecordSerializer(latest_record).data if latest_record else None,
            'current_goal': GoalProgressSerializer(current_goal).data if current_goal else None,
            'total_records': WeightRecord.objects.filter(user=request.user).count(),
        }
        
        return Response(summary, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found. Please complete your profile first.'}, 
            status=status.HTTP_404_NOT_FOUND
        ) 