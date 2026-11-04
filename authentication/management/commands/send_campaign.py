from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from brevo import Brevo
from brevo.core import ApiError

class Command(BaseCommand):
    help = "Create a Brevo email campaign (as a draft unless --schedule is given)"

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--subject", required=True)
        parser.add_argument("--html-file", required=True, help="Path to the HTML body")
        parser.add_argument("--list-id", type=int, action="append", required=True, help="Brevo list ID; repeat for multiple lists")
        parser.add_argument("--schedule", help="UTC time, e.g. 2026-11-10T09:00:00Z")

    def handle(self, *args, **opts):
        if not settings.BREVO_API_KEY:
            raise CommandError("BREVO_API_KEY is not set")
        if not settings.DEFAULT_FROM_EMAIL:
            raise CommandError("DEFAULT_FROM_EMAIL is not set")

        with open(opts["html_file"], encoding="utf-8") as f:
            html = f.read()

        client = Brevo(api_key=settings.BREVO_API_KEY)
        kwargs = dict(
            name=opts["name"],
            subject=opts["subject"],
            sender={"name": "AMRx Hub", "email": settings.DEFAULT_FROM_EMAIL},
            html_content=html,
            recipients={"list_ids": opts["list_id"]},
        )
        if opts["schedule"]:
            kwargs["scheduled_at"] = opts["schedule"]

        try:
            resp = client.email_campaigns.create_email_campaign(**kwargs)
        except ApiError as exc:
            raise CommandError(f"Brevo campaign failed: {exc.status_code} {exc.body}") from exc
        
        self.stdout.write(self.style.SUCCESS(f"Created campaign {resp.id}"))