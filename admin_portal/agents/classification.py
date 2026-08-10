from admin_portal.ai_registry import register_agent
from admin_portal.models import AIJob

@register_agent('classification', 'Classification Agent', description='Classify resource into AMRx taxonomy')
def classification_info():
    return {
        'key': 'classification',
        'label': 'Classification Agent',
        'description': 'Classifies content according to AMRx taxonomy',
        'status': 'active',
    }


def submit_job(url, created_by=None, payload=None):
    return AIJob.objects.create(agent_key='classification', url=url, payload=payload or {}, created_by=created_by, status='pending')


def process_job(job: AIJob):
    # naive classification stub: copy shared payload and add taxonomy placeholder
    payload = job.payload or {}
    text = payload.get('result_text') or payload.get('text') or ''
    # For now, produce a simple classification based on keywords
    category = 'unknown'
    if 'genome' in (text or '').lower():
        category = 'Genomics'
    elif 'workflow' in (text or '').lower():
        category = 'Workflow'
    else:
        category = 'General'

    payload['classification'] = {
        'category': category,
        'confidence': 0.6,
    }
    job.payload = payload
    job.status = 'completed'
    job.finished_at = job.finished_at or job.started_at
    job.save()
    return job
