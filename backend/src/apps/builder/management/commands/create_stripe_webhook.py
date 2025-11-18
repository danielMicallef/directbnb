import stripe
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Checks if Stripe Webhook exists, and if it does not, creates Stripe Webhook"

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not stripe.api_key:
            self.stdout.write(
                self.style.ERROR(
                    "STRIPE_SECRET_KEY is not set. Please configure it in your environment variables."
                )
            )
            return

        # Define the webhook URL and events
        webhook_url = f"{settings.SITE_URL}/api/builder/stripe-webhook/"
        webhook_events = ["checkout.session.completed"]

        self.stdout.write(f"Checking for existing webhooks at: {webhook_url}")

        # List all existing webhooks
        try:
            webhooks = stripe.WebhookEndpoint.list(limit=100)
            self.stdout.write(
                self.style.SUCCESS(f"Found {len(webhooks.data)} existing webhook(s)")
            )

            # Check if webhook already exists
            webhook_exists = False
            for webhook in webhooks.data:
                self.stdout.write(
                    f"\n  - URL: {webhook.url}\n"
                    f"    ID: {webhook.id}\n"
                    f"    Status: {webhook.status}\n"
                    f"    Events: {', '.join(webhook.enabled_events)}\n"
                    f"    API Version: {webhook.api_version or 'default'}\n"
                    f"    Description: {webhook.description or 'N/A'}"
                )

                if (
                    webhook.url == webhook_url
                    and "checkout.session.completed" in webhook.enabled_events
                ):
                    webhook_exists = True
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"\n✓ Webhook already exists with ID: {webhook.id}"
                        )
                    )

            # Create webhook if it doesn't exist
            if not webhook_exists:
                self.stdout.write(
                    self.style.WARNING(
                        f"\nWebhook not found. Creating new webhook for {webhook_url}..."
                    )
                )

                new_webhook = stripe.WebhookEndpoint.create(
                    url=webhook_url,
                    enabled_events=webhook_events,
                    description="DirectBnB checkout session completion webhook",
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Successfully created webhook!\n"
                        f"  - ID: {new_webhook.id}\n"
                        f"  - URL: {new_webhook.url}\n"
                        f"  - Events: {', '.join(new_webhook.enabled_events)}\n"
                        f"  - Secret: {new_webhook.secret}"
                    )
                )

                self.stdout.write(
                    self.style.WARNING(
                        f"\nIMPORTANT: Save the webhook secret to your environment variables:\n"
                        f"STRIPE_WEBHOOK_SECRET={new_webhook.secret}"
                    )
                )

        except stripe.error.StripeError as e:
            self.stdout.write(self.style.ERROR(f"Stripe API error: {str(e)}"))
