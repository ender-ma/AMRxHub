import os

import sib_api_v3_sdk
from django.core.management.base import BaseCommand
from sib_api_v3_sdk.rest import ApiException


class Command(BaseCommand):
    help = "Create a Brevo email campaign"

    def handle(self, *args, **options):
        api_key = os.getenv("BREVO_API_KEY")
        if not api_key:
            raise RuntimeError("BREVO_API_KEY is not set")

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = api_key

        api_client = sib_api_v3_sdk.ApiClient(configuration)
        api_instance = sib_api_v3_sdk.EmailCampaignsApi(api_client)

        campaign = sib_api_v3_sdk.CreateEmailCampaign(
            name="Campaign sent via the API",
            subject="My subject",
            sender={"name": "AMRx Hub", "email": "verified-sender@yourdomain.com"},
            type="classic",
            html_content="Congratulations! You successfully sent this example campaign via the Brevo API.",
            recipients={"listIds": [2, 7]},
            scheduled_at="2018-01-01 00:00:01",
        )

        try:
            api_response = api_instance.create_email_campaign(campaign)
            self.stdout.write(self.style.SUCCESS(str(api_response)))
        except ApiException as exc:
            raise RuntimeError(f"Brevo campaign failed: {exc}") from exc