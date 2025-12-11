import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [react()],
  base: "./", // Required for Electron to load assets correctly
  resolve: {
    alias: {
      "react-hot-toast": path.resolve(__dirname, "src/utils/toast.tsx"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/system": "http://localhost:8000",
      "/ai": "http://localhost:8000",
      "/search": "http://localhost:8000",
      "/projects": "http://localhost:8000",
      "/billing": "http://localhost:8000",
      "/planes": "http://localhost:8000",
      "/operations": "http://localhost:8000",
      "/audit": "http://localhost:8000",
      "/docs": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ui": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          router: ["react-router-dom"],
          query: ["@tanstack/react-query"],
        },
      },
    },
  },
});
