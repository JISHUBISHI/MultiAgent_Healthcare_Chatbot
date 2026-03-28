self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open("healthbuddy-shell-v1").then((cache) =>
      cache.addAll([
        "/",
        "/manifest.webmanifest",
        "/icon-192.png",
        "/icon-512.png",
        "/icon-512-maskable.png",
        "/healthbuddy-logo.jpeg"
      ])
    )
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) {
        return cached;
      }
      return fetch(event.request).then((response) => {
        const cloned = response.clone();
        caches.open("healthbuddy-shell-v1").then((cache) => cache.put(event.request, cloned));
        return response;
      });
    })
  );
});
