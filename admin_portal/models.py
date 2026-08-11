from django.db import models
from django.conf import settings

class PipelineRun(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('running','Running'),
        ('completed','Completed'),
        ('failed','Failed'),
        ('cancelled','Cancelled'),
    ]
    url = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    current_stage = models.CharField(max_length=100, blank=True, null=True)
    stages = models.JSONField(default=dict, blank=True)  # map stage -> {status, job_id, error}
    shared_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pipeline Run'
        verbose_name_plural = 'Pipeline Runs'

    def __str__(self):
        return f"PipelineRun {self.pk} ({self.status}) - {self.url}"


class AIJob(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('running','Running'),
        ('completed','Completed'),
        ('failed','Failed'),
        ('cancelled','Cancelled'),
    ]
    agent_key = models.CharField(max_length=100, db_index=True)
    stage_name = models.CharField(max_length=100, blank=True, null=True)
    pipeline_run = models.ForeignKey(PipelineRun, on_delete=models.CASCADE, null=True, blank=True, related_name='jobs')
    external_id = models.CharField(max_length=200, blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    payload = models.JSONField(blank=True, null=True, default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    attempts = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Job'
        verbose_name_plural = 'AI Jobs'

    def __str__(self):
        return f"{self.agent_key} job {self.pk} ({self.status})"


class AIRequestLog(models.Model):
    job = models.ForeignKey(AIJob, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    model = models.CharField(max_length=150, blank=True)
    prompt_version = models.CharField(max_length=200, blank=True)
    tokens_in = models.IntegerField(default=0)
    tokens_out = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    latency_ms = models.IntegerField(default=0)
    success = models.BooleanField(default=True)
    error = models.TextField(blank=True)
    response = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'AI Request Log'
        verbose_name_plural = 'AI Request Logs'

    def __str__(self):
        return f"Log {self.pk} for job {self.job_id} at {self.timestamp}"


class AIContentSuggestion(models.Model):
    OBJECT_TYPES = [
        ("tool", "Tool"),
        ("resource", "Resource"),
    ]
    STATUS_CHOICES = [
        ("pending_review", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("archived", "Archived"),
    ]

    object_type = models.CharField(max_length=50, choices=OBJECT_TYPES, default="tool", db_index=True)
    title = models.CharField(max_length=300, blank=True)
    short_description = models.TextField(blank=True)
    detailed_metadata = models.JSONField(blank=True, default=dict)
    provenance = models.JSONField(blank=True, default=dict)
    url = models.TextField(blank=True, null=True)
    confidence_score = models.FloatField(default=0.0)
    quality_score = models.FloatField(default=0.0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending_review", db_index=True)
    pipeline_run = models.ForeignKey(PipelineRun, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_suggestions')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_suggestions_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Content Suggestion'
        verbose_name_plural = 'AI Content Suggestions'

    def __str__(self):
        return f"Suggestion {self.pk} - {self.title or self.url or 'unnamed'}"


class AIPreferences(models.Model):
    """Singleton-ish model for AI-related site preferences editable via admin.
    Do NOT store secrets (API keys) here.
    """
    default_model = models.CharField(max_length=150, blank=True, help_text='Fallback model for agents')
    research_model = models.CharField(max_length=150, blank=True)
    classification_model = models.CharField(max_length=150, blank=True)
    metadata_model = models.CharField(max_length=150, blank=True)
    quality_model = models.CharField(max_length=150, blank=True)
    research_fetch_timeout = models.IntegerField(default=30)
    research_fetch_retries = models.IntegerField(default=3)

    class Meta:
        verbose_name = 'AI Preferences'
        verbose_name_plural = 'AI Preferences'

    def __str__(self):
        return 'AI Preferences'
