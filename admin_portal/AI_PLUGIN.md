AI Plugin Registry — admin_portal/ai_registry.py

Overview

This repository includes a simple plugin registry for AI agents used by the Administration Portal. The registry enables pluggable agents to appear in the AI Workspace and expose a consistent metadata surface to the UI.

Files

- admin_portal/ai_registry.py
  - register_agent(key, label, description, status): decorator used to register an agent. Stores callable and metadata in an in-memory registry.
  - list_agents(): returns list of registered agents (metadata only).
  - get_agent(key): returns the registered agent metadata dict (including 'callable').

- admin_portal/agents/
  - Example agents live here. Each agent module should register itself with the registry using the decorator.

Design principles

- Minimal API surface: agents should implement a callable that returns metadata and optionally provide helper functions to submit/list jobs.
- Storage: the scaffold includes admin_portal.models.AIJob and AIRequestLog models to store jobs and per-request logs. Agents should create AIJob entries when submitting work.
- Extensibility: new agents can be added by creating a module under admin_portal/agents and calling @register_agent(...).

Recommended agent contract

- register with: @register_agent('key', 'Label', description='...', status='active')
- expose optional helpers:
  - submit_job(url, created_by=None, payload=None)
  - list_jobs(limit=50)
  - cancel_job(job_id)

Example: admin_portal/agents/sample_research.py

    from admin_portal.ai_registry import register_agent
    from admin_portal.models import AIJob

    @register_agent('sample_research', 'Sample Research Agent', description='Sample research agent for testing')
    def sample_research_info():
        return {...}

    def submit_job(url, created_by=None, payload=None):
        return AIJob.objects.create(agent_key='sample_research', url=url, payload=payload or {}, created_by=created_by, status='pending')

Notes

- This registry is intentionally simple to be easy to extend. For production, consider plugin discovery, registration via app config, and persistent configuration.
- Agents are expected to be the bridge to a worker system (Celery/RQ) for heavy processing. The registry only provides metadata and helper functions — it does not execute long-running code in-process.
