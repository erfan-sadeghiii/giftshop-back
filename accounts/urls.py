from django.urls import path
from .views import register_view, login_view, refresh_view, logout_view,me_view, UserListView,UserDetailView










urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('refresh/', refresh_view, name='refresh'),
    path('logout/', logout_view, name='logout'),
    path('me/', me_view, name='me'),
]
