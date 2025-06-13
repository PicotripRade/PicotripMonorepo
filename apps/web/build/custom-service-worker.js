// public/custom-service-worker.js

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    // Clear old cache versions here if needed
                    return caches.delete(cache);
                })
            );
        })
    );
});

self.addEventListener('fetch', (event) => {
    // This can be customized to cache certain requests or avoid caching
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
