import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Interface locale : 127.0.0.1:5173. L'API Flask reste sur 127.0.0.1:5000.
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
  },
})
