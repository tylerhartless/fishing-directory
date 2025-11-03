// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://wherecanifish.com',
  integrations: [sitemap()],
  output: 'static',
  build: {
    assets: '_assets'
  }
});
