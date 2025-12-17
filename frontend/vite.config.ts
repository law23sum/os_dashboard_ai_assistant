import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const apiTarget = process.env.VITE_API_TARGET || "http://localhost:8000";
const wsTarget = apiTarget.replace(/^http/, "ws");

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
    https: false,
    proxy: {
      "/api": {
        target: apiTarget,
        changeOrigin: true,
        secure: false, // Allow self-signed certificates
      },
      "/system": {
        target: apiTarget,
        secure: false,
      },
      "/ai": {
        target: apiTarget,
        secure: false,
      },
      "/search": {
        target: apiTarget,
        secure: false,
      },
      "/projects": {
        target: apiTarget,
        secure: false,
      },
      "/billing": {
        target: apiTarget,
        secure: false,
      },
      "/planes": {
        target: apiTarget,
        secure: false,
      },
      "/operations": {
        target: apiTarget,
        secure: false,
      },
      "/office": {
        target: apiTarget,
        changeOrigin: true,
        secure: false,
      },
      "/audit": {
        target: apiTarget,
        secure: false,
      },
      "/docs": {
        target: apiTarget,
        changeOrigin: true,
        secure: false,
      },
      "/ui": {
        target: apiTarget,
        changeOrigin: true,
        secure: false,
      },
      "/ws": {
        target: wsTarget,
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
