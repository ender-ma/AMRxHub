from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Sets up OAuth providers'

    def handle(self, *args, **options):
        # Get or create site
        site, _ = Site.objects.get_or_create(id=1)
        
        # Update site domain to match your production domain
        site.domain = 'amrxhub.up.railway.app'
        site.name = 'AMR X Hub'
        site.save()
        
        self.stdout.write(self.style.SUCCESS(f'Updated site: {site.domain}'))
        
        # Clean up existing Google apps
        existing_apps = SocialApp.objects.filter(provider='google')
        
        if existing_apps.count() > 1:
            # Keep only the most recent one
            app_to_keep = existing_apps.order_by('-id')[0]
            for app in existing_apps:
                if app.id != app_to_keep.id:
                    self.stdout.write(f'Deleting app ID {app.id}: {app.name}')
                    app.delete()
            self.stdout.write(self.style.SUCCESS(f'Kept only one Google OAuth app (ID: {app_to_keep.id})'))
            
            # Update the remaining app
            app_to_keep.client_id = '876154968492-g59fkpqkgtrl3bpaf7h4k5qu4bue3s31.apps.googleusercontent.com'
            app_to_keep.secret = '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'
            app_to_keep.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Google OAuth app (ID: {app_to_keep.id})'))
        elif existing_apps.exists():
            # Update the existing app
            app = existing_apps.first()
            app.client_id = '876154968492-g59fkpqkgtrl3bpaf7h4k5qu4bue3s31.apps.googleusercontent.com'
            app.secret = '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'
            app.save()
            self.stdout.write(self.style.SUCCESS(f'Updated existing Google OAuth app (ID: {app.id})'))
        else:
            # Create Google provider
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id='876154968492-g59fkpqkgtrl3bpaf7h4k5qu4bue3s31.apps.googleusercontent.com',
                secret='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'
            )
            google_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('Successfully created Google OAuth app'))