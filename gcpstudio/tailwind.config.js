/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // Include all your source files
  ],
  theme: {
    extend: {
      animation: {
        rainbow: 'rainbow 5s linear infinite',
      },
      keyframes: {
        rainbow: {
          '0%, 100%': { color: '#ff0000' },
          '15%': { color: '#ff9900' },
          '30%': { color: '#ffff00' },
          '45%': { color: '#33cc33' },
          '60%': { color: '#0099ff' },
          '75%': { color: '#6600cc' },
          '90%': { color: '#cc00cc' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}