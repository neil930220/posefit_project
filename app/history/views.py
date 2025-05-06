from django.views.generic import TemplateView
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import FoodEntry
from .serializers import FoodEntrySerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only the owner (or anonymous owner via session_key) may edit/view.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for owners or anonymous session
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated:
                return obj.user == request.user
            return obj.session_key == request.session.session_key

        # Write permissions: same check
        if request.user.is_authenticated:
            return obj.user == request.user
        return obj.session_key == request.session.session_key


class FoodEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing/creating/updating FoodEntry.
    - Authenticated users see only their entries.
    - Anonymous users see only entries tied to their session_key.
    - Authenticated create attaches user; anonymous create attaches session_key.
    """
    serializer_class = FoodEntrySerializer

    # ✨ JWT + default-session auth (if you still want browsable API)
    authentication_classes = [JWTAuthentication]  
    permission_classes     = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = FoodEntry.objects.all()
        if self.request.user.is_authenticated:
            return qs.filter(user=self.request.user)
        # ensure session exists
        session_key = self.request.session.session_key or self.request.session.create()
        return qs.filter(session_key=session_key)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            session_key = self.request.session.session_key or self.request.session.create()
            serializer.save(session_key=session_key)


class HistoryPageView(TemplateView):
    template_name = "index.html"
