import logging
import requests
from django.utils import timezone
from admin_portal.ai_registry import register_agent
from admin_portal.models import AIJob

logger = logging.getLogger(__name__)

@register_agent("collection", "Collection Agent", description="Fetch and extract content from URLs")
def collection_info():
    return {
        "key": "collection",
        "label": "Collection Agent",
        "description": "Fetches webpage content and extracts text/metadata",
        "status": "active",
    }

def submit_job(url, created_by=None, payload=None):
    return AIJob.objects.create(
        agent_key="collection",
        url=url,
        payload=payload or {},
        created_by=created_by,
        status="pending"
    )

def process_job(job: AIJob):
    payload = job.payload or {}
    url = job.url
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, timeout=10, headers=headers)
        resp.raise_for_status()
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)[:2000]
            title = soup.title.string if soup.title and soup.title.string else url.split("/")[-1]
            meta_desc = ""
            meta = soup.find("meta", attrs={"name": "description"})
            if meta:
                meta_desc = meta.get("content", "")
        except Exception:
            text = resp.text[:2000]
            title = url.split("/")[-1]
            meta_desc = ""
        
        payload["url_fetched"] = url
        payload["raw_text"] = text
        payload["title"] = title or ""
        payload["description"] = meta_desc or ""
        job.payload = payload
        job.status = "completed"
        job.finished_at = timezone.now()
        job.save()
    except Exception as exc:
        logger.error("Collection failed: %s", str(exc))
        payload["error"] = str(exc)
        job.payload = payload
        job.status = "failed"
        job.finished_at = timezone.now()
        job.save()
    return job
