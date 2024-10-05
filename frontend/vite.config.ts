import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export const API_URL = "http://localhost:5000";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    "import.meta.env.API_URL": JSON.stringify(API_URL),
  },
});
