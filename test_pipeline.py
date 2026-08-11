from admin_portal.models import PipelineRun
from admin_portal.tasks import process_pipeline_run

pr = PipelineRun.objects.create(url='https://example.com/amr-database', created_by_id=2)
print(f"Created pipeline run: {pr.id}")

print("\nRunning pipeline...")
process_pipeline_run(pr.id)

pr.refresh_from_db()
print(f"\n=== RESULT ===")
print(f"Status: {pr.status}")
print(f"Final payload: {pr.shared_payload}")
print(f"\nStage breakdown:")
for stage, info in pr.stages.items():
    status = info.get('status')
    job_id = info.get('job_id')
    print(f"  {stage:20s} -> {status:12s} (job #{job_id})")
