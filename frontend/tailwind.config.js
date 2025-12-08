/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        mint: {
          50: '#ecfff6',
          100: '#d3ffe9',
          200: '#a4f8cb',
          300: '#6ef0b2',
          500: '#22d17f',
          600: '#16b26a',
        },
        lagoon: {
          50: '#e8f6ff',
          100: '#d9f0ff',
          200: '#a6dcff',
          300: '#84caff',
          500: '#1f9ae0',
        },
        ink: '#0f172a',
        sand: '#f5f1e8',
        cloud: '#f8fbff',
      },
      fontFamily: {
        display: ['var(--font-display)', 'Space Grotesk', 'Inter', 'system-ui', 'sans-serif'],
        sans: ['var(--font-body)', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        lift: '0 18px 50px rgba(15, 23, 42, 0.08)',
      },
      backgroundImage: {
        'soft-radial':
          'radial-gradient(circle at 20% 20%, rgba(34, 209, 127, 0.18), transparent 45%), radial-gradient(circle at 80% 0%, rgba(31, 154, 224, 0.16), transparent 30%)',
      },
    },
  },
  plugins: [],
}

