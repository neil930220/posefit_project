from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions
from .models import FoodEntry
from .serializers import FoodEntrySerializer
from django.views.generic import TemplateView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication      import SessionAuthentication

class HistoryPageView(TemplateView):
    template_name = "index.html"

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: only owners (or anonymous owners via session_key)
    can edit/view their entries.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Check read permissions
            if request.user.is_authenticated:
                return obj.user == request.user
            return obj.session_key == request.session.session_key
        # Write permissions: same check
        if request.user.is_authenticated:
            return obj.user == request.user
        return obj.session_key == request.session.session_key

class FoodEntryViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes     = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class       = FoodEntrySerializer

    def get_queryset(self):
        qs = FoodEntry.objects.all()
        if self.request.user.is_authenticated:
            return qs.filter(user=self.request.user)
        # ensure session exists
        session_key = self.request.session.session_key or self.request.session.create()
        return qs.filter(session_key=self.request.session.session_key)

    def perform_create(self, serializer):
        # Attach user or session_key automatically
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # ensure session exists
            session_key = self.request.session.session_key or self.request.session.create()
            serializer.save(session_key=session_key)
