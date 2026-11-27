// Service worker de la versión iPhone: guarda la app y los modelos ya vistos para usarlos sin internet.
const VERSION = "atlas-iphone-v4";
const NUCLEO = ["./", "./index.html", "./manifest.webmanifest", "./icono-180.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(NUCLEO)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  const pesado = /\/modelos-iphone\/.+\.glb$|\/draco\//.test(url.pathname);
  if (pesado) {
    // Modelos: primero la copia guardada (no cambian entre versiones).
    e.respondWith(
      caches.open(VERSION).then(async (c) => {
        const guardado = await c.match(e.request);
        if (guardado) return guardado;
        const r = await fetch(e.request);
        if (r.ok) c.put(e.request, r.clone());
        return r;
      }),
    );
  } else {
    // App, fichas y manifest: primero la red (para recibir correcciones); sin red, la copia.
    e.respondWith(
      fetch(e.request)
        .then((r) => {
          if (r.ok) {
            const copia = r.clone();
            caches.open(VERSION).then((c) => c.put(e.request, copia));
          }
          return r;
        })
        .catch(() => caches.match(e.request).then((g) => g || caches.match("./index.html"))),
    );
  }
});
