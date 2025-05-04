from django.urls import path
from .views import signup, LoginView, LogoutView, current_user
from .views import fetch_messages

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', current_user, name='current_user'),
    path('messages/', fetch_messages, name='fetch_messages'),
]
