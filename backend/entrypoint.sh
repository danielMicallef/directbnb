#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run the management command to create a superuser if none exists.
uv run django-admin createsuperuser_if_none_exists

# Execute the command passed as arguments to this script.
exec "$@"
