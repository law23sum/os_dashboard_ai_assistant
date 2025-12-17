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
    https: false, // Vite dev server can run on HTTP, but proxies to HTTPS backend
    proxy: {
      "/api": {
        target: "https://localhost:8000",
        changeOrigin: true,
        secure: false, // Allow self-signed certificates
      },
      "/system": {
        target: "https://localhost:8000",
        secure: false,
      },
      "/ai": {
        target: "https://localhost:8000",
        secure: false,
      },
      "/search": {
        target: "https://localhost:8000",
        secure: false,
      },
      "/projects": {
        target: "https://localhost:8000",
        secure: false,
      },
      "/billing": {
        target: "https://localhost:8000",
        secure: false,
      },
      "/planes": {
        target: "https://localhost:8000",
        secure: false,
      },
      "/operations": {
        target: "https://localhost:8000",
        secure: false,
      },
      "/office": {
        target: "https://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/audit": {
        target: "https://localhost:8000",
        secure: false,
      },
      "/docs": {
        target: "https://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/ui": {
        target: "https://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/ws": {
        target: "wss://localhost:8000",
        ws: true,
        secure: false,
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
