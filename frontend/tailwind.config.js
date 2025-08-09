/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'agent': {
          'primary': '#f9d5e5',
          'secondary': '#e891b0',
        },
        'cluster': {
          'primary': '#fcf3cf',
          'secondary': '#f7dc6f',
        },
        'backend': {
          'primary': '#e5f5e0',
          'secondary': '#a9dfbf',
        },
        'frontend': {
          'primary': '#d3e5ef',
          'secondary': '#85c1e9',
        }
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
      }
    },
  },
  plugins: [],
} 