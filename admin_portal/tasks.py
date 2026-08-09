"""
Asynchronous task handling for admin_portal AI jobs.
This uses Celery if available; otherwise provides a synchronous fallback function.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
    HAS_CELERY = True
except Exception:
    HAS_CELERY = False

from .models import AIJob
from .ai_registry import get_agent


if HAS_CELERY:
    @shared_task(bind=True)
    def process_ai_job(self, job_id: int):
        try:
            job = AIJob.objects.get(pk=job_id)
        except AIJob.DoesNotExist:
            logger.error('AIJob %s does not exist', job_id)
            return
        agent = get_agent(job.agent_key)
        if not agent:
            job.status = 'failed'
            job.save(update_fields=['status'])
            return
        # agent callable may be function or class; prefer a 'process_job' function on agent module
        callable_obj = agent.get('callable')
        # If the registered callable is a function that exposes process_job, try module lookup
        # If callable is a class, try to call a class method process_job
        try:
            # many agent modules expose process_job(job, **kwargs)
            if hasattr(callable_obj, 'process_job'):
                callable_obj.process_job(job)
            else:
                # callable_obj might be a function; attempt to import module and call process_job
                # best-effort: try attribute on module
                if hasattr(callable_obj, '__module__'):
                    mod = __import__(callable_obj.__module__, fromlist=[''])
                    if hasattr(mod, 'process_job'):
                        getattr(mod, 'process_job')(job)
                    else:
                        # fallback: if callable itself is a function, try calling it with job
                        try:
                            callable_obj(job)
                        except TypeError:
                            job.status = 'failed'
                            job.save(update_fields=['status'])
                else:
                    job.status = 'failed'
                    job.save(update_fields=['status'])
        except Exception as exc:
            logger.exception('Error processing job %s', job_id)
            job.status = 'failed'
            job.save(update_fields=['status'])


else:
    def process_ai_job(job_id: int):
        # synchronous fallback for environments without Celery
        try:
            job = AIJob.objects.get(pk=job_id)
        except AIJob.DoesNotExist:
            logger.error('AIJob %s does not exist', job_id)
            return
        agent = get_agent(job.agent_key)
        if not agent:
            job.status = 'failed'
            job.save(update_fields=['status'])
            return
        callable_obj = agent.get('callable')
        try:
            if hasattr(callable_obj, 'process_job'):
                callable_obj.process_job(job)
            else:
                if hasattr(callable_obj, '__module__'):
                    mod = __import__(callable_obj.__module__, fromlist=[''])
                    if hasattr(mod, 'process_job'):
                        getattr(mod, 'process_job')(job)
                    else:
                        try:
                            callable_obj(job)
                        except TypeError:
                            job.status = 'failed'
                            job.save(update_fields=['status'])
                else:
                    job.status = 'failed'
                    job.save(update_fields=['status'])
        except Exception:
            logger.exception('Error processing job %s', job_id)
            job.status = 'failed'
            job.save(update_fields=['status'])
