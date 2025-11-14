import stripe
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check Stripe configuration and API key"

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not stripe.api_key:
            self.stdout.write(
                self.style.ERROR(
                    "STRIPE_SECRET_KEY is not set in environment variables!"
                )
            )
            return

        # Mask the key for security (show first 12 and last 4 characters)
        masked_key = (
            f"{stripe.api_key[:12]}...{stripe.api_key[-4:]}"
            if len(stripe.api_key) > 16
            else "KEY_TOO_SHORT"
        )

        self.stdout.write(f"\nStripe API Key (masked): {masked_key}")
        self.stdout.write(f"Key type: {'TEST' if stripe.api_key.startswith('sk_test_') else 'LIVE'}")

        # Try to fetch account info to verify the key works
        try:
            account = stripe.Account.retrieve()
            account_email = account.get("email", "N/A")
            account_country = account.get("country", "N/A")
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ API Key is valid!\n"
                    f"  Account ID: {account.id}\n"
                    f"  Account Email: {account_email}\n"
                    f"  Country: {account_country}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error: {e}"))
            return

        # Check webhook secret
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        if webhook_secret:
            masked_webhook_secret = (
                f"{webhook_secret[:12]}...{webhook_secret[-4:]}"
                if len(webhook_secret) > 16
                else "SECRET_TOO_SHORT"
            )
            self.stdout.write(
                f"\nWebhook Secret (masked): {masked_webhook_secret}"
            )
        else:
            self.stdout.write(
                self.style.WARNING("\n⚠ STRIPE_WEBHOOK_SECRET is not set!")
            )
