FROM python:3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UV_SYSTEM_PYTHON 1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ARG DEBUG=False

COPY pyproject.toml uv.lock* ./

RUN if [ "$DEBUG" = "False" ]; then \
    uv sync --frozen --no-dev; \
    else \
    uv sync; \
    fi

COPY . .

RUN uv run django-admin collectstatic --no-input --clear || true

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi:application"]