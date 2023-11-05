import daisyui from 'daisyui'
import typography from '@tailwindcss/typography'

export default {
  content: [
    './src/components/*.vue',
    './src/App.vue',
    './src/style.css',
  ],
  daisyui: {
    themes: [
      'light',
    ],
  },
  plugins: [
    daisyui,
    typography,
  ],
}
