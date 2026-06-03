import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Delete ALL existing Google apps
count = SocialApp.objects.filter(provider='google').count()
SocialApp.objects.filter(provider='google').delete()
print(f"Deleted {count} Google apps")

# Make sure there's exactly one site with ID 1
Site.objects.all().delete()
site = Site.objects.create(id=1, domain='127.0.0.1:8000', name='localhost')
print(f"Created site: {site.domain}")

# Create ONE new Google app
app = SocialApp.objects.create(
    provider='google',
    name='Google',
    client_id='876154968492-g59fkpqkgtrl3bpaf7h4k5qu4bue3s31.apps.googleusercontent.com',
    secret='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'
)
app.sites.add(site)
app.save()
print(f"Created Google app: {app.client_id}")
print("Database cleanup complete!")