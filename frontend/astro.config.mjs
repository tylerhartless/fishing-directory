// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Determine site URL based on environment
// ASTRO_SITE can be set during build for staging deployments
const siteUrl = process.env.ASTRO_SITE || 'https://wherecanifish.com';

// https://astro.build/config
export default defineConfig({
  site: siteUrl,
  integrations: [sitemap()],
  output: 'static',
  build: {
    assets: '_assets'
  }
});
