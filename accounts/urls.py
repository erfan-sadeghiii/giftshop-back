from django.urls import path
from .views import register_view, login_view, refresh_view, logout_view,me_view, UserListView,UserDetailView,verify_code,send_verification_code,send_verification_code_login,verify_code_login










urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('refresh/', refresh_view, name='refresh'),
    path('logout/', logout_view, name='logout'),
    path('verify-code/', verify_code, name='verify-code'),
    path('send-code/', send_verification_code, name='send-code'),
    path("send-login-code/", send_verification_code_login),
    path("login-phone/", verify_code_login),
    path('me/', me_view, name='me'),
]
