from django.db import models

class Advertisement(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='adverts/')
    url = models.URLField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    display_duration = models.IntegerField(default=5)  # seconds per image
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def __str__(self):
        return self.title

class Announcement(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    description = models.TextField()
    photo = models.ImageField(upload_to='team_photos/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name
