from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db import migrations, models

class ToolCategory(models.Model):
    CATEGORY_TYPE_CHOICES = (
        ('organism', 'Organism Specific'),
        ('general', 'General Use'),
    )
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-tools')
    color = models.CharField(max_length=7, default='#667eea')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES,
        default='general',
        db_index=True,
    )
    detailed_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tool Category"
        verbose_name_plural = "Tool Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_tools_count(self):
        return self.tools.filter(is_active=True, approval_status='approved').count()
    
    def get_absolute_url(self):
        return reverse('tools:category_tools', args=[self.id])

class Tool(models.Model):
    TOOL_TYPES = [
        ('web', 'Web-based Tool'),
        ('download', 'Downloadable Software'),
        ('api', 'API Service'),
        ('database', 'Database/Resource'),
        ('standalone', 'Standalone Application'),
    ]
    
    APPROVAL_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    category = models.ForeignKey(ToolCategory, on_delete=models.CASCADE, related_name='tools')
    url = models.URLField()
    tool_type = models.CharField(max_length=20, choices=TOOL_TYPES, default='web', db_index=True)
    ...
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='approved',
        db_index=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)

    # Additional Information
    institution = models.CharField(max_length=200, blank=True)
    author = models.CharField(max_length=200, blank=True)
    version = models.CharField(max_length=50, blank=True)
    license = models.CharField(max_length=100, blank=True)
    
    # Media
    logo = models.ImageField(
        upload_to='tool_logos/', 
        blank=True, 
        null=True,
        help_text="Tool logo/icon (recommended: 200x200px)"
    )
    screenshot = models.ImageField(
        upload_to='tool_screenshots/', 
        blank=True, 
        null=True,
        help_text="Tool screenshot (optional)"
    )
    
    # Requirements/Features
    requirements = models.TextField(
        blank=True,
        help_text="System requirements or prerequisites"
    )
    features = models.TextField(
        blank=True,
        help_text="Key features (one per line)"
    )
    
    # Admin/Management
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='approved'  # Changed from 'pending' to 'approved'
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='added_tools'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_tools'
    )
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Analytics
    click_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Tool"
        verbose_name_plural = "Tools"
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    @property
    def is_approved(self):
        return self.approval_status == 'approved'
    
    def get_absolute_url(self):
        return reverse('tools:tool_detail', args=[self.id])
    
    def get_features_list(self):
        if self.features:
            return [feature.strip() for feature in self.features.split('\n') if feature.strip()]
        return []

class ToolClick(models.Model):
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='clicks')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tool Click"
        verbose_name_plural = "Tool Clicks"

