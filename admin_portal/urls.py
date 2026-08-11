from django.urls import path
from . import views

app_name = "admin_portal"

from . import api

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("users/", views.UsersListView.as_view(), name="users"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("tools/", views.tools_view, name="tools"),
    path("tools/htmx/approve/<int:pk>/", __import__('admin_portal.htmx_views', fromlist=['']).approve_tool, name='htmx_tool_approve'),
    path("tools/htmx/reject/<int:pk>/", __import__('admin_portal.htmx_views', fromlist=['']).reject_tool, name='htmx_tool_reject'),
    path("ai/", views.ai_workspace_view, name="ai_workspace"),
    path("ai/<str:key>/", views.ai_agent_view, name="ai_agent"),
    path("ai/htmx/start/<str:key>/", __import__('admin_portal.htmx_views', fromlist=['']).start_agent_job, name='htmx_ai_start'),
    path("ai/htmx/cancel/<int:job_id>/", __import__('admin_portal.htmx_views', fromlist=['']).cancel_agent_job, name='htmx_ai_cancel'),
    path("api/dashboard-data/", views.dashboard_data, name="dashboard_data"),
    path("api/metrics/", api.metrics_view, name="metrics"),
    path("ai/htmx/start-pipeline/", __import__('admin_portal.htmx_views', fromlist=['']).start_pipeline, name='htmx_pipeline_start'),
]