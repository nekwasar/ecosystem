// Service Worker for Portfolio Image Caching
// Cache First for Images, Network First for HTML/JS/CSS

const CACHE_NAME = 'portfolio-assets-v1';
const IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico'];

// install: Cache core assets (optional, here we focus on runtime caching)
self.addEventListener('install', (event) => {
    self.skipWaiting();
    console.log('[SW] Installed');
});

// activate: detailed cleanup of old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        console.log('[SW] Clearing old cache:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
    return self.clients.claim();
});

// fetch: implementing strategies
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Only handle GET requests
    if (event.request.method !== 'GET') return;

    // Check if it's an image
    const isImage = IMAGE_EXTENSIONS.some(ext => url.pathname.endsWith(ext));

    if (isImage) {
        // Strategy: Cache First, falling back to network
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                if (cachedResponse) {
                    // Return cached response immediately
                    return cachedResponse;
                }

                // Fetch from network, then cache
                return fetch(event.request).then((networkResponse) => {
                    // Check if we received a valid response
                    if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                        return networkResponse;
                    }

                    // Clone the response because it's a stream and can only be consumed once
                    const responseToCache = networkResponse.clone();

                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseToCache);
                    });

                    return networkResponse;
                });
            })
        );
    } else {
        // Strategy: Network First (for HTML, JS, CSS) to always get fresh content, falling back to cache if offline
        // Ideally we don't cache HTML aggressively for development, but good for production PWA
        // For this specific request ("cache images"), we can stick to mainly network for others to avoid stale code issues
        return; // Let browser handle it normally (Network only)
    }
});
