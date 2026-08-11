from admin_portal.ai_registry import register_agent
from admin_portal.models import AIJob

@register_agent('sample_research', 'Sample Research Agent', description='Sample research agent for testing')
def sample_research_info():
    return {
        'key': 'sample_research',
        'label': 'Sample Research Agent',
        'description': 'Sample research agent used by the admin portal scaffold',
        'status': 'active',
    }


def submit_job(url, created_by=None, payload=None):
    return AIJob.objects.create(agent_key='sample_research', url=url, payload=payload or {}, created_by=created_by, status='pending')


def process_job(job: AIJob):
    # Simple pass-through: mark complete without processing
    payload = job.payload or {}
    payload['sample_research'] = {'processed': True}
    job.payload = payload
    job.status = 'completed'
    job.finished_at = job.finished_at or job.started_at
    job.save()
    return job


def list_jobs(limit=50):
    return AIJob.objects.filter(agent_key='sample_research').order_by('-created_at')[:limit]
