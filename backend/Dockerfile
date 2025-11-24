FROM python:3.13-bookworm as base

RUN apt-get update && \
    apt-get install -y build-essential pkg-config gdal-bin libgdal-dev \
    libgeos-dev proj-bin libproj-dev curl unzip

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UV_SYSTEM_PYTHON 1
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ARG DEBUG=False

# Copy Python dependencies first
COPY pyproject.toml uv.lock* gunicorn-cfg.py ./

RUN if [ "$DEBUG" = "False" ]; then \
    uv sync --frozen --no-dev; \
    else \
    uv sync; \
    fi

# Copy and build frontend assets
COPY package.json bun.lockb* ./
COPY vite.config.ts tsconfig.json tailwind.config.js postcss.config.js ./

RUN bun install

# Copy source files needed for Vite build
COPY src/static ./src/static

# Build Vite assets for production
RUN bun run build

# Copy remaining source files
COPY src ./src
COPY entrypoint.sh ./

# Collect static files including Vite build output
RUN uv run django-admin collectstatic --no-input --clear || true

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

FROM base as development
CMD ["uv", "run", "django-admin", "runserver", "0.0.0.0:8000"]

FROM base as production
CMD ["uv", "run", "gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi:application"]
