# Quick Start - Testing

## Prerequisites

Ensure test dependencies are installed:
```bash
uv sync --group dev
```

## Running Tests Locally

The key issue with running tests locally is that pytest needs to find the Django project in the `src/` directory. This is now configured in `pytest.ini` with `pythonpath = src`.

### Basic Commands

```bash
# Run all tests
uv run --env-file=.env.local pytest

# Run with verbose output
uv run --env-file=.env.local pytest -v

# Run specific app tests
uv run --env-file=.env.local pytest src/apps/builder/tests/

# Run specific test file
uv run --env-file=.env.local pytest src/apps/builder/tests/test_stripe_webhook.py

# Run specific test
uv run --env-file=.env.local pytest src/apps/builder/tests/test_stripe_webhook.py::TestStripeWebhookView::test_webhook_with_valid_signature_payment_intent_created
```

### Coverage Reports

```bash
# Run with coverage
uv run --env-file=.env.local pytest --cov=src

# Generate HTML coverage report
uv run --env-file=.env.local pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Parallel Execution

```bash
# Run tests in parallel (faster)
uv run --env-file=.env.local pytest -n auto
```

### Common Options

```bash
# Stop on first failure
uv run --env-file=.env.local pytest -x

# Show print statements
uv run --env-file=.env.local pytest -s

# Show local variables on failure
uv run --env-file=.env.local pytest -l

# Run only tests matching a keyword
uv run --env-file=.env.local pytest -k "webhook"

# Run tests with specific marker
uv run --env-file=.env.local pytest -m unit
uv run --env-file=.env.local pytest -m integration
uv run --env-file=.env.local pytest -m "not slow"
```

## Running Tests in Docker

```bash
# Run all tests
docker compose exec app uv run pytest

# Run specific test file
docker compose exec app uv run pytest src/apps/builder/tests/test_stripe_webhook.py

# Run with coverage
docker compose exec app uv run pytest --cov=src --cov-report=html
```

## Troubleshooting

### "No module named 'core'" Error

**Solution:** The `pythonpath = src` configuration in `pytest.ini` should fix this. Make sure you're running pytest from the `backend/` directory.

### Database Connection Issues

**Solution:** Make sure your `.env.local` file has the correct database credentials, or run tests in Docker where the database is already configured.

```bash
# Create test database manually if needed
docker compose exec db psql -U postgresuser -c "CREATE DATABASE test_directbnb;"
```

### Import Errors

**Solution:** Ensure you're in the correct directory:
```bash
cd /Users/danielmicallef/pdev/directbnb/backend
uv run --env-file=.env.local pytest
```

## Configuration Files

- **pytest.ini** - Main pytest configuration (preferred)
- **pyproject.toml** - Alternative configuration (has a warning)
- **.coveragerc** - Coverage reporting configuration
- **src/conftest.py** - Global test fixtures

## Key Configuration

From `pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings
pythonpath = src          # Critical: adds src to Python path
testpaths = src           # Where to look for tests
```

## Test Structure

```
backend/
├── pytest.ini            # Pytest configuration
├── .coveragerc          # Coverage configuration
└── src/
    ├── conftest.py      # Global fixtures
    └── apps/
        └── builder/
            └── tests/
                ├── __init__.py
                ├── test_package_api.py
                ├── test_stripe_webhook.py
                ├── test_utils.py
                └── README.md
```

## Quick Test of Stripe Webhook

```bash
# Test the Stripe webhook endpoint
uv run --env-file=.env.local pytest src/apps/builder/tests/test_stripe_webhook.py -v

# Test specific webhook scenario
uv run --env-file=.env.local pytest src/apps/builder/tests/test_stripe_webhook.py::TestStripeWebhookView::test_webhook_with_valid_signature_checkout_completed -v
```

## See Full Documentation

For more details, see:
- **TESTING.md** - Comprehensive testing guide
- **src/apps/builder/tests/README.md** - Builder app tests documentation
