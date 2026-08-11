from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from tools.models import Tool

from admin_portal.models import AIJob, PipelineRun
from admin_portal.tasks import process_ai_job, process_pipeline_run
from admin_portal.ai_registry import get_agent

from admin_portal.models import AIJob, PipelineRun
from admin_portal.tasks import process_ai_job, process_pipeline_run

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
    return render(request, 'admin_portal/tool_status.html', {'tool': tool})


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
    return render(request, 'admin_portal/tool_status.html', {'tool': tool})


@staff_member_required
def start_agent_job(request, key):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    agent = get_agent(key)
    if not agent:
        return HttpResponseBadRequest('Unknown agent')
    url = request.POST.get('url') or request.POST.get('input')
    created_by = request.user
    # preferred: agents expose submit_job
    try:
        mod = agent.get('callable')
        # if callable is function (module-level) try calling submit_job on that module
        if hasattr(mod, 'submit_job'):
            job = mod.submit_job(url, created_by=created_by)
        else:
            # try module import
            import importlib
            amod = importlib.import_module(mod.__module__)
            if hasattr(amod, 'submit_job'):
                job = getattr(amod, 'submit_job')(url, created_by=created_by)
            else:
                # fallback: create AIJob record directly
                job = AIJob.objects.create(agent_key=key, url=url, created_by=created_by, status='pending')
    except Exception:
        # fallback create job
        job = AIJob.objects.create(agent_key=key, url=url, created_by=created_by, status='pending')

    # enqueue processing
    try:
        if hasattr(process_ai_job, 'delay'):
            process_ai_job.delay(job.id)
        else:
            process_ai_job(job.id)
    except Exception:
        # synchronous fallback
        process_ai_job(job.id)

    return render(request, 'admin_portal/agent_job_row.html', {'job': job})


@staff_member_required
def start_pipeline(request):
    """Start a full pipeline run for a submitted URL.
    Creates a PipelineRun and enqueues the pipeline processor.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    url = request.POST.get('url') or request.POST.get('input')
    created_by = request.user
    pr = None
    try:
        pr = PipelineRun.objects.create(url=url, status='pending', created_by=created_by)
        job = AIJob.objects.create(
        agent_key='pipeline',
        stage_name='pipeline',
        pipeline_run=pr,
        url=url,
        payload={},
        status='running',
        created_by=created_by,
    )
    except Exception:
        return HttpResponseBadRequest('Could not create pipeline run')

    try:
        if hasattr(process_pipeline_run, 'delay'):
            process_pipeline_run.delay(pr.id)
        else:
            process_pipeline_run(pr.id)
    except Exception:
        process_pipeline_run(pr.id)

    return render(request, 'admin_portal/agent_job_row.html', {'job': pr}, {'job': job})


@staff_member_required
def cancel_agent_job(request, job_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    try:
        job = AIJob.objects.get(pk=job_id)
    except AIJob.DoesNotExist:
        return HttpResponseBadRequest('Unknown job')
    job.status = 'cancelled'
    job.save(update_fields=['status'])
    # attempt to revoke celery task if provided (best-effort)
    return render(request, 'admin_portal/agent_job_row.html', {'job': job})