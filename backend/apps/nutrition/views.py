from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import UserProfile, WeightRecord, GoalProgress
from apps.history.models import FoodEntry
from .serializers import (
    UserProfileSerializer, WeightRecordSerializer, GoalProgressSerializer,
    BMRTDEECalculationSerializer, WeightProgressSerializer
)


def get_current_date_in_timezone():
    """Get current date in the configured timezone"""
    from django.conf import settings
    import pytz
    
    # Get the configured timezone
    tz = pytz.timezone(settings.TIME_ZONE)
    # Get current time in that timezone
    now_in_tz = timezone.now().astimezone(tz)
    return now_in_tz.date()


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(
                {'error': 'Profile not found. Please create your profile first.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            # Create new profile if it doesn't exist
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Update existing profile
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class WeightRecordListCreateView(generics.ListCreateAPIView):
    """List weight records or create new one"""
    serializer_class = WeightRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WeightRecord.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Check if a record already exists for this date
        existing_record = WeightRecord.objects.filter(
            user=request.user,
            date=request.data.get('date')
        ).first()

        if existing_record:
            # Update the existing record
            serializer = self.get_serializer(existing_record, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new record if no existing record found
        return super().create(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


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
    end_date = get_current_date_in_timezone()
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def calorie_progress_analytics(request):
    """Get calorie intake progress compared to BMR/TDEE"""
    date_range = request.GET.get('range', '7d')
    comparison_type = request.GET.get('type', 'tdee')  # 'bmr' or 'tdee'
    if comparison_type not in {'bmr', 'tdee'}:
        comparison_type = 'tdee'
    
    # Calculate date filtering
    end_date = get_current_date_in_timezone()
    if date_range == '1d':
        start_date = end_date
    elif date_range == '7d':
        start_date = end_date - timedelta(days=6)  # Include today
    elif date_range == '30d':
        start_date = end_date - timedelta(days=29)  # Include today
    elif date_range == '90d':
        start_date = end_date - timedelta(days=89)  # Include today
    else:  # default to 7d
        start_date = end_date - timedelta(days=6)
    
    # Get user's latest weight record for BMR/TDEE calculation
    latest_weight_record = WeightRecord.objects.filter(user=request.user).first()
    if not latest_weight_record:
        return Response(
            {'error': 'No weight records found. Please add a weight record first.'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get user profile for fallback calculations
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None

    # Get target calorie value (BMR or TDEE) with fallback if missing on record
    if comparison_type == 'tdee':
        target_calories = latest_weight_record.tdee
        if (target_calories is None or target_calories <= 0) and profile:
            target_calories = profile.calculate_tdee(latest_weight_record.weight)
    else:  # 'bmr'
        target_calories = latest_weight_record.bmr
        if (target_calories is None or target_calories <= 0) and profile:
            target_calories = profile.calculate_bmr(latest_weight_record.weight)

    # If still no valid target, return a helpful error
    if target_calories is None or target_calories <= 0:
        return Response(
            {
                'error': 'Unable to determine target calories. Please complete your profile (age, gender, height, activity level) and add a weight record.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get daily calorie intake data
    daily_data = []
    total_intake = 0
    total_target = 0
    
    current_date = start_date
    while current_date <= end_date:
        # Get food entries for this date - using date range instead of exact date
        start_datetime = timezone.datetime.combine(current_date, timezone.datetime.min.time())
        end_datetime = timezone.datetime.combine(current_date, timezone.datetime.max.time())
        
        # Make them timezone aware
        if timezone.is_naive(start_datetime):
            start_datetime = timezone.make_aware(start_datetime)
        if timezone.is_naive(end_datetime):
            end_datetime = timezone.make_aware(end_datetime)
        
        daily_entries = FoodEntry.objects.filter(
            user=request.user,
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        )
        
        daily_intake = daily_entries.aggregate(total=Sum('total_calories'))['total'] or 0
        total_intake += daily_intake
        total_target += target_calories
        
        # Calculate progress percentage for this day
        progress_percentage = (daily_intake / target_calories * 100) if target_calories > 0 else 0
        
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'intake': daily_intake,
            'target': target_calories,
            'progress_percentage': round(progress_percentage, 1),
            'status': 'over' if daily_intake > target_calories else 'under' if daily_intake < target_calories else 'on_target'
        })
        
        current_date += timedelta(days=1)
    
    # Calculate overall statistics
    avg_daily_intake = total_intake / len(daily_data) if daily_data else 0
    avg_daily_target = total_target / len(daily_data) if daily_data else 0
    overall_progress = (avg_daily_intake / avg_daily_target * 100) if avg_daily_target > 0 else 0
    
    # Calculate streak data
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    
    for day in reversed(daily_data):  # Start from most recent
        if abs(day['progress_percentage'] - 100) <= 10:  # Within 10% of target
            temp_streak += 1
            if current_streak == 0:  # First day of current streak
                current_streak = temp_streak
        else:
            if temp_streak > best_streak:
                best_streak = temp_streak
            temp_streak = 0
            if current_streak > 0:  # End of current streak
                current_streak = temp_streak
    
    # Final check for best streak
    if temp_streak > best_streak:
        best_streak = temp_streak
    
    response_data = {
        'analytics': {
            'comparison_type': comparison_type,
            'target_calories': target_calories,
            'avg_daily_intake': round(avg_daily_intake, 1),
            'avg_daily_target': round(avg_daily_target, 1),
            'overall_progress_percentage': round(overall_progress, 1),
            'total_days': len(daily_data),
            'days_on_target': len([d for d in daily_data if abs(d['progress_percentage'] - 100) <= 10]),
            'days_over_target': len([d for d in daily_data if d['progress_percentage'] > 110]),
            'days_under_target': len([d for d in daily_data if d['progress_percentage'] < 90]),
            'current_streak': current_streak,
            'best_streak': best_streak,
        },
        'daily_data': daily_data,
        'date_range': date_range
    }
    
    return Response(response_data, status=status.HTTP_200_OK) 