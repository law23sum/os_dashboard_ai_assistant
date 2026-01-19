import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Support multiple port configurations: 8070 (assistant_hub_gui direct), 8000 (start_ui.py - default)
const resolveProxyTarget = () => {
  const explicitTarget = process.env.VITE_API_TARGET;
  if (explicitTarget) return explicitTarget;

  const baseEnv = process.env.VITE_API_BASE_URL || process.env.VITE_API_BASE;
  if (baseEnv && /^https?:\/\//.test(baseEnv)) {
    try {
      return new URL(baseEnv).origin;
    } catch {
      // Fall through to host/port defaults.
    }
  }

  const host = process.env.OSDASH_API_HOST || "127.0.0.1";
  const port = process.env.OSDASH_API_PORT || "8000";
  const normalizedHost = host === "0.0.0.0" ? "127.0.0.1" : host;
  return `http://${normalizedHost}:${port}`;
};

const apiTarget = resolveProxyTarget();
const wsTarget = apiTarget.replace(/^http/, "ws");

export default defineConfig({
  plugins: [react()],
  base: "./", // Required for Electron to load assets correctly
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "react-hot-toast": path.resolve(__dirname, "src/utils/toast.tsx"),
    },
  },
  server: {
    host: process.env.VITE_HOST || '127.0.0.1', // Bind to localhost only for security (use VITE_HOST=0.0.0.0 for network access)
    port: 5173,
    https: false,
    proxy: {
      // Only proxy actual API calls - NOT frontend routes
      // All API calls should go through /api prefix
      "/api": {
        target: apiTarget,
        changeOrigin: true,
        secure: false,
      },
      // WebSocket connection for real-time updates
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
        manualChunks(id) {
          const normalizedId = id.replace(/\\/g, "/");

          if (normalizedId.includes("/src/data/iaManifest.from_json")) {
            return "ia-manifest";
          }

          if (normalizedId.includes("/src/navigation/routeComponentMap")) {
            return "route-map";
          }

          if (normalizedId.includes("node_modules")) {
            if (normalizedId.includes("/node_modules/react-dom/") || normalizedId.includes("/node_modules/react/")) {
              return "react";
            }
            if (normalizedId.includes("/node_modules/react-router")) {
              return "router";
            }
            if (normalizedId.includes("/node_modules/@tanstack/")) {
              return "query";
            }
            if (normalizedId.includes("/node_modules/axios/")) {
              return "axios";
            }
            if (normalizedId.includes("/node_modules/lucide-react/")) {
              return "icons";
            }
            if (normalizedId.includes("/node_modules/zod/")) {
              return "zod";
            }
            return "vendor";
          }

          return undefined;
        },
      },
    },
  },
});
