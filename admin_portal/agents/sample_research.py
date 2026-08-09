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


def list_jobs(limit=50):
    return AIJob.objects.filter(agent_key='sample_research').order_by('-created_at')[:limit]
