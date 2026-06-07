import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://repuvesaltillo.com',
  trailingSlash: 'always',
  build: {
    format: 'directory'
  }
});
