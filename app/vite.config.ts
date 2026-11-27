import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";

// Dos versiones con el mismo código: Mac (index.html) e iPhone (iphone/index.html).
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    rollupOptions: {
      input: {
        mac: resolve(__dirname, "index.html"),
        iphone: resolve(__dirname, "iphone/index.html"),
      },
    },
  },
});
