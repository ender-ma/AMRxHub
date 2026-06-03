from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import ToolCategory, Tool, ToolClick
from django.urls import reverse
from rapidfuzz import process
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from history.models import History
from history.signals import object_viewed_signal
from history.mixins import ObjectViewMixin
from django.views.generic.detail import DetailView
from .models import Tool
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from history.signals import object_viewed_signal
from authentication.utils import email_verified_required

def my_view(request, pk):
    obj = get_object_or_404(Tool, pk=pk)
    if request.user.is_authenticated:
        object_viewed_signal.send(obj.__class__, instance=obj, request=request)
    ...

@csrf_exempt  # Or use @csrf_protect and pass the token in JS
def history_delete(request, pk):
    if request.method == 'POST' and request.user.is_authenticated:
        History.objects.filter(pk=pk, user=request.user).delete()
        return HttpResponse(status=204)
    return HttpResponse(status=403)

class ToolDetailView(ObjectViewMixin, DetailView):
    model = Tool
    template_name = 'tools/tool_detail.html'
    context_object_name = 'tool'
    
@login_required
def tool_access(request, tool_id):
    tool = get_object_or_404(Tool, pk=tool_id)
    ct = ContentType.objects.get_for_model(tool)
    History.objects.create(user=request.user, content_type=ct, object_id=tool.pk)
    return redirect(tool.url)

@login_required
def use_tool(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id, is_active=True, approval_status='approved')
    if request.method == 'POST':
        description = request.POST.get('description', '')
        uploaded_file = request.FILES.get('uploaded_file')
        # Record generic history entry
        ct = ContentType.objects.get_for_model(tool)
        History.objects.create(user=request.user, content_type=ct, object_id=tool.pk)
        messages.success(request, f"Usage of {tool.name} recorded.")
        return redirect('tools:history')
    return render(request, 'tools/tool_use.html', {'tool': tool})

@login_required
@email_verified_required
def history(request):
    ct = ContentType.objects.get_for_model(Tool)
    history_items = History.objects.filter(user=request.user, content_type=ct).order_by('-viewed_on')
    return render(request, 'history/history.html', {'history_items': history_items})

def tool_redirect(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id, is_active=True, approval_status='approved')
    ToolClick.objects.create(
        tool=tool,
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR', '')
    )
    tool.click_count = (tool.click_count or 0) + 1
    tool.save(update_fields=['click_count'])
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(tool)
        History.objects.create(user=request.user, content_type=ct, object_id=tool.pk)
    return redirect(tool.url)

def tools_home(request):
    organism_categories = ToolCategory.objects.filter(category_type='organism', is_active=True).order_by('order', 'name')
    general_categories = ToolCategory.objects.filter(category_type='general', is_active=True).order_by('order', 'name')
    featured_tools = Tool.objects.filter(is_featured=True, is_active=True, approval_status='approved')[:6]
    return render(request, 'tools/tools.html', {
        'featured_tools': featured_tools,
        'organism_categories': organism_categories,
        'general_categories': general_categories
    })

def tools(request):
    return redirect('tools:tools_home')

def category_tools(request, category_id):
    category = get_object_or_404(ToolCategory, id=category_id, is_active=True)
    tools_qs = Tool.objects.filter(category=category, is_active=True, approval_status='approved').order_by('-is_featured', 'name')
    return render(request, 'tools/category_tools.html', {'category': category, 'tools': tools_qs})

def tool_detail(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id, is_active=True, approval_status='approved')
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(tool)
        History.objects.create(user=request.user, content_type=ct, object_id=tool.pk)
    return render(request, 'tools/tool_detail.html', {'tool': tool})

def search_tools(request):
    query = request.GET.get('q', '').strip()
    results = Tool.objects.none()
    if query:
        all_tools = Tool.objects.filter(is_active=True, approval_status='approved')
        tool_strings = [f"{tool.name} {tool.short_description}" for tool in all_tools]
        matches = process.extract(query, tool_strings, limit=10, score_cutoff=40)
        matched_names = [m[0].split(' ', 1)[0] for m in matches]
        results = all_tools.filter(name__in=matched_names)
    return render(request, 'tools/search_results.html', {'query': query, 'results': results})

def ajax_search_tools(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        tools_qs = Tool.objects.filter(is_active=True, approval_status='approved').filter(
            Q(name__icontains=query) | Q(short_description__icontains=query)
        )[:10]
        for tool in tools_qs:
            results.append({
                'name': tool.name,
                'short_description': tool.short_description,
                'category': tool.category.name if tool.category else '',
                'logo': tool.logo.url if tool.logo else '',
                'url': tool.get_absolute_url()
            })
    return JsonResponse({'results': results})

@login_required
def workflow(request):
    return render(request, 'tools/workflow.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('tools:tools_home')
    context = {
        'total_categories': ToolCategory.objects.count(),
        'active_categories': ToolCategory.objects.filter(is_active=True).count(),
        'total_tools': Tool.objects.count(),
        'approved_tools': Tool.objects.filter(approval_status='approved').count(),
        'pending_tools': Tool.objects.filter(approval_status='pending').count()
    }
    return render(request, 'tools/admin_dashboard.html', context)