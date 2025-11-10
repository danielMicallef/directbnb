# Testing Guide

This document provides information on testing the DirectBnB Django application.

## Setup

Testing dependencies are managed in `pyproject.toml` under the `dev` dependency group.

### Install Test Dependencies

Inside the Docker container:
```bash
docker compose exec app uv sync --group dev
```

Or locally with UV:
```bash
uv sync --group dev
```

## Running Tests

### Locally (Outside Docker)

Run all tests:
```bash
uv run --env-file=.env.local pytest
```

Run with coverage report:
```bash
uv run --env-file=.env.local pytest --cov=src --cov-report=html --cov-report=term
```

Run specific test file:
```bash
uv run --env-file=.env.local pytest src/apps/builder/tests/test_package_api.py
```

Run specific test class or function:
```bash
uv run --env-file=.env.local pytest src/apps/builder/tests/test_package_api.py::TestPackageListAPI
uv run --env-file=.env.local pytest src/apps/builder/tests/test_package_api.py::TestPackageListAPI::test_package_list_returns_grouped_by_label
```

### Inside Docker Container

Run all tests:
```bash
docker compose exec app uv run pytest
```

Run with coverage report:
```bash
docker compose exec app uv run pytest --cov=src --cov-report=html --cov-report=term
```

Run specific test file:
```bash
docker compose exec app uv run pytest src/apps/builder/tests/test_package_api.py
```

Run specific test class or function:
```bash
docker compose exec app uv run pytest src/apps/builder/tests/test_package_api.py::TestPackageListAPI
docker compose exec app uv run pytest src/apps/builder/tests/test_package_api.py::TestPackageListAPI::test_package_list_returns_grouped_by_label
```

### Parallel Testing

Run tests in parallel using pytest-xdist:
```bash
docker compose exec app uv run pytest -n auto
```

### Test Markers

Run only unit tests:
```bash
docker compose exec app uv run pytest -m unit
```

Run only integration tests:
```bash
docker compose exec app uv run pytest -m integration
```

Exclude slow tests:
```bash
docker compose exec app uv run pytest -m "not slow"
```

## Test Configuration

Test configuration is defined in two places:

1. **pytest.ini** - Main pytest configuration file
2. **pyproject.toml** - `[tool.pytest.ini_options]` section (alternative configuration)

### Key Settings

- **DJANGO_SETTINGS_MODULE**: `core.settings`
- **testpaths**: `src` (where tests are located)
- **--reuse-db**: Reuses test database between runs for speed
- **--nomigrations**: Skips running migrations, uses schema from models directly
- **--cov**: Generates code coverage reports

## Code Coverage

After running tests with coverage, view the HTML report:
```bash
# Coverage report is generated in htmlcov/
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

Coverage configuration is in `.coveragerc`.

## Linting and Formatting

### Ruff (with isort)

Ruff is configured in `pyproject.toml` under `[tool.ruff]` and includes isort functionality.

Check for linting issues:
```bash
docker compose exec app uv run ruff check .
```

Auto-fix linting issues:
```bash
docker compose exec app uv run ruff check --fix .
```

Format code:
```bash
docker compose exec app uv run ruff format .
```

Check import sorting (isort via ruff):
```bash
docker compose exec app uv run ruff check --select I .
```

Fix import sorting:
```bash
docker compose exec app uv run ruff check --select I --fix .
```

## Writing Tests

### Test Structure

Tests are organized within each app under a `tests/` directory:
```
src/apps/builder/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_package_api.py
│   └── test_serializers.py
```

### Fixtures

Common fixtures are defined in `src/conftest.py`:
- `api_client`: Unauthenticated DRF API client
- `authenticated_client`: Authenticated DRF API client with test user

### Example Test

```python
import pytest
from django.urls import reverse
from apps.builder.models import Package

@pytest.mark.django_db
class TestPackageAPI:
    def test_create_package(self, api_client):
        url = reverse("builder_api:package-list")
        data = {
            "name": "Test Package",
            "amount": "100.00",
            "frequency": 1,
        }
        response = api_client.post(url, data)
        assert response.status_code == 201
```

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

## Best Practices

1. **Use factories**: Consider using `factory-boy` for complex model creation
2. **Isolate tests**: Each test should be independent
3. **Use fixtures**: Share common setup via pytest fixtures
4. **Mark tests**: Use markers to categorize tests (unit, integration, slow)
5. **Test edge cases**: Don't just test the happy path
6. **Keep tests fast**: Use `--nomigrations` and `--reuse-db`
7. **Aim for coverage**: Target 80%+ code coverage

## CI/CD Integration

To integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    docker compose exec -T app uv run pytest --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Troubleshooting

### Database Issues

If you encounter database-related errors:
```bash
# Recreate test database
docker compose exec app uv run pytest --create-db

# Or drop and recreate
docker compose exec db psql -U postgresuser -c "DROP DATABASE IF EXISTS test_directbnb;"
```

### Import Errors

Ensure you're running tests from the correct directory and PYTHONPATH is set:
```bash
cd /Users/danielmicallef/pdev/directbnb/backend
docker compose exec app uv run pytest
```

### Migration Issues

If migrations are causing issues, you can skip them:
```bash
docker compose exec app uv run pytest --nomigrations
```
