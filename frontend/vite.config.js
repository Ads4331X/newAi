// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  define: {
    // This tells Vite that when it sees "PIXI", it should look at window.PIXI
    PIXI: "window.PIXI",
  },
  resolve: {
    alias: {
      // If you are using the official Framework folders, add this alias
      "@framework":
        "/home/erza/git_projects/newAi/frontend/CubismSdkForWeb-5-r.4/Framework",
    },
  },
});
