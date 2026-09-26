// Radar JCC — service worker: works offline, always tries fresh data first.
const VERSION = "radar-jcc-v1";
const SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png",
  "./data.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

async function dataRequest(request) {
  const cache = await caches.open(VERSION);
  const key = new URL("./data.json", self.registration.scope).href;
  try {
    const fresh = await fetch(request, { cache: "no-store" });
    if (fresh.ok) cache.put(key, fresh.clone());
    return fresh;
  } catch (err) {
    const cached = await cache.match(key);
    if (!cached) throw err;
    return new Response(await cached.blob(), {
      headers: { "Content-Type": "application/json", "X-Radar-Offline": "1" }
    });
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(VERSION);
  const cached = await cache.match(request, { ignoreSearch: request.mode === "navigate" });
  const network = fetch(request)
    .then((res) => {
      if (res && (res.ok || res.type === "opaque")) cache.put(request, res.clone());
      return res;
    })
    .catch(() => null);
  return cached || (await network) || (request.mode === "navigate" ? cache.match("./index.html") : Response.error());
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin === self.location.origin) {
    event.respondWith(url.pathname.endsWith("/data.json") ? dataRequest(request) : staleWhileRevalidate(request));
  } else if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    event.respondWith(staleWhileRevalidate(request));
  }
});
