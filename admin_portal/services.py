import importlib
import logging
from django.conf import settings
from django.utils import timezone
from .models import PipelineRun, AIJob
from .ai_registry import get_agent

logger = logging.getLogger(__name__)

DEFAULT_PIPELINE = getattr(settings, 'ADMIN_PORTAL_PIPELINE', [
    'collection',
    'research',
    'classification',
    'metadata',
    'quality',
])


def run_pipeline(pipeline_run_id: int):
    """Run a pipeline synchronously. Creates AIJob per stage and updates PipelineRun.shared_payload.
    Designed to be called from a Celery task or synchronously as fallback.
    """
    pr = PipelineRun.objects.get(pk=pipeline_run_id)
    pr.status = 'running'
    pr.started_at = timezone.now()
    pr.save(update_fields=['status', 'started_at'])

    agent_sequence = DEFAULT_PIPELINE
    shared = pr.shared_payload or {}

    for key in agent_sequence:
        pr.current_stage = key
        pr.save(update_fields=['current_stage'])
        agent = get_agent(key)
        if not agent:
            pr.stages[key] = {'status': 'failed', 'error': 'agent_not_found'}
            pr.status = 'failed'
            pr.save(update_fields=['stages', 'status'])
            return pr

        # create job for this stage
        job = AIJob.objects.create(
            agent_key=key,
            stage_name=key,
            pipeline_run=pr,
            url=pr.url,
            payload=shared,
            status='pending',
            created_by=pr.created_by,
        )
        pr.stages[key] = {'status': 'running', 'job_id': job.id}
        pr.save(update_fields=['stages'])

        callable_obj = agent.get('callable')
        try:
            job.status = 'running'
            job.started_at = timezone.now()
            job.save(update_fields=['status', 'started_at'])
            module = importlib.import_module(callable_obj.__module__)
            if not hasattr(module, 'process_job'):
                raise RuntimeError(f'{key} agent does not define process_job(job)')
            job = module.process_job(job)
            shared = job.payload or shared
            pr.shared_payload = shared
            pr.stages[key] = {'status': job.status, 'job_id': job.id}
            pr.save(update_fields=['shared_payload', 'stages'])
            if job.status != 'completed':
                pr.status = 'failed'
                pr.save(update_fields=['status'])
                return pr
        except Exception as exc:
            logger.exception('Stage %s failed for pipeline %s', key, pr.id)
            job.status = 'failed'
            job.finished_at = timezone.now()
            job.save(update_fields=['status', 'finished_at'])
            pr.stages[key] = {'status': 'failed', 'job_id': job.id, 'error': str(exc)}
            pr.status = 'failed'
            pr.save(update_fields=['stages', 'status'])
            return pr

    pr.status = 'completed'
    pr.finished_at = timezone.now()
    pr.current_stage = None
    pr.save(update_fields=['status', 'finished_at', 'current_stage'])
    return pr
