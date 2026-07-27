from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = "Ensures the site record exists for OAuth configuration"

    def handle(self, *args, **options):
        site_domain = getattr(settings, "SITE_DOMAIN", "amrxhub.com")
        site_name = "AMRx Hub"

        site, created = Site.objects.update_or_create(
            domain=site_domain,
            defaults={"name": site_name},
        )

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} site: {site.domain} (id={site.id})"))