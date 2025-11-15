# DaisyUI + Tailwind CSS v4 - Framer Theme Setup

## Overview

DirectBnB now uses **Tailwind CSS v4** with **DaisyUI 5** and a custom Framer-inspired theme featuring rich colors, high contrast, and excellent visual hierarchy with the Inter font family.

## Setup Complete ✓

### Configuration Files

1. **tailwind.config.js** - Tailwind v4 with custom Framer theme
2. **postcss.config.js** - PostCSS configuration for Tailwind
3. **src/static/src/main.css** - Clean CSS with Tailwind imports and Inter font
4. **vite.config.ts** - Vite configuration with CSS processing

### Templates

All templates now extend from base templates and use DaisyUI classes:

- **base.html** - Base template for all pages
- **logged_in_base.html** - Template with sidebar navigation and topbar for authenticated users

#### Updated Templates:
- ✓ Registration templates (login, register, password reset flow)
- ✓ Home page (extends logged_in_base.html)
- ✓ All password reset pages
- ✓ Logout page

## Theme Colors

### Framer Dark Theme (default)

```javascript
{
  primary: '#6366F1',      // Rich indigo
  secondary: '#06B6D4',    // Vibrant cyan
  accent: '#A855F7',       // Electric purple
  neutral: '#242424',      // Dark neutral
  'base-100': '#0A0A0A',   // Deep black
  'base-200': '#131313',   // Dark surface
  'base-300': '#1A1A1A',   // Elevated surface
  success: '#10B981',      // Green
  warning: '#F59E0B',      // Amber
  error: '#EF4444',        // Red
  info: '#3B82F6',         // Blue
}
```

### Light Theme (available)

Switch by changing `data-theme="light"` on the `<html>` tag.

## Typography

- **Font**: Inter (variable font from rsms.me)
- **Features**: Advanced OpenType features enabled (cv02, cv03, cv04, cv11)
- **Rendering**: Optimized with -webkit-font-smoothing and -moz-osx-font-smoothing

## Key DaisyUI Components Used

### Navigation
- `drawer` - Sidebar navigation
- `navbar` - Top navigation bar
- `menu` - Sidebar menu items

### Cards & Content
- `card` - Content cards with shadow
- `card-body` - Card content wrapper
- `card-title` - Card headings

### Forms
- `form-control` - Form field wrapper
- `label` - Form labels
- `input` - Text inputs with variants (input-bordered, input-error)
- `btn` - Buttons with variants (btn-primary, btn-outline, btn-ghost)

### Feedback
- `alert` - Alert messages (alert-success, alert-error, alert-warning)
- `badge` - Small labels and status indicators
- `divider` - Section dividers

### Layout
- `hero` - Hero sections
- `dropdown` - Dropdown menus
- `avatar` - User avatars

## Usage Examples

### Creating a Page

**For authenticated pages:**
```django
{% extends "logged_in_base.html" %}

{% block title %}My Page - DirectBnB{% endblock %}

{% block page_content %}
<div class="hero min-h-[60vh] bg-base-200">
    <div class="hero-content text-center">
        <div class="max-w-2xl">
            <h1 class="text-5xl font-bold mb-6">Page Title</h1>
            <p class="text-lg opacity-80 mb-8">Page description</p>
            <button class="btn btn-primary btn-lg">Call to Action</button>
        </div>
    </div>
</div>
{% endblock %}
```

**For public pages (auth pages):**
```django
{% extends "base.html" %}

{% block title %}My Page - DirectBnB{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="card w-full max-w-md shadow-2xl bg-base-100">
        <div class="card-body">
            <h2 class="card-title">Card Title</h2>
            <!-- Content here -->
        </div>
    </div>
</div>
{% endblock %}
```

### Form Fields

```html
<div class="form-control">
    <label class="label">
        <span class="label-text">Field Label</span>
    </label>
    <input type="text" class="input input-bordered" placeholder="Enter text" />
    <label class="label">
        <span class="label-text-alt text-error">Error message</span>
    </label>
</div>
```

### Buttons

```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-accent">Accent</button>
<button class="btn btn-outline">Outline</button>
<button class="btn btn-ghost">Ghost</button>
```

### Cards

```html
<div class="card bg-base-200 shadow-xl">
    <div class="card-body">
        <h3 class="card-title">Card Title</h3>
        <p>Card content goes here</p>
        <div class="card-actions justify-end">
            <button class="btn btn-primary">Action</button>
        </div>
    </div>
</div>
```

### Alerts

```html
<div class="alert alert-success">
    <span>Success message</span>
</div>

<div class="alert alert-error">
    <span>Error message</span>
</div>
```

## Development Workflow

### Run Dev Server

```bash
cd backend
bun run dev
```

This starts Vite dev server with HMR on `http://localhost:5173`

### Build for Production

```bash
cd backend
bun run build
```

Outputs optimized assets to `src/static/dist/`

### Collect Static Files (Django)

```bash
docker compose exec app uv run python manage.py collectstatic
```

## Customization

### Change Theme

Edit `tailwind.config.js` to modify colors:

```javascript
daisyui: {
  themes: [
    {
      framer: {
        'primary': '#YOUR_COLOR',
        // ... other colors
      }
    }
  ]
}
```

### Add Custom Utilities

Add to `main.css`:

```css
@import "tailwindcss";

/* Your custom utilities */
.my-custom-class {
  /* ... */
}
```

### Switch to Light Theme

Change in `base.html`:
```html
<html lang="en" data-theme="light">
```

## Resources

- [DaisyUI Documentation](https://daisyui.com/)
- [Tailwind CSS v4 Documentation](https://tailwindcss.com/)
- [Inter Font](https://rsms.me/inter/)
- [Heroicons](https://heroicons.com/) (for SVG icons)

## File Structure

```
backend/
├── tailwind.config.js         # Tailwind + DaisyUI configuration
├── postcss.config.js           # PostCSS configuration
├── vite.config.ts              # Vite configuration
├── package.json                # Node dependencies
├── src/
│   ├── static/
│   │   ├── src/
│   │   │   ├── main.css       # Main stylesheet
│   │   │   └── main.ts        # Main JavaScript
│   │   └── dist/              # Built assets (generated)
│   └── templates/
│       ├── base.html           # Base template
│       ├── logged_in_base.html # Authenticated user template
│       ├── registration/       # Auth templates
│       └── users/              # User-specific templates
```

## Notes

- All inline styles have been removed in favor of DaisyUI utility classes
- The theme follows Framer's design principles: clean, modern, high contrast
- Inter font is loaded with variable font support for better rendering
- Dark theme is the default but light theme is available
- All form inputs automatically get proper styling from DaisyUI
- The sidebar drawer is responsive and works on mobile
