from django.db import models

class ResourceCategory(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class, e.g. 'fas fa-book'")
    description = models.TextField(blank=True)

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

    def __str__(self):
        return self.title

class Resource(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/')