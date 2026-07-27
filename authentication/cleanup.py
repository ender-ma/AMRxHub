from django.conf import settings
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from allauth.socialaccount.models import SocialApp

count = SocialApp.objects.filter(provider="google").count()
SocialApp.objects.filter(provider="google").delete()
print(f"Deleted {count} Google apps")
print("Database cleanup complete!")