from admin_portal.ai_registry import register_agent
from admin_portal.models import AIJob, AIRequestLog
from admin_portal.openai_client import call_chat_model
from admin_portal import fetcher
from django.utils import timezone

@register_agent('research_openai', 'Research Agent (OpenAI)', description='Extracts summary and metadata using OpenAI models', status='active')
def research_openai_info():
    return {
        'key': 'research_openai',
        'label': 'Research Agent (OpenAI)',
        'description': 'Uses OpenAI models to summarise and extract metadata from a submitted URL',
        'status': 'active',
    }


def submit_job(url, created_by=None, payload=None, model=None):
    from django.conf import settings
    if not model:
        model = settings.RESEARCH_AGENT_MODEL or settings.OPENAI_DEFAULT_MODEL
    job = AIJob.objects.create(agent_key='research_openai', url=url, payload=payload or {}, created_by=created_by, status='pending')
    # caller (UI) should enqueue a worker to process this job. We return the created job.
    return job


def process_job(job: AIJob, model: str = None) -> AIJob:
    """Synchronous processing. For production, run via a Celery worker (admin_portal.tasks.process_ai_job).
    This implementation fetches the URL content before calling the model and stores raw_text in payload.
    """
    from django.conf import settings
    if not model:
        model = settings.RESEARCH_AGENT_MODEL or settings.OPENAI_DEFAULT_MODEL

    # Fetch page HTML/text with retries
    try:
        fetch_timeout = getattr(settings, 'RESEARCH_FETCH_TIMEOUT', None)
        fetched = fetcher.fetch_url(job.url, timeout=fetch_timeout)
        raw_text = fetched.get('text', '')
        job.payload = job.payload or {}
        job.payload['raw_text'] = raw_text
        job.payload['fetched_headers'] = fetched.get('headers', {})
    except Exception as e:
        # Log fetch failure but continue — model may still work from URL
        job.payload = job.payload or {}
        job.payload['raw_text'] = ''
        job.payload['fetch_error'] = str(e)

    prompt_system = "You are a metadata extraction assistant. Given a URL and page text, extract title, summary, authors, publication_date, doi (if present), and list any missing metadata. Return JSON only."
    snippet = (job.payload.get('raw_text') or '')[:12000]
    prompt_user = f"Process this URL and return structured JSON. URL: {job.url}\nPage text (truncated): {snippet}\nReturn keys: title, summary, authors, publication_date, doi, license, institution, website, screenshots, missing_fields"

    messages = [
        {'role': 'system', 'content': prompt_system},
        {'role': 'user', 'content': prompt_user},
    ]

    job.status = 'running'
    job.started_at = timezone.now()
    job.save(update_fields=['status', 'started_at', 'payload'])

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
        # capture text result
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
