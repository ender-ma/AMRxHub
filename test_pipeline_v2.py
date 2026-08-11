from admin_portal.models import PipelineRun
from admin_portal.tasks import process_pipeline_run

# Create a pipeline
pr = PipelineRun.objects.create(url="https://github.com", created_by_id=2)
print(f"Created pipeline {pr.id}")

# Run it
process_pipeline_run(pr.id)

# Check result
pr.refresh_from_db()
print(f"\nStatus: {pr.status}")
print(f"Stages completed: {list(pr.stages.keys())}")
print(f"\nFinal payload keys: {list(pr.shared_payload.keys())}")
if "title" in pr.shared_payload:
    print(f"Title: {pr.shared_payload['title']}")
if "description" in pr.shared_payload:
    desc = pr.shared_payload['description'][:100]
    print(f"Description: {desc}...")
