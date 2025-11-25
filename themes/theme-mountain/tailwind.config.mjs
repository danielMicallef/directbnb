/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        mountain: {
          "primary": "#3b82f6",
          "primary-content": "#ffffff",
          "secondary": "#10b981",
          "secondary-content": "#ffffff",
          "accent": "#f59e0b",
          "accent-content": "#ffffff",
          "neutral": "#1f2937",
          "neutral-content": "#f9fafb",
          "base-100": "#ffffff",
          "base-200": "#f3f4f6",
          "base-300": "#e5e7eb",
          "base-content": "#1f2937",
          "info": "#3b82f6",
          "success": "#10b981",
          "warning": "#f59e0b",
          "error": "#ef4444",
        },
        seaside: {
          "primary": "#06b6d4",        // Cyan/Ocean blue
          "primary-content": "#ffffff",
          "secondary": "#f59e0b",      // Coral/Sandy
          "secondary-content": "#ffffff",
          "accent": "#ec4899",         // Pink sunset
          "accent-content": "#ffffff",
          "neutral": "#0e7490",        // Deep ocean
          "neutral-content": "#ffffff",
          "base-100": "#f0fdfa",       // Light aqua
          "base-200": "#ccfbf1",       // Lighter teal
          "base-300": "#99f6e4",       // Pale turquoise
          "base-content": "#164e63",   // Deep teal text
          "info": "#0ea5e9",
          "success": "#14b8a6",
          "warning": "#f59e0b",
          "error": "#ef4444",
        },
        city: {
          "primary": "#6366f1",
          "primary-content": "#ffffff",
          "secondary": "#eab308",
          "secondary-content": "#ffffff",
          "accent": "#ef4444",
          "accent-content": "#ffffff",
          "neutral": "#374151",
          "neutral-content": "#f9fafb",
          "base-100": "#ffffff",
          "base-200": "#f9fafb",
          "base-300": "#e5e7eb",
          "base-content": "#1f2937",
          "info": "#3b82f6",
          "success": "#10b981",
          "warning": "#f59e0b",
          "error": "#dc2626",
        },
        neobrutalism: {
          "primary": "#ff006e",
          "primary-content": "#000000",
          "secondary": "#ffbe0b",
          "secondary-content": "#000000",
          "accent": "#00f5ff",
          "accent-content": "#000000",
          "neutral": "#000000",
          "neutral-content": "#ffffff",
          "base-100": "#ffffff",
          "base-200": "#f8f8f8",
          "base-300": "#e0e0e0",
          "base-content": "#000000",
          "info": "#00f5ff",
          "success": "#06ffa5",
          "warning": "#ffbe0b",
          "error": "#ff006e",
        },
      },
      "dark",
      "cupcake",
      "bumblebee",
      "retro",
      "nord",
      "winter",
      "acid",
      "lofi",
      "pastel",
      "fantasy",
      "synthwave",
    ],
  },
};
