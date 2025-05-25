"""
URL configuration for posefit_project project.

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
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path,re_path
from app.history.views import HistoryPageView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,         # optional: verify a token
    TokenBlacklistView,      # optional: blacklist a refresh token
)
from django.http import FileResponse
import os
from django.views.generic import View
from django_rest_passwordreset.views import (
    ResetPasswordRequestToken,
    ResetPasswordConfirm,
    ResetPasswordValidateToken
)
from django.views.decorators.csrf import csrf_exempt

class FrontendAppView(View):
    def get(self, request):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
        return FileResponse(open(file_path, 'rb'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.classify.urls')),
    path('accounts/', include('app.accounts.urls')),
    path("history/", HistoryPageView.as_view(), name="history_page"),
    path("api/history/", include("app.history.urls")),
    path('api/token/',              TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('api/token/refresh/',      TokenRefreshView.as_view(),     name='token_refresh'),
    # optional extra endpoints
    path('api/token/verify/',       TokenVerifyView.as_view(),      name='token_verify'),
    path('api/token/blacklist/',    TokenBlacklistView.as_view(),   name='token_blacklist'),
    path('api/password_reset',csrf_exempt(ResetPasswordRequestToken.as_view()),name='password_reset'),
    path('api/password_reset/validate_token',csrf_exempt(ResetPasswordValidateToken.as_view()),name='password_reset_validate_token'),
    path('api/password_reset/confirm',csrf_exempt(ResetPasswordConfirm.as_view()),name='password_reset_confirm'),
]

if settings.DEBUG:
    # 1) Serve /media/ from disk
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#    This must come *after* static(). Otherwise it intercepts /media/ too.
urlpatterns += [
    re_path(r'^.*$', FrontendAppView.as_view()),
]

