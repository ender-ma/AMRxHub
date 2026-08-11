from django.conf import settings


def get_ai_model(agent_key: str | None = None) -> str:
    """Return the model to use for an agent. Priority:
    1. DB AIPreferences per-agent field
    2. DB AIPreferences.default_model
    3. Django settings per-agent env var (e.g., RESEARCH_AGENT_MODEL)
    4. Django settings OPENAI_DEFAULT_MODEL
    """
    # import models lazily to avoid import-time app registry issues during test discovery
    try:
        from .models import AIPreferences
    except Exception:
        AIPreferences = None

    prefs = None
    if AIPreferences is not None:
        try:
            prefs = AIPreferences.objects.first()
        except Exception:
            prefs = None

    if prefs:
        if agent_key == 'research' and prefs.research_model:
            return prefs.research_model
        if agent_key == 'classification' and prefs.classification_model:
            return prefs.classification_model
        if agent_key == 'metadata' and prefs.metadata_model:
            return prefs.metadata_model
        if agent_key == 'quality' and prefs.quality_model:
            return prefs.quality_model
        if prefs.default_model:
            return prefs.default_model
    # fallback to settings
    if agent_key == 'research':
        return getattr(settings, 'RESEARCH_AGENT_MODEL', getattr(settings, 'OPENAI_DEFAULT_MODEL', 'gpt-5.6-terra'))
    if agent_key == 'classification':
        return getattr(settings, 'CLASSIFICATION_AGENT_MODEL', getattr(settings, 'OPENAI_DEFAULT_MODEL', 'gpt-5.6-terra'))
    if agent_key == 'metadata':
        return getattr(settings, 'METADATA_AGENT_MODEL', getattr(settings, 'OPENAI_DEFAULT_MODEL', 'gpt-5.6-terra'))
    if agent_key == 'quality':
        return getattr(settings, 'QUALITY_AGENT_MODEL', getattr(settings, 'OPENAI_DEFAULT_MODEL', 'gpt-5.6-terra'))
    return getattr(settings, 'OPENAI_DEFAULT_MODEL', 'gpt-5.6-terra')
