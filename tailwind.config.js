/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: '#1d4ed8',
        success: '#16a34a',
        warning: '#ca8a04',
        danger: '#dc2626',
      },
    },
  },
  plugins: [],
}