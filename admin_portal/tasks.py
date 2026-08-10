"""
Asynchronous task handling for admin_portal AI jobs.
This uses Celery if available; otherwise provides a synchronous fallback function.
Also exposes a pipeline runner task.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
    HAS_CELERY = True
except Exception:
    HAS_CELERY = False

from .models import AIJob, PipelineRun
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
        except Exception as exc:
            logger.exception('Error processing job %s', job_id)
            job.status = 'failed'
            job.save(update_fields=['status'])

    @shared_task(bind=True)
    def process_pipeline_run(self, pipeline_run_id: int):
        # import locally to avoid cycles
        from .services import run_pipeline
        try:
            run_pipeline(pipeline_run_id)
        except Exception:
            logger.exception('Error processing pipeline %s', pipeline_run_id)


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

    def process_pipeline_run(pipeline_run_id: int):
        from .services import run_pipeline
        try:
            run_pipeline(pipeline_run_id)
        except Exception:
            logger.exception('Error processing pipeline %s', pipeline_run_id)
