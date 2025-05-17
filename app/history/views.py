from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions
from .models import FoodEntry
from .serializers import FoodEntrySerializer
from django.views.generic import TemplateView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication      import SessionAuthentication
from rest_framework.permissions import IsAuthenticated


class HistoryPageView(TemplateView):
    template_name = "index.html"

class FoodEntryViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]      # ← 只接受 JWT
    permission_classes     = [IsAuthenticated]       # ← 一定要登入（JWT）
    serializer_class       = FoodEntrySerializer

    def get_queryset(self):
        return FoodEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
