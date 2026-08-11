from admin_portal.models import PipelineRun
from admin_portal.tasks import process_pipeline_run

pr = PipelineRun.objects.create(url="https://github.com/ender-ma/AMRxHub", created_by_id=2)
print(f"Pipeline {pr.id} created")

process_pipeline_run(pr.id)

pr.refresh_from_db()
print(f"Status: {pr.status}")
print(f"Stages: {list(pr.stages.keys())}")
print(f"Payload keys: {list(pr.shared_payload.keys())}")
