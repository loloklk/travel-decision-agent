import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    proxy: Object.fromEntries(
      ['/chat', '/stop', '/history', '/conversations', '/delete-conversation', '/clear-history', '/health']
        .map(path => [path, 'http://127.0.0.1:8000']),
    ),
  },
});
