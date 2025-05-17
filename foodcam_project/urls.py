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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.classify.urls')),
    path('classify/', include('app.classify.urls')),
    path('accounts/', include('app.accounts.urls')),
    path("history/", HistoryPageView.as_view(), name="history_page"),
    path("api/history/", include("app.history.urls")),
    path('api/token/',              TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('api/token/refresh/',      TokenRefreshView.as_view(),     name='token_refresh'),
    # optional extra endpoints
    path('api/token/verify/',       TokenVerifyView.as_view(),      name='token_verify'),
    path('api/token/blacklist/',    TokenBlacklistView.as_view(),   name='token_blacklist'),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]

if settings.DEBUG:
    # 1) Serve /media/ from disk
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 2) Finally, your SPA entrypoint (catch-all)
#    This must come *after* static(). Otherwise it intercepts /media/ too.
urlpatterns += [
    # re_path catches everything else and sends index.html
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]

