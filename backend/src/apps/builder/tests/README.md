# Builder App Tests

This directory contains tests for the builder app, including models, serializers, API views, and Stripe webhook integration.

## Test Files

- **test_package_api.py** - Tests for the Package listing API
- **test_stripe_webhook.py** - Tests for Stripe webhook handling
- **test_utils.py** - Utility functions for testing (e.g., Stripe signature generation)

## Running Tests

### Run all builder tests
```bash
docker compose exec app uv run pytest src/apps/builder/tests/
```

### Run specific test file
```bash
docker compose exec app uv run pytest src/apps/builder/tests/test_stripe_webhook.py
```

### Run specific test class
```bash
docker compose exec app uv run pytest src/apps/builder/tests/test_stripe_webhook.py::TestStripeWebhookView
```

### Run specific test function
```bash
docker compose exec app uv run pytest src/apps/builder/tests/test_stripe_webhook.py::TestStripeWebhookView::test_webhook_with_valid_signature_payment_intent_created
```

### Run with verbose output
```bash
docker compose exec app uv run pytest src/apps/builder/tests/ -v
```

### Run with coverage
```bash
docker compose exec app uv run pytest src/apps/builder/tests/ --cov=apps.builder --cov-report=term-missing
```

## Stripe Webhook Tests

The Stripe webhook tests (`test_stripe_webhook.py`) verify the webhook endpoint's behavior with various scenarios:

### Test Coverage

1. **Valid Signature Tests**
   - `test_webhook_with_valid_signature_payment_intent_created` - Tests payment_intent.created event
   - `test_webhook_with_valid_signature_checkout_completed` - Tests checkout.session.completed event

2. **Security Tests**
   - `test_webhook_without_signature_header` - Verifies 401 response without signature
   - `test_webhook_with_invalid_signature` - Tests behavior with invalid signature

3. **Error Handling Tests**
   - `test_webhook_with_invalid_json_payload` - Tests invalid JSON handling
   - `test_webhook_handles_nonexistent_lead_registration` - Tests missing lead registration

4. **Business Logic Tests**
   - `test_webhook_creates_webhook_payload_record` - Verifies webhook storage
   - `test_webhook_payload_stores_lead_registration_reference` - Verifies lead reference storage
   - `test_webhook_with_multiple_registration_options` - Tests updating multiple options

5. **Integration Tests**
   - `test_webhook_stripe_construct_event_called` - Verifies Stripe library integration

### Stripe Webhook Secret

The webhook secret is configured in `core/settings.py`:
```python
STRIPE_WEBHOOK_SECRET = os.getenv(
    "STRIPE_WEBHOOK_SECRET",
    "whsec_e136fcf022bbf4fe4d31d2ca7f62c3b9d3bb824beb1368d6c592eb38b137cc06"
)
```

For testing, the default value is used. In production, set the `STRIPE_WEBHOOK_SECRET` environment variable to your actual webhook secret from the Stripe dashboard.

### Stripe Signature Generation

The `test_utils.py` module provides a `generate_stripe_signature()` function that creates valid Stripe webhook signatures for testing:

```python
from apps.builder.tests.test_utils import generate_stripe_signature

payload = json.dumps(webhook_data).encode('utf-8')
signature = generate_stripe_signature(payload, STRIPE_WEBHOOK_SECRET)
```

This allows tests to simulate real Stripe webhook requests with valid signatures.

## Test Fixtures

Common fixtures are defined in:
- `src/conftest.py` - Global fixtures (api_client, authenticated_client, etc.)
- Test files - Local fixtures specific to test modules

### Key Fixtures in test_stripe_webhook.py

- `stripe_webhook_secret` - Mocks the Stripe webhook secret
- `lead_registration` - Creates a test lead registration
- `package_with_promotion` - Creates a test package with active promotion
- `registration_option` - Creates a registration option
- `payment_intent_created_payload` - Sample payment_intent.created webhook payload
- `checkout_session_completed_payload` - Sample checkout.session.completed webhook payload

## Debugging Tests

### View test output with print statements
```bash
docker compose exec app uv run pytest src/apps/builder/tests/ -s
```

### Run with Python debugger
```bash
docker compose exec app uv run pytest src/apps/builder/tests/ --pdb
```

### Show local variables on failure
```bash
docker compose exec app uv run pytest src/apps/builder/tests/ -l
```

## Writing New Tests

When writing new tests for the builder app:

1. Follow the existing test structure and naming conventions
2. Use descriptive test names that explain what is being tested
3. Organize tests into classes by feature or endpoint
4. Use fixtures to avoid code duplication
5. Mark tests appropriately (`@pytest.mark.django_db`, `@pytest.mark.slow`, etc.)
6. Test both success and failure scenarios
7. Verify side effects (database changes, external API calls, etc.)

### Example Test Structure

```python
import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestMyFeature:
    """Test my feature"""

    @pytest.fixture
    def setup_data(self, db):
        """Create test data"""
        # Setup code here
        return test_data

    def test_success_case(self, api_client, setup_data):
        """Test successful operation"""
        url = reverse("builder_api:my-endpoint")
        response = api_client.get(url)

        assert response.status_code == 200
        # Additional assertions

    def test_error_case(self, api_client):
        """Test error handling"""
        url = reverse("builder_api:my-endpoint")
        response = api_client.get(url + "/invalid")

        assert response.status_code == 404
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Ensure your pipeline:

1. Sets up the PostgreSQL/PostGIS database
2. Installs test dependencies (`uv sync --group dev`)
3. Runs migrations or uses `--nomigrations` flag
4. Collects coverage reports
5. Fails the build on test failures

Example CI configuration:
```yaml
- name: Run builder tests
  run: docker compose exec -T app uv run pytest src/apps/builder/tests/ --cov=apps.builder
```
