from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from tools.models import Tool


@staff_member_required
def approve_tool(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    tool = get_object_or_404(Tool, pk=pk)
    tool.approval_status = 'approved'
    tool.approved_by = request.user
    tool.approved_at = timezone.now()
    tool.rejection_reason = ''
    tool.save(update_fields=['approval_status', 'approved_by', 'approved_at', 'rejection_reason'])
    # Return a small snippet to update the UI
    return render(request, 'admin_portal/partials/tool_status.html', {'tool': tool})


@staff_member_required
def reject_tool(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    tool = get_object_or_404(Tool, pk=pk)
    reason = request.POST.get('reason', '').strip()
    tool.approval_status = 'rejected'
    tool.rejection_reason = reason
    tool.approved_by = request.user
    tool.approved_at = timezone.now()
    tool.save(update_fields=['approval_status', 'rejection_reason', 'approved_by', 'approved_at'])
    return render(request, 'admin_portal/partials/tool_status.html', {'tool': tool})