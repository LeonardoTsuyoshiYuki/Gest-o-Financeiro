from django.urls import path
from .views import UserDetailView, UserListCreateView, UserManageView

urlpatterns = [
    path('me/', UserDetailView.as_view(), name='user-me'),
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserManageView.as_view(), name='user-manage'),
]
