import hashlib
import hmac
import time
from typing import Optional


def generate_stripe_signature(
    payload: bytes, secret: str, timestamp: Optional[int] = None
) -> str:
    """
    Generate a Stripe webhook signature for testing.

    Args:
        payload: The raw webhook payload as bytes
        secret: The Stripe webhook secret
        timestamp: Optional timestamp (defaults to current time)

    Returns:
        The Stripe-Signature header value
    """
    if timestamp is None:
        timestamp = int(time.time())

    # Construct the signed payload
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"

    # Compute the signature
    signature = hmac.new(
        secret.encode("utf-8"), signed_payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # Return the signature header format
    return f"t={timestamp},v1={signature}"
