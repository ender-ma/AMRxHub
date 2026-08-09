from django.urls import path
from . import views

app_name = "admin_portal"

from . import api

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("users/", views.users_view, name="users"),
    path("tools/", views.tools_view, name="tools"),
    path("ai/", views.ai_workspace_view, name="ai_workspace"),
    path("api/dashboard-data/", views.dashboard_data, name="dashboard_data"),
    path("api/metrics/", api.metrics_view, name="metrics"),
]