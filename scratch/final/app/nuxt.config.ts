export default defineNuxtConfig({
  compatibilityDate: '2025-05-01',
  devtools: { enabled: false },
  ssr: true,

  modules: ['@vite-pwa/nuxt', '@nuxt/icon'],

  icon: {
    mode: 'svg',
    clientBundle: {
      scan: true,
      includeCustomCollections: true
    },
    serverBundle: 'local'
  },

  app: {
    head: {
      htmlAttrs: { lang: 'sk' },
      title: 'FEI Companion — Ultimate Student Hub for FEI STU Bratislava',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'description', content: 'Ultimate study companion for FEI STU Bratislava students: explore programs, survive your first week, match with JobFair employers.' },
        { name: 'keywords', content: 'FEI STU, FEI Bratislava, study programs, Erasmus, JobFair, freshman, survival kit, informatika, elektrotechnika' },
        { property: 'og:title', content: 'FEI Companion — Ultimate Student Hub' },
        { property: 'og:description', content: 'Discover programs, survive first weeks, land jobs — for every FEI STU student.' },
        { property: 'og:type', content: 'website' },
        { property: 'og:url', content: 'https://fei.murzin.digital' },
        { property: 'og:image', content: 'https://fei.murzin.digital/icon-512.png' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'theme-color', content: '#0a1726' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
        { name: 'apple-mobile-web-app-title', content: 'FEI Companion' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'format-detection', content: 'telephone=no' }
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/icon.svg' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/icon-180.png' },
        { rel: 'canonical', href: 'https://fei.murzin.digital' }
      ]
    }
  },

  nitro: {
    preset: 'node-server'
  },

  runtimeConfig: {
    geminiApiKey: process.env.GEMINI_API_KEY || '',
    public: {
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://fei.murzin.digital'
    }
  },

  css: ['~/assets/css/main.css'],

  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'FEI Companion — Student Hub',
      short_name: 'FEI Companion',
      description: 'Programs · Survival Kit · JobFair Match — your ultimate FEI STU companion.',
      lang: 'sk',
      theme_color: '#0a1726',
      background_color: '#060e1a',
      display: 'standalone',
      orientation: 'portrait',
      scope: '/',
      start_url: '/',
      categories: ['education', 'productivity', 'utilities'],
      icons: [
        { src: '/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
        { src: '/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
        { src: '/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
      ],
      shortcuts: [
        { name: 'Programs', short_name: 'Programs', url: '/courses', icons: [{ src: '/icon-192.png', sizes: '192x192' }] },
        { name: 'Survival Kit', short_name: 'Survival', url: '/freshman', icons: [{ src: '/icon-192.png', sizes: '192x192' }] },
        { name: 'JobFair', short_name: 'JobFair', url: '/jobfair', icons: [{ src: '/icon-192.png', sizes: '192x192' }] }
      ]
    },
    workbox: {
      globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2,json}'],
      navigateFallback: '/',
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
          handler: 'CacheFirst',
          options: {
            cacheName: 'google-fonts-stylesheets',
            expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 }
          }
        },
        {
          urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
          handler: 'CacheFirst',
          options: {
            cacheName: 'google-fonts-webfonts',
            expiration: { maxEntries: 30, maxAgeSeconds: 60 * 60 * 24 * 365 }
          }
        },
        {
          urlPattern: /\/data\/.*\.json$/,
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'fei-data',
            expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 }
          }
        }
      ]
    },
    client: { installPrompt: true },
    devOptions: { enabled: false }
  }
})
