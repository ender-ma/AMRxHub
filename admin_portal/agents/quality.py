from admin_portal.ai_registry import register_agent
from admin_portal.models import AIJob

@register_agent('quality', 'Quality Agent', description='Validate completeness and quality')
def quality_info():
    return {
        'key': 'quality',
        'label': 'Quality Agent',
        'description': 'Checks for missing fields and basic quality heuristics',
        'status': 'active',
    }


def submit_job(url, created_by=None, payload=None):
    return AIJob.objects.create(agent_key='quality', url=url, payload=payload or {}, created_by=created_by, status='pending')


def process_job(job: AIJob):
    payload = job.payload or {}
    issues = []
    if not payload.get('title'):
        issues.append('missing_title')
    if not payload.get('authors'):
        issues.append('missing_authors')
    if not payload.get('summary') and not payload.get('result_text'):
        issues.append('missing_summary')

    quality_score = max(0, 1.0 - (len(issues) * 0.2))
    payload['quality'] = {
        'score': round(quality_score, 2),
        'issues': issues,
    }

    job.payload = payload
    job.status = 'completed'
    job.finished_at = job.finished_at or job.started_at
    job.save()
    return job
