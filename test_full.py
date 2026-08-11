from admin_portal.models import PipelineRun
from admin_portal.tasks import process_pipeline_run

pr = PipelineRun.objects.create(url="https://www.ncbi.nlm.nih.gov/", created_by_id=2)
print(f"Pipeline {pr.id} running...")

process_pipeline_run(pr.id)

pr.refresh_from_db()
print(f"\nStatus: {pr.status}")
print(f"Stages: {', '.join(pr.stages.keys())}")
print(f"Payload keys: {list(pr.shared_payload.keys())[:5]}")
print(f"Title: {pr.shared_payload.get('"'"'title'"'"', '')[:80]}")
