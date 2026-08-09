OpenAI Integration — admin_portal

This document describes how to wire OpenAI models (your agents on OpenAI Platform) into the admin_portal AI Workspace.

Overview

- The scaffold includes a simple OpenAI wrapper (admin_portal/openai_client.py) and a sample agent (admin_portal/agents/research_openai.py).
- Jobs are recorded in admin_portal.models.AIJob and per-request logs in AIRequestLog.
- Processing is done by admin_portal.tasks.process_ai_job, which uses Celery if installed or runs synchronously as fallback.

Steps to enable and test

1) Install dependencies

   pip install openai
   # If you use Celery for background processing also install:
   pip install celery

2) Set environment variables (DO NOT COMMIT API KEYS)

   export OPENAI_API_KEY="sk-..."
   # If using a custom base for OpenAI-compatible APIs:
   export OPENAI_API_BASE="https://api.openai.com/v1"

3) Database migrations

   python manage.py makemigrations admin_portal
   python manage.py migrate

4) (Optional) Configure Celery

   # Example minimal celery.py inside your project package
   from celery import Celery
   app = Celery('proj')
   app.config_from_object('django.conf:settings', namespace='CELERY')
   app.autodiscover_tasks()

   # set broker (Redis/RabbitMQ) in settings.py
   CELERY_BROKER_URL = 'redis://localhost:6379/0'

   Start worker:
   celery -A your_project_name worker -l info

5) Register your OpenAI agents

   - Create a module under admin_portal/agents/ and use @register_agent(...)
   - Provide submit_job(url, created_by, payload, model) and process_job(job, model) if desired

   Example: admin_portal/agents/research_openai.py already exists; it uses OPENAI via admin_portal.openai_client.

6) Test via UI

   - Run Django server and sign in as staff
   - Visit /portal/ai/ and click the Research Agent (OpenAI)
   - Use the start-job form to submit a URL (agent will create AIJob and enqueue processing)
   - If Celery is running, worker will pick up and update job status; otherwise processing will run synchronously

7) Shell testing (quick)

   python manage.py shell
   from admin_portal.agents.research_openai import submit_job
   from django.contrib.auth import get_user_model
   User = get_user_model()
   submit_job('https://example.com', created_by=User.objects.first())

8) Monitoring

   - AIJob records: check admin or /admin/admin_portal/aijob/
   - AIRequestLog records: /admin/admin_portal/airequestlog/

Security & Cost

- Keep OPENAI_API_KEY secret. Use environment variables or a secrets manager.
- Track token usage in AIRequestLog and set model/timeout/cost guards as needed.

Troubleshooting

- If openai import fails: pip install openai
- If using Celery, ensure broker is reachable and worker started

Next steps

- Implement robust scraping for research agent (use a headless fetcher or micro-service to retrieve page HTML)
- Add retry, backoff, and rate limiting to process_ai_job
- Record estimated cost per request (use per-model pricing)
- Add per-agent configuration in DB (default model, temperature, token limits)
