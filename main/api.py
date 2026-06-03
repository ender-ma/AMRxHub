from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from resources.models import ResourceItem
from tools.models import Tool


def serialize_tool(tool):
    return {
        "id": tool.id,
        "type": "tool",
        "name": tool.name,
        "description": tool.short_description,
        "category": tool.category.name if tool.category else "",
        "subcategory": "Organism Specific" if tool.category and tool.category.category_type == "organism" else "General Use",
        "organism": tool.category.name if tool.category and tool.category.category_type == "organism" else None,
        "url": reverse("tools:tool_detail", args=[tool.id]),
    }


def serialize_resource(resource):
    return {
        "id": resource.id,
        "type": "resource",
        "name": resource.title,
        "description": resource.description,
        "category": resource.category.name if resource.category else "",
        "subcategory": resource.category.name if resource.category else "",
        "organism": None,
        "url": reverse("resources:resource_detail", args=[resource.id]),
    }


@cache_page(60 * 60 * 24)
@require_GET
def search_catalog(request):
    catalog = []

    tools = (
        Tool.objects.select_related("category")
        .filter(is_active=True, approval_status="approved")
        .only("id", "name", "short_description", "category__name", "category__category_type")
    )
    for tool in tools:
        catalog.append(serialize_tool(tool))

    resources = (
        ResourceItem.objects.select_related("category")
        .only("id", "title", "description", "category__name")
    )
    for resource in resources:
        catalog.append(serialize_resource(resource))

    return JsonResponse(catalog, safe=False)