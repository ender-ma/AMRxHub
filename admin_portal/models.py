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
