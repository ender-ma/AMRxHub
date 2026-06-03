from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class ResearchInterest(models.Model):
    """Model for predefined research interest categories"""
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Research Interest"
        verbose_name_plural = "Research Interests"

class UserProfile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    department = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Research Information - rename to avoid migration conflicts
    interests = models.ManyToManyField(ResearchInterest, blank=True)
    research_background = models.TextField(blank=True)
    
    # Account Settings
    receive_research_updates = models.BooleanField(default=True)
    receive_email_notifications = models.BooleanField(default=True)
    profile_visibility = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.email}"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

# Create a UserProfile automatically when a new User is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)