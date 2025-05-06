"""
URL configuration for foodcam_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path
from app.history.views import HistoryPageView
from app.classify.views import upload_image, analyzing_page
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,         # optional: verify a token
    TokenBlacklistView,      # optional: blacklist a refresh token
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.index.urls')),
    path('analyzing/', analyzing_page, name='analyzing_page'),
    path('upload/',upload_image, name="upload_image"),
    path('classify/', include('app.classify.urls')),
    path('accounts/', include('app.accounts.urls')),
    path("history/", HistoryPageView.as_view(), name="history_page"),
    path("api/history/", include("app.history.urls")),
    path('api/token/',              TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('api/token/refresh/',      TokenRefreshView.as_view(),     name='token_refresh'),
    # optional extra endpoints
    path('api/token/verify/',       TokenVerifyView.as_view(),      name='token_verify'),
    path('api/token/blacklist/',    TokenBlacklistView.as_view(),   name='token_blacklist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


