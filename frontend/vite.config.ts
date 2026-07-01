import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import path from 'path';
import fs from 'fs';

// Docker mounts ./.cursor → /app/.cursor-host
const DEBUG_LOG_PATH = path.resolve(__dirname, '.cursor-host/debug-c10c9a.log');

function debugLogPlugin() {
  return {
    name: 'debug-log',
    configureServer(server: { middlewares: { use: Function } }) {
      server.middlewares.use('/__debug_log', (req: { method?: string; on: Function }, res: { statusCode: number; end: Function }, next: () => void) => {
        if (req.method !== 'POST') {
          next();
          return;
        }
        let body = '';
        req.on('data', (chunk: Buffer | string) => { body += chunk; });
        req.on('end', () => {
          try {
            fs.mkdirSync(path.dirname(DEBUG_LOG_PATH), { recursive: true });
            fs.appendFileSync(DEBUG_LOG_PATH, body.trim() + '\n');
          } catch { /* ignore */ }
          res.statusCode = 204;
          res.end();
        });
      });
    },
  };
}
// Enable proxy via environment variable (default true for development)
const enableProxy = process.env.VITE_ENABLE_PROXY !== 'false';

// Mock data for API endpoints when backend is unavailable
const mockResults = { results: [{ id: 1, value: 'sample' }], total: 1 };
const mockUserCount = { count: 42 };

function mockApiPlugin() {
  return {
    name: 'mock-api',
    configureServer(server: any) {
      server.middlewares.use('/api/results/', (req: any, res: any, next: any) => {
        if (!enableProxy) {
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify(mockResults));
        } else {
          next();
        }
      });

      server.middlewares.use('/api/users/count', (req: any, res: any, next: any) => {
        if (!enableProxy) {
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify(mockUserCount));
        } else {
          next();
        }
      });
    }
  };
}

export default defineConfig({
  resolve: {
    alias: {
      '@mediapipe/camera_utils': path.resolve(
        __dirname,
        'node_modules/@mediapipe/camera_utils/camera_utils.js'
      ),
    },
  },
  plugins: [sveltekit(), debugLogPlugin(), mockApiPlugin()],
  server: {
    ...(enableProxy && (function () {
      const API_TARGET = process.env.VITE_API_TARGET || 'http://backend:5000';
      return {
        proxy: {
          '/api': {
            target: API_TARGET,
            changeOrigin: true,
            secure: false,
          },
        },
      };
    })())
  }
});
