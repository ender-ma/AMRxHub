from django.conf import settings


def test_openai_default_model_present():
    assert hasattr(settings, 'OPENAI_DEFAULT_MODEL')
    assert settings.OPENAI_DEFAULT_MODEL == 'gpt-5.6-terra'
