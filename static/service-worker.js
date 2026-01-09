const CACHE_NAME = "break-balance-v1";
const ASSETS = [
  "/",
  "/static/manifest.json",
  "/static/mug_favicon.ico",
  "/static/mug_icon-192.png",
  "/static/mug_icon-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
