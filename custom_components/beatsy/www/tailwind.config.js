/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./admin.html",
    "./player.html",
    "./js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        'beatsy-purple': '#7c3aed',
        'beatsy-indigo': '#4f46e5',
        'beatsy-green': '#16a34a',
      },
    },
  },
  plugins: [],
}
