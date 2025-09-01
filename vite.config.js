import { defineConfig } from 'vite'; // ✅ From Vite
import react from '@vitejs/plugin-react';
import { defineConfig as definePWAConfig } from 'vite-plugin-pwa'; // ✅ Rename to avoid conflict

export default defineConfig({
  plugins: [
    react(),
    definePWAConfig({ // ✅ Use renamed function
      registerType: 'autoUpdate',
      devOptions: {
        enabled: true
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}']
      },
      manifest: {
        name: 'Soccer Predict PWA',
        short_name: 'SoccerPredict',
        description: 'AI-powered football predictions',
        theme_color: '#ffffff',
        icons: [
          {
            src: 'pwa-64x64.png',
            sizes: '64x64',
            type: 'image/png'
          },
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  server: {
    port: 3000,
    host: true
  }
});