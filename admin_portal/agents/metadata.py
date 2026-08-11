from admin_portal.ai_registry import register_agent
from admin_portal.models import AIJob

@register_agent('metadata', 'Metadata Agent', description='Add structured metadata')
def metadata_info():
    return {
        'key': 'metadata',
        'label': 'Metadata Agent',
        'description': 'Extracts/normalizes metadata fields',
        'status': 'active',
    }


def submit_job(url, created_by=None, payload=None):
    return AIJob.objects.create(agent_key='metadata', url=url, payload=payload or {}, created_by=created_by, status='pending')


def process_job(job: AIJob):
    payload = job.payload or {}
    payload['title'] = payload.get('title') or ''
    payload['authors'] = payload.get('authors') or payload.get('research', {}).get('extracted_authors', [])
    payload['publication_date'] = payload.get('publication_date') or ''
    payload['doi'] = payload.get('doi') or ''
    payload['license'] = payload.get('license') or ''

    job.payload = payload
    job.status = 'completed'
    job.finished_at = job.finished_at or job.started_at
    job.save()
    return job
