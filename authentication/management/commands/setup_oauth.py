from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = "Sets up OAuth providers"

    def handle(self, *args, **options):
        site_domain = getattr(settings, "SITE_DOMAIN", "amrxhub.com")
        site_name = "AMRx Hub"

        site, _ = Site.objects.update_or_create(
            domain=site_domain,
            defaults={"name": site_name},
        )

        existing_apps = SocialApp.objects.filter(provider="google")

        if existing_apps.count() > 1:
            app_to_keep = existing_apps.order_by("-id").first()
            for app in existing_apps.exclude(id=app_to_keep.id):
                app.delete()
            app = app_to_keep
        elif existing_apps.exists():
            app = existing_apps.first()
        else:
            app = SocialApp.objects.create(
                provider="google",
                name="Google",
                client_id="",
                secret="",
            )

        app.sites.set([site])
        app.save()

        self.stdout.write(self.style.SUCCESS(f"Updated site: {site.domain}"))
        self.stdout.write(self.style.SUCCESS(f"Updated Google OAuth app: {app.id}"))