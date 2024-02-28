import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [
    vue(),
  ],
  server: {
    proxy: {
      '/socket.io': {
        target: 'ws://192.168.0.202',
        ws: true,
      },
    },
  },
})
