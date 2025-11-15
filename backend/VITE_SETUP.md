# Django-Vite Setup Guide

This project now uses django-vite for frontend asset management with Vite as the build tool.

## Project Structure

```
backend/
├── package.json           # Node.js dependencies
├── vite.config.ts        # Vite configuration
├── src/
│   ├── static/
│   │   └── src/
│   │       ├── main.ts   # Main JavaScript/TypeScript entry
│   │       └── main.css  # Main CSS entry
│   └── templates/
│       └── base.html     # Base template with django-vite tags
```

## Installation

1. Install Node.js dependencies (use Bun as per project standards):
```bash
cd backend
bun install
```

## Development

### Start Vite Dev Server

For hot module replacement (HMR) during development:

```bash
cd backend
bun run dev
```

This starts the Vite dev server on `http://localhost:5173`.

### Start Django

In another terminal:

```bash
docker compose up -d
# or
docker compose exec app uv run python manage.py runserver
```

The Django app will automatically connect to the Vite dev server when `DEBUG=True`.

## Production Build

Build optimized assets for production:

```bash
cd backend
bun run build
```

This creates optimized bundles in `src/static/dist/` with a manifest file.

## Using in Templates

### Base Template

The `base.html` template includes the django-vite setup:

```django
{% load django_vite %}
<!DOCTYPE html>
<html>
<head>
    {% vite_asset 'src/static/src/main.css' %}
</head>
<body>
    {% block content %}{% endblock %}
    {% vite_asset 'src/static/src/main.ts' %}
</body>
</html>
```

### Extending Base Template

Other templates can extend the base:

```django
{% extends "base.html" %}

{% block title %}My Page{% endblock %}

{% block content %}
    <div class="container">
        <h1>Hello World</h1>
    </div>
{% endblock %}
```

## Features

- **Hot Module Replacement (HMR)**: Changes to CSS/JS are reflected instantly in development
- **TypeScript Support**: Write TypeScript with full type checking
- **Alpine.js**: Included for reactive components
- **CSS Bundling**: Automatic CSS processing and optimization
- **Asset Fingerprinting**: Automatic cache-busting in production

## Configuration

### Django Settings (src/core/settings.py:318-329)

```python
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_host": "localhost",
        "dev_server_port": 5173,
        "static_url_prefix": "dist",
    }
}
```

### Vite Config (vite.config.ts)

- Entry points: `main.ts` and `main.css`
- Output directory: `src/static/dist/`
- Dev server: `localhost:5173`
- Manifest file: `manifest.json`

## Adding New JavaScript/CSS Files

1. Create your file in `src/static/src/`:
```typescript
// src/static/src/custom.ts
console.log('Custom script');
```

2. Add it to `vite.config.ts` inputs:
```typescript
rollupOptions: {
  input: {
    main: resolve('./src/static/src/main.ts'),
    styles: resolve('./src/static/src/main.css'),
    custom: resolve('./src/static/src/custom.ts'), // Add this
  },
}
```

3. Use it in templates:
```django
{% vite_asset 'src/static/src/custom.ts' %}
```

## Troubleshooting

### Vite dev server not connecting

1. Ensure Vite is running: `bun run dev`
2. Check CORS settings in `settings.py:37-43`
3. Verify port 5173 is not blocked

### Assets not loading in production

1. Run the build: `bun run build`
2. Check that `src/static/dist/` contains built files
3. Run `collectstatic`: `python manage.py collectstatic`
4. Verify `DEBUG=False` in production

### TypeScript errors

Install type definitions:
```bash
bun add -d @types/alpinejs
```

## Resources

- [django-vite Documentation](https://github.com/MrBin99/django-vite)
- [Vite Documentation](https://vitejs.dev/)
- [Alpine.js Documentation](https://alpinejs.dev/)