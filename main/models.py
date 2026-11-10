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


# ---------------------------------------------------------------------------
# Glossary
# ---------------------------------------------------------------------------

from django.conf import settings
from django.utils.text import slugify


class GlossaryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, help_text="Used in glossary links, e.g. #category/core")
    icon = models.CharField(max_length=50, default='fas fa-book', help_text="FontAwesome icon class, e.g. 'fas fa-dna'")
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, help_text="Lower numbers show first")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Glossary category'
        verbose_name_plural = 'Glossary categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:110]
        super().save(*args, **kwargs)


class GlossaryTerm(models.Model):
    APPROVAL_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    category = models.ForeignKey(GlossaryCategory, related_name='terms', on_delete=models.PROTECT)
    term = models.CharField(max_length=200, unique=True, db_index=True)
    slug = models.SlugField(max_length=210, unique=True, blank=True, help_text="Used in glossary links, e.g. #term/plasmid. Filled in automatically if left blank.")
    abbreviation = models.CharField(max_length=30, blank=True)
    definition = models.TextField()
    context = models.TextField(blank=True, help_text="Optional extra explanation shown under 'Scientific Context'")
    references = models.TextField(blank=True, help_text="Optional. One reference per line.")
    related_terms = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='referenced_by')

    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='approved', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_glossary_terms')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_glossary_terms')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_glossary_terms')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['term']

    def __str__(self):
        return f"{self.term} ({self.abbreviation})" if self.abbreviation else self.term

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.abbreviation or self.term)[:200] or 'term'
            slug, n = base, 2
            while GlossaryTerm.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.is_active and self.approval_status == 'approved'

    def get_references_list(self):
        return [line.strip() for line in self.references.splitlines() if line.strip()]
