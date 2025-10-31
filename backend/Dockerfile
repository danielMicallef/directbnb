FROM python:3.13-bookworm as base

RUN apt-get update && \
    apt-get install -y build-essential pkg-config gdal-bin libgdal-dev \
    libgeos-dev proj-bin libproj-dev

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UV_SYSTEM_PYTHON 1
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV PATH="/app/.venv/bin/python:$PATH"
ENV PYTHONPATH="/app/src"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ARG DEBUG=False

COPY pyproject.toml uv.lock* gunicorn-cfg.py ./

RUN if [ "$DEBUG" = "False" ]; then \
    uv sync --frozen --no-dev; \
    else \
    uv sync; \
    fi

COPY src ./src

RUN uv run django-admin collectstatic --no-input --clear || true

EXPOSE 8000

FROM base as development
CMD ["uv", "run", "django-admin", "runserver", "0.0.0.0:8000"]

FROM base as production
CMD ["uv", "run", "gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi:application"]