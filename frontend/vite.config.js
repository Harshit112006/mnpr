import react from "@vitejs/plugin-react";
import {
  defineConfig,
} from "vite";

import {
  VitePWA,
} from "vite-plugin-pwa";


export default defineConfig({

  plugins: [

    react(),

    VitePWA({

      registerType:
        "prompt",

      injectRegister:
        "auto",

      includeAssets: [
        "icons/pwa-192x192.png",
        "icons/pwa-512x512.png",
        "icons/pwa-maskable-512x512.png",
      ],


      manifest: {

        name:
          "BreedVision AI",

        short_name:
          "BreedVision",

        description:
          "AI-powered cattle and buffalo breed identification and livestock operations platform.",

        theme_color:
          "#07151c",

        background_color:
          "#07151c",

        display:
          "standalone",

        orientation:
          "portrait-primary",

        start_url:
          "/",

        scope:
          "/",


        icons: [

          {
            src:
              "/icons/pwa-192x192.png",

            sizes:
              "192x192",

            type:
              "image/png",
          },


          {
            src:
              "/icons/pwa-512x512.png",

            sizes:
              "512x512",

            type:
              "image/png",
          },


          {
            src:
              "/icons/pwa-maskable-512x512.png",

            sizes:
              "512x512",

            type:
              "image/png",

            purpose:
              "maskable",
          },

        ],

      },


      workbox: {

  cleanupOutdatedCaches:
    true,

  clientsClaim:
    true,

  skipWaiting:
    false,

  navigateFallback:
    "/index.html",

  globPatterns: [
    "**/*.{js,css,html,ico,png,svg,webp,woff2}",
  ],

},
    }),

  ],

});