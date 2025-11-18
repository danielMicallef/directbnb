import stripe
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "List recent Stripe checkout sessions"

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not stripe.api_key:
            self.stdout.write(self.style.ERROR("STRIPE_SECRET_KEY is not set!"))
            return

        self.stdout.write("\nFetching recent checkout sessions...\n")

        try:
            # List recent checkout sessions
            sessions = stripe.checkout.Session.list(limit=10)

            if not sessions.data:
                self.stdout.write(self.style.WARNING("No checkout sessions found."))
                return

            for session in sessions.data:
                customer_email = "N/A"
                if session.customer_details:
                    customer_email = session.customer_details.get("email", "N/A")

                self.stdout.write(
                    f"\n{'=' * 60}\n"
                    f"Session ID: {session.id}\n"
                    f"Status: {session.status}\n"
                    f"Payment Status: {session.payment_status}\n"
                    f"Customer Email: {customer_email}\n"
                    f"Amount Total: {session.amount_total / 100 if session.amount_total else 0} {session.currency.upper() if session.currency else 'N/A'}\n"
                    f"Client Reference ID: {session.client_reference_id or 'N/A'}\n"
                    f"Created: {session.created}"
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error: {e}"))
