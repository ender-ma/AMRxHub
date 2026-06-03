from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db import migrations, models

class ToolCategory(models.Model):
    CATEGORY_TYPE_CHOICES = (
        ('organism', 'Organism Specific'),
        ('general', 'General Use'),
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(
        max_length=50, 
        default='fas fa-tools',
        help_text="FontAwesome icon class (e.g., 'fas fa-microscope', 'fas fa-chart-bar')"
    )
    color = models.CharField(
        max_length=7, 
        default='#667eea',
        help_text="Hex color code for category card"
    )
    order = models.IntegerField(default=0, help_text="Order in which categories appear")
    is_active = models.BooleanField(default=True)
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES,
        default='general',
        help_text="Choose if this category is for general use or organism specific tools"
    )
    detailed_description = models.TextField(
        blank=True,
        help_text="Long, detailed description for this category. Shown at the top of the category page."
    )
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
    name = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(
        max_length=300, 
        help_text="Brief description shown on tool cards"
    )
    category = models.ForeignKey(
        ToolCategory, 
        on_delete=models.CASCADE, 
        related_name='tools'
    )
    
    # Tool Access
    url = models.URLField(
        help_text="External URL where the tool is hosted"
    )
    tool_type = models.CharField(
        max_length=20, 
        choices=TOOL_TYPES, 
        default='web'
    )
    
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

class AnalysisHistory(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tool = models.ForeignKey('Tool', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    used_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Add status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Files for input and results
    uploaded_file = models.FileField(upload_to='user_uploads/', null=True, blank=True)
    result_file = models.FileField(upload_to='analysis_results/', null=True, blank=True)
    
    # Error message if analysis fails
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.tool.name} by {self.user.username} at {self.used_at}"
    
    def duration(self):
        if not self.completed_at or self.status in ['pending', 'processing']:
            return None
        return self.completed_at - self.used_at
