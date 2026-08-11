from admin_portal.models import AIJob, PipelineRun
from admin_portal.tasks import process_pipeline_run

pr = PipelineRun.objects.get(pk=16)
if pr.jobs.exists():
    job = pr.jobs.first()
    print(f"Job {job.id} status: {job.status}")
    print(f"Payload: {job.payload}")
    if job.logs.exists():
        for log in job.logs.all():
            if log.error:
                print(f"Error: {log.error}")
