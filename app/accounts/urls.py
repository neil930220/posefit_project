from django.urls import path
from .views import signup, LoginView, LogoutView, current_user
from .views import fetch_messages
from .views import RegisterView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/user/', current_user, name='current_user'),
    path('messages/', fetch_messages, name='fetch_messages'),
]
