from django.urls import path
from . import views

app_name = "admin_portal"

from . import api

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("users/", views.UsersListView.as_view(), name="users"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("tools/", views.tools_view, name="tools"),
    path("ai/", views.ai_workspace_view, name="ai_workspace"),
    path("api/dashboard-data/", views.dashboard_data, name="dashboard_data"),
    path("api/metrics/", api.metrics_view, name="metrics"),
]