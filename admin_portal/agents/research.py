import logging
from admin_portal.ai_registry import register_agent
from admin_portal.models import AIJob
from django.utils import timezone

logger = logging.getLogger(__name__)

@register_agent("research", "Research Agent", description="Analyze and extract metadata from content")
def research_info():
    return {
        "key": "research",
        "label": "Research Agent",
        "description": "Analyzes content to extract key metadata",
        "status": "active",
    }

def submit_job(url, created_by=None, payload=None):
    return AIJob.objects.create(
        agent_key="research",
        url=url,
        payload=payload or {},
        created_by=created_by,
        status="pending"
    )

def process_job(job: AIJob):
    payload = job.payload or {}
    text = payload.get("raw_text", "")
    
    authors = []
    keywords = []
    if text:
        keywords = [w.strip() for w in text.split()[:5]]
    
    research_indicators = ["study", "research", "genome", "amr", "bacteria"]
    is_research = any(ind in (text or "").lower() for ind in research_indicators)
    
    payload["research"] = {
        "extracted_authors": authors,
        "keywords": keywords,
        "is_research": is_research,
    }
    
    job.payload = payload
    job.status = "completed"
    job.finished_at = timezone.now()
    job.save()
    
    return job
