import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import AppIphone from "./AppIphone";
import "../estilos.css";
import "./iphone.css";

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js", { scope: "./" }).catch(() => {
      /* sin service worker la app funciona igual, solo que no offline */
    });
  });
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppIphone />
  </StrictMode>,
);
