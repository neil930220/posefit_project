# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import SignUpForm
import json
from django_ratelimit.decorators import ratelimit
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
import os

class RegisterView(generics.CreateAPIView):
    authentication_classes = []      # ← disable all authentication
    permission_classes     = [AllowAny]
    serializer_class       = RegisterSerializer

@ratelimit(key='ip', rate='5/m', block=True)
def signup(request):
    if request.method == 'POST':
        # try to parse JSON, fallback to form-encoded
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST

        form = SignUpForm(data)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('login')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(form.errors, status=400)

    else:
        form = SignUpForm()

    # Serve the frontend index.html for non-AJAX requests
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'frontend', 'index.html')
    return FileResponse(open(file_path, 'rb'))


# views.py
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from django.views import View

class LoginView(View):
    @ratelimit(key='ip', rate='10/m', block=True)
    def post(self, request, *args, **kwargs):
        from django.contrib.auth.forms import AuthenticationForm
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if is_ajax:
            # Handle AJAX login requests
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                data = request.POST
            
            form = AuthenticationForm(request, data=data)
            if form.is_valid():
                user = form.get_user()
                auth_login(request, user)
                return JsonResponse({'success': True})
            else:
                errors = form.errors.get_json_data()
                clean = {f: [d['message'] for d in v] for f, v in errors.items()}
                return JsonResponse(clean, status=400)
        else:
            # For non-AJAX requests, serve the frontend app
            return self.get(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # Serve the frontend index.html for GET requests
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'frontend', 'index.html')
        return FileResponse(open(file_path, 'rb'))

class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('login')

from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)    

from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

@require_GET
@login_required
def fetch_messages(request):
    # Just return an empty list for now
    return JsonResponse([], safe=False)
