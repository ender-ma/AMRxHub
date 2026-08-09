from admin_portal.ai_registry import register_agent
from admin_portal.models import AIJob, AIRequestLog
from admin_portal.openai_client import call_chat_model
from django.utils import timezone

@register_agent('research_openai', 'Research Agent (OpenAI)', description='Extracts summary and metadata using OpenAI models', status='active')
def research_openai_info():
    return {
        'key': 'research_openai',
        'label': 'Research Agent (OpenAI)',
        'description': 'Uses OpenAI models to summarise and extract metadata from a submitted URL',
        'status': 'active',
    }


def submit_job(url, created_by=None, payload=None, model='gpt-4o-mini'):
    job = AIJob.objects.create(agent_key='research_openai', url=url, payload=payload or {}, created_by=created_by, status='pending')
    # caller (UI) should enqueue a worker to process this job. We return the created job.
    return job


def process_job(job: AIJob, model: str = 'gpt-4o-mini') -> AIJob:
    """Synchronous processing. For production, run via a Celery worker (admin_portal.tasks.process_ai_job).
    This minimal implementation sends a chat prompt to the OpenAI model and stores a single log entry.
    """
    prompt_system = "You are a metadata extraction assistant. Given a URL, extract title, summary, authors, publication_date, doi (if present), and list any missing metadata. Return JSON only."
    prompt_user = f"Process this URL and return structured JSON: {job.url}\nReturn keys: title, summary, authors, publication_date, doi, license, institution, website, screenshots, missing_fields"

    messages = [
        {'role': 'system', 'content': prompt_system},
        {'role': 'user', 'content': prompt_user},
    ]

    job.status = 'running'
    job.started_at = timezone.now()
    job.save(update_fields=['status', 'started_at'])

    try:
        resp = call_chat_model(model=model, messages=messages, temperature=0)
        # store log
        log = AIRequestLog.objects.create(
            job=job,
            model=model,
            prompt_version='1',
            tokens_in=resp.get('usage', {}).get('prompt_tokens', 0) or 0,
            tokens_out=resp.get('usage', {}).get('completion_tokens', 0) or 0,
            cost=0,
            latency_ms=0,
            success=True,
            response=resp.get('raw'),
        )
        # attempt to parse text as JSON summary (best-effort)
        text = resp.get('text') or ''
        job.payload['result_text'] = text
        job.status = 'completed'
        job.finished_at = timezone.now()
        job.tokens_used = (log.tokens_in or 0) + (log.tokens_out or 0)
        job.save()
    except Exception as exc:
        AIRequestLog.objects.create(job=job, model=model, success=False, error=str(exc))
        job.status = 'failed'
        job.finished_at = timezone.now()
        job.save()
    return job
