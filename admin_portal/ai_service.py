from django.conf import settings
from django.utils import timezone
from .models import AIJob, PipelineRun
from .ai_registry import get_agent
from .tasks import process_ai_job, process_pipeline_run
import logging

logger = logging.getLogger(__name__)


def submit_ai_job(url: str, agent_key: str = 'research', created_by=None, payload: dict = None, model: str = None) -> AIJob:
    """Create an AIJob and enqueue processing via Celery if available, otherwise run synchronously."""
    job = AIJob.objects.create(agent_key=agent_key, url=url, payload=payload or {}, status='pending', created_by=created_by)
    try:
        if hasattr(process_ai_job, 'delay'):
            process_ai_job.delay(job.id)
        else:
            process_ai_job(job.id)
    except Exception:
        logger.exception('Failed to enqueue AI job, attempting synchronous processing')
        try:
            process_ai_job(job.id)
        except Exception:
            logger.exception('Synchronous processing failed for job %s', job.id)
    return job


def run_research_agent(job_id: int):
    job = AIJob.objects.get(pk=job_id)
    agent = get_agent(job.agent_key)
    if not agent:
        raise RuntimeError('Agent not found')
    callable_obj = agent.get('callable')
    if hasattr(callable_obj, 'process_job'):
        return callable_obj.process_job(job)
    else:
        # fallback to module-level process_job
        module = __import__(callable_obj.__module__, fromlist=[''])
        if hasattr(module, 'process_job'):
            return getattr(module, 'process_job')(job)
        raise RuntimeError('Agent callable has no process_job')


def start_pipeline(url: str, created_by=None) -> PipelineRun:
    pr = PipelineRun.objects.create(url=url, status='pending', created_by=created_by)
    try:
        if hasattr(process_pipeline_run, 'delay'):
            process_pipeline_run.delay(pr.id)
        else:
            process_pipeline_run(pr.id)
    except Exception:
        logger.exception('Failed to enqueue pipeline run, attempting synchronous processing')
        process_pipeline_run(pr.id)
    return pr


def get_ai_job(job_id: int) -> AIJob:
    return AIJob.objects.get(pk=job_id)


def retry_ai_job(job_id: int):
    job = AIJob.objects.get(pk=job_id)
    job.attempts = job.attempts + 1
    job.status = 'pending'
    job.save(update_fields=['attempts', 'status'])
    submit_ai_job(job.url, agent_key=job.agent_key, created_by=job.created_by, payload=job.payload)
    return job


def cancel_ai_job(job_id: int):
    job = AIJob.objects.get(pk=job_id)
    job.status = 'cancelled'
    job.finished_at = timezone.now()
    job.save(update_fields=['status', 'finished_at'])
    return job
