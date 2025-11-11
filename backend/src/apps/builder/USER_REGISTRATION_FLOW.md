# User Registration Flow After Payment

This document describes the automated user registration and email verification flow that occurs after a successful Stripe payment.

## Overview

When a customer completes payment through Stripe for a direct booking website package, the following automated process occurs:

1. Stripe sends a webhook to our system
2. Payment is recorded for the lead registration
3. A user account is automatically created
4. A confirmation email is sent with:
   - Payment summary
   - Email verification link
   - Account details
   - Next steps information

## Workflow Diagram

```
Stripe Payment Completed
         ↓
Webhook Received (checkout.session.completed)
         ↓
Update RegistrationOptions.paid_at
         ↓
Create BNBUser from LeadRegistration
         ↓
Generate Email Verification Token (24h expiry)
         ↓
Send Payment Confirmation Email
         ↓
User Clicks Verification Link
         ↓
Email Confirmed → Account Fully Activated
```

## Components

### 1. Stripe Webhook Handler

**File:** `src/apps/builder/api_views.py`
**Method:** `StripeWebhookView.handle_checkout_session_completed()`

This method:
- Receives the `checkout.session.completed` event from Stripe
- Updates registration options with `paid_at` timestamp
- Calls `LeadRegistration.create_user_from_lead()` to create the user
- Calls `LeadRegistration.send_payment_confirmation_email()` to send the email
- Logs all actions for debugging
- Handles errors gracefully (email failures don't fail the webhook)

### 2. User Creation

**File:** `src/apps/builder/models.py`
**Method:** `LeadRegistration.create_user_from_lead()`

This method:
- Checks if a user with the email already exists
- Creates a new `BNBUser` if needed with:
  - Email from `LeadRegistration.email`
  - Name from `LeadRegistration.first_name` and `last_name`
  - Phone from `LeadRegistration.phone_number`
  - Random secure password (32 characters)
  - `is_email_confirmed=False` (requires verification)
  - `is_active=True` (account is active but email not verified)
- Links the user to the lead registration via `LeadRegistration.user`
- Returns `(user, created)` tuple

**Important:** If the user already exists, it's not recreated, but the lead registration is linked to the existing user.

### 3. Email Sending

**File:** `src/apps/builder/models.py`
**Method:** `LeadRegistration.send_payment_confirmation_email()`

This method:
- Gets or creates the user
- Generates a new email verification token (or refreshes if user exists)
- Collects payment details from `get_latest_registration_options()`
- Calculates discounted amounts for each package
- Renders the HTML email template
- Sends the email using Django's email system

**Template:** `src/templates/builder/emails/payment_confirmation.html`

### 4. Email Template

**File:** `src/templates/builder/emails/payment_confirmation.html`

Features:
- Professional, responsive HTML design
- Prominent "Verify Email" call-to-action button
- Complete payment summary with:
  - Package names and descriptions
  - Original and discounted prices
  - Discount percentages
  - Payment frequency (one-time, monthly, yearly, etc.)
  - Total amount paid
- Account details (email, name, phone)
- Clear "What Happens Next" section
- Warning about 24-hour token expiration

### 5. Email Verification

**Files:**
- `src/apps/users/models.py` - `UserToken` model and `BNBUser.create_user_token()`
- User clicks link in email → `users:verify_email` URL
- Token is validated (not expired, belongs to user)
- `BNBUser.is_email_confirmed` is set to `True`
- User can now fully access their account

## Configuration

### Email Settings

Configured in `src/core/settings.py`:

```python
# Development (uses console backend)
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST", "mailcatcher")
    DEFAULT_FROM_EMAIL = "noreply@directbnb.local"
```

### Stripe Webhook Secret

```python
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
```

### Site Settings

```python
SITE_URL = os.getenv("SITE_URL", default="http://localhost:8000")
SITE_NAME = os.getenv("SITE_NAME", default="DIRECTBNB")
```

## Testing

### Manual Testing

1. Create a test lead registration:
```python
lead = LeadRegistration.objects.create(
    email="test@example.com",
    first_name="John",
    last_name="Doe",
    phone_number="+1234567890"
)
```

2. Create test packages and registration options:
```python
package = Package.objects.create(
    name="Builder Package",
    amount=Decimal("650.00"),
    frequency=Frequency.ONE_TIME,
    label=Package.LabelChoices.BUILDER
)

option = RegistrationOptions.objects.create(
    lead_registration=lead,
    package=package
)
```

3. Simulate Stripe webhook or test directly:
```python
# Create user and send email
user, created = lead.create_user_from_lead()
lead.send_payment_confirmation_email()

# Check email was sent (in console during development)
```

### Automated Testing

Tests are located in `src/apps/builder/tests/test_stripe_webhook.py`

Key test cases:
- `test_webhook_with_valid_signature_checkout_completed` - Verifies payment recording
- Should add: Test for user creation
- Should add: Test for email sending

## Error Handling

### User Creation Errors

- If user creation fails, the webhook handler logs the error and returns `False`
- The webhook payload is still stored with `processed_successfully=False`
- Can be retried manually or via admin interface

### Email Sending Errors

- If email sending fails, the error is logged but webhook still returns success
- Payment has been recorded and user has been created
- Email can be resent manually via admin or custom management command

**Recommendation:** Implement Celery task for retry logic:
```python
@app.task(bind=True, max_retries=3)
def send_payment_confirmation_email_task(self, lead_registration_id):
    try:
        lead = LeadRegistration.objects.get(id=lead_registration_id)
        lead.send_payment_confirmation_email()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

## Security Considerations

### Password Generation

- Users are created with a random 32-character password
- Password is generated using `make_random_password(length=32)`
- Users must reset password through "Forgot Password" flow

### Email Verification Token

- Tokens are UUIDs stored in `UserToken` model
- Tokens expire after 24 hours (`UserToken.MAX_HOURS_VALID = 24`)
- One token per user (old tokens deleted when new one created)
- Tokens are validated in the email verification view

### Webhook Security

- Stripe webhook signatures are verified using `stripe.Webhook.construct_event()`
- Invalid signatures return 400 Bad Request
- Webhook secret is stored securely in environment variables

## Monitoring

### Logs to Monitor

```python
# Success logs
logger.info(f"Lead registration {lead_registration_id} payment recorded")
logger.info(f"Created new user {user.email} from lead registration {lead_registration_id}")
logger.info(f"Payment confirmation email sent to {user.email}")

# Error logs
logger.error(f"Lead registration {lead_registration_id} not found")
logger.error(f"Failed to send payment confirmation email to {user.email}: {email_error}")
logger.error(f"Error handling checkout session completed: {e}")
```

### Key Metrics

- User creation success rate
- Email delivery success rate
- Email verification completion rate (within 24 hours)
- Time from payment to email verification

### Admin Interface

You can view and manage:
- **LeadRegistration** - View payment status, linked user
- **BNBUser** - View email confirmation status
- **UserToken** - View active verification tokens
- **StripeWebhookPayload** - View webhook processing status

## Future Enhancements

1. **Password Reset Email** - Send password reset link in welcome email
2. **Celery Integration** - Queue email sending for retry logic
3. **Email Templates** - Add plain text versions of emails
4. **Notification System** - Notify admin of new paid registrations
5. **Dashboard Access** - Link to user dashboard in email
6. **Progress Tracking** - Show website setup progress to user
7. **Multi-language Support** - Translate emails based on user locale
8. **Email Preferences** - Allow users to opt-in/out of certain emails

## Troubleshooting

### User didn't receive email

1. Check email backend configuration in settings
2. Check Django logs for email errors
3. Verify SMTP settings (if using SMTP backend)
4. Check spam folder
5. Resend email manually via admin or API

### Email verification link expired

1. Generate new token:
```python
user = BNBUser.objects.get(email="user@example.com")
new_token = user.refresh_user_token()
# Send new verification email
```

2. Or user can request new verification email via UI

### Webhook processed but user not created

1. Check `StripeWebhookPayload` table for processing errors
2. Check logs for exception details
3. Manually trigger user creation:
```python
lead = LeadRegistration.objects.get(email="user@example.com")
user, created = lead.create_user_from_lead()
```

### Multiple users with same email

This should not happen due to:
- `email` field has `unique=True` on `BNBUser` model
- `get_or_create()` prevents duplicates
- If it occurs, it's a data integrity issue that needs investigation
