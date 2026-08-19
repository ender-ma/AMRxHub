from django.conf import settings
from django.db import models

class ResourceCategory(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class, e.g. 'fas fa-book'")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return self.name

class ResourceItem(models.Model):
    category = models.ForeignKey(ResourceCategory, related_name='items', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    link = models.URLField(blank=True)
    link_text = models.CharField(max_length=100, blank=True)
    link_icon = models.CharField(max_length=50, blank=True)
    pdf_file = models.FileField(upload_to='resources/pdfs/', blank=True, null=True)
    image = models.ImageField(upload_to='resources/images/', null=True, blank=True)
    APPROVAL_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='approved',
        db_index=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_resource_items'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def is_approved(self):
        return self.approval_status == 'approved'

class Resource(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)