from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from authentication.models import CustomUser
from notifications.models import Notification
from resources.models import Resource, ResourceCategory, ResourceItem
from tools.models import Tool

from django.db.models.functions import TruncDate
from .ai_registry import list_agents


def _dashboard_metrics():
    return {
        "total_users": CustomUser.objects.count(),
        "verified_users": CustomUser.objects.filter(is_email_verified=True).count(),
        "total_tools": Tool.objects.count(),
        "approved_tools": Tool.objects.filter(approval_status="approved").count(),
        "pending_tool_reviews": Tool.objects.filter(approval_status="pending").count(),
        "total_resources": Resource.objects.count(),
        "resource_items": ResourceItem.objects.count(),
        "resource_categories": ResourceCategory.objects.count(),
        "unread_notifications": Notification.objects.filter(is_read=False).count(),
        "recent_notifications": Notification.objects.order_by("-created_at")[:8],
        "ai_jobs_running": 0,
        "ai_jobs_completed": 0,
        "ai_jobs_failed": 0,
    }


def _chart_series(model, date_field, days=14):
    end = timezone.now().date()
    start = end - timedelta(days=days - 1)
    labels = []
    values = []

    for offset in range(days):
        day = start + timedelta(days=offset)
        labels.append(day.strftime("%b %d"))
        values.append(
            model.objects.filter(**{
                f"{date_field}__date": day,
            }).count()
        )

    return labels, values


@staff_member_required
def dashboard(request):
    metrics = _dashboard_metrics()

    user_labels, user_values = _chart_series(CustomUser, "date_joined")
    tool_labels, tool_values = _chart_series(Tool, "created_at")
    resource_labels = user_labels
    resource_values = [0] * len(user_labels)

    context = {
        "active_page": "dashboard",
        **metrics,
        "chart_labels": user_labels,
        "user_series": user_values,
        "tool_series": tool_values,
        "resource_series": resource_values,
    }
    return render(request, "admin_portal/dashboard.html", context)


@staff_member_required
def dashboard_data(request):
    user_labels, user_values = _chart_series(CustomUser, "date_joined")
    tool_labels, tool_values = _chart_series(Tool, "created_at")
    resource_labels = user_labels
    resource_values = [0] * len(user_labels)
    payload = {
        "metrics": _dashboard_metrics(),
        "charts": {
            "labels": user_labels,
            "users": user_values,
            "tools": tool_values,
            "resources": resource_values,
        },
    }
    return JsonResponse(payload)

def _daily_series(model, date_field, days=14):
    end = timezone.now().date()
    start = end - timedelta(days=days - 1)

    rows = (
        model.objects
        .filter(**{f"{date_field}__date__gte": start, f"{date_field}__date__lte": end})
        .annotate(day=TruncDate(date_field))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    series_map = {row["day"]: row["total"] for row in rows}
    labels = []
    values = []

    for offset in range(days):
        day = start + timedelta(days=offset)
        labels.append(day.strftime("%b %d"))
        values.append(series_map.get(day, 0))

    return labels, values

@staff_member_required
def users_view(request):
    users = (
        CustomUser.objects
        .annotate(
            notification_count=Count("notifications", distinct=True),
        )
        .order_by("-date_joined")
    )
    return render(request, "admin_portal/users.html", {
        "active_page": "users",
        "users": users,
        "total_users": CustomUser.objects.count(),
        "verified_users": CustomUser.objects.filter(is_email_verified=True).count(),
    })


@staff_member_required
def tools_view(request):
    tools = Tool.objects.select_related("category", "added_by", "approved_by").order_by("-created_at")
    return render(request, "admin_portal/tools.html", {
        "active_page": "tools",
        "tools": tools,
        "pending_tool_reviews": Tool.objects.filter(approval_status="pending").count(),
        "approved_tools": Tool.objects.filter(approval_status="approved").count(),
    })


@staff_member_required
def ai_workspace_view(request):
    agents = list_agents()
    agents = [
        {"key": "pipeline", "label": "Pipeline Overview", "status": "active"},
        {"key": "research", "label": "Research Agent", "status": "active"},
        {"key": "classification", "label": "Classification Agent", "status": "active"},
        {"key": "metadata", "label": "Metadata Agent", "status": "active"},
        {"key": "quality", "label": "Quality Agent", "status": "active"},
        {"key": "prompts", "label": "Prompt Library", "status": "active"},
        {"key": "logs", "label": "AI Logs", "status": "active"},
        {"key": "queue", "label": "Job Queue", "status": "active"},
        {"key": "settings", "label": "AI Settings", "status": "active"},
    ]
    return render(request, "admin_portal/ai_workspace.html", {
        "active_page": "ai_workspace",
        "agents": agents,
    })
    
