import logging
from django.conf import settings
from django.utils import timezone
from .models import PipelineRun, AIJob
from .ai_registry import get_agent

logger = logging.getLogger(__name__)

DEFAULT_PIPELINE = getattr(settings, "ADMIN_PORTAL_PIPELINE", [
    "collection",
    "research",
    "classification",
    "metadata",
    "quality",
])

def run_pipeline(pipeline_run_id: int):
    pr = PipelineRun.objects.get(pk=pipeline_run_id)
    pr.status = "running"
    pr.started_at = timezone.now()
    pr.save(update_fields=["status", "started_at"])

    agent_sequence = DEFAULT_PIPELINE
    shared = pr.shared_payload or {}

    for key in agent_sequence:
        pr.current_stage = key
        pr.save(update_fields=["current_stage"])
        agent = get_agent(key)
        if not agent:
            pr.stages[key] = {"status": "failed", "error": "agent_not_found"}
            pr.status = "failed"
            pr.save(update_fields=["stages", "status"])
            return pr

        job = AIJob.objects.create(
            agent_key=key,
            stage_name=key,
            pipeline_run=pr,
            url=pr.url,
            payload=shared,
            status="pending",
            created_by=pr.created_by,
        )
        pr.stages[key] = {"status": "running", "job_id": job.id}
        pr.save(update_fields=["stages"])

        callable_obj = agent.get("callable")
        try:
            job.status = "running"
            job.started_at = timezone.now()
            job.save(update_fields=["status", "started_at"])
            if hasattr(callable_obj, "process_job"):
                job = callable_obj.process_job(job)
            else:
                if hasattr(callable_obj, "__module__"):
                    mod = __import__(callable_obj.__module__, fromlist=[""])
                    if hasattr(mod, "process_job"):
                        job = getattr(mod, "process_job")(job)
                    else:
                        try:
                            res = callable_obj(job)
                            if isinstance(res, AIJob):
                                job = res
                        except TypeError:
                            raise RuntimeError("agent callable not invokable")
            shared = job.payload or shared
            pr.shared_payload = shared
            pr.stages[key] = {"status": job.status, "job_id": job.id}
            pr.save(update_fields=["shared_payload", "stages"])
            if job.status != "completed":
                pr.status = "failed"
                pr.save(update_fields=["status"])
                return pr
        except Exception as exc:
            logger.exception("Stage %s failed", key)
            job.status = "failed"
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "finished_at"])
            pr.stages[key] = {"status": "failed", "job_id": job.id, "error": str(exc)}
            pr.status = "failed"
            pr.save(update_fields=["stages", "status"])
            return pr

    pr.status = "completed"
    pr.finished_at = timezone.now()
    pr.current_stage = None
    pr.save(update_fields=["status", "finished_at", "current_stage"])
    return pr

def pipeline_result_to_tool(pipeline_run: PipelineRun) -> dict:
    payload = pipeline_run.shared_payload or {}
    title = payload.get("title", "Untitled")
    description = payload.get("description", "") or payload.get("raw_text", "")[:300]
    classification = payload.get("classification", {})
    category_name = classification.get("category", "General")
    metadata = payload.get("research", {})
    authors = metadata.get("extracted_authors", [])
    
    return {
        "name": title[:200],
        "url": pipeline_run.url,
        "description": description[:500],
        "short_description": description[:300],
        "category_name": category_name,
        "author": ", ".join(authors) if authors else "",
        "approval_status": "pending",
        "tool_type": "web",
        "pipeline_run_id": pipeline_run.id,
    }
