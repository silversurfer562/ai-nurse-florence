module.exports = {
  plugins: [
    require('@tailwindcss/postcss')('../frontend/tailwind.config.js'),
    require('autoprefixer'),
  ],
}
