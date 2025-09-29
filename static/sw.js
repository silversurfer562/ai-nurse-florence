// Service Worker for PWA functionality
// Provides offline support and app-like behavior

const CACHE_NAME = 'ai-nurse-florence-v2.0.1';
const STATIC_CACHE = 'static-v2.0.1';
const DYNAMIC_CACHE = 'dynamic-v2.0.1';

// Files to cache for offline functionality
const STATIC_FILES = [
    '/',
    '/static/index.html',
    '/static/clinical-workspace.html',
    '/static/css/app.css',
    '/static/js/app.js',
    '/static/js/mobile-touch-enhancer.js',
    '/static/manifest.json',
    'https://cdn.tailwindcss.com',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// API endpoints that should be cached
const API_CACHE_PATTERNS = [
    '/api/v1/health',
    '/api/v1/quick-assessment',
    '/api/v1/medical-info'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static files...');
                return cache.addAll(STATIC_FILES);
            })
            .catch(err => console.log('Cache installation failed:', err))
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
    );
    self.clients.claim();
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests and chrome-extension requests
    if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
        return;
    }

    // Handle different types of requests
    if (isStaticFile(request.url)) {
        event.respondWith(cacheFirst(request));
    } else if (isAPIRequest(request.url)) {
        event.respondWith(networkFirst(request));
    } else {
        event.respondWith(staleWhileRevalidate(request));
    }
});

// Cache first strategy (for static files)
async function cacheFirst(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        const networkResponse = await fetch(request);
        const cache = await caches.open(STATIC_CACHE);
        cache.put(request, networkResponse.clone());
        return networkResponse;
    } catch (error) {
        console.log('Cache first failed:', error);
        return new Response('Offline content not available', { status: 503 });
    }
}

// Network first strategy (for API calls)
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);

        // Cache successful API responses
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.log('Network request failed, trying cache:', error);
        const cachedResponse = await caches.match(request);

        if (cachedResponse) {
            return cachedResponse;
        }

        // Return offline API response
        return new Response(
            JSON.stringify({
                message: 'This feature requires an internet connection',
                offline: true,
                timestamp: new Date().toISOString()
            }),
            {
                headers: { 'Content-Type': 'application/json' },
                status: 503
            }
        );
    }
}

// Stale while revalidate strategy (for dynamic content)
async function staleWhileRevalidate(request) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await caches.match(request);

    const fetchPromise = fetch(request).then(networkResponse => {
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    });

    return cachedResponse || fetchPromise;
}

// Helper functions
function isStaticFile(url) {
    return STATIC_FILES.some(file => url.includes(file)) ||
           url.includes('.css') ||
           url.includes('.js') ||
           url.includes('.png') ||
           url.includes('.jpg') ||
           url.includes('.ico');
}

function isAPIRequest(url) {
    return API_CACHE_PATTERNS.some(pattern => url.includes(pattern)) ||
           url.includes('/api/');
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag);

    if (event.tag === 'chat-message-sync') {
        event.waitUntil(syncChatMessages());
    }
});

async function syncChatMessages() {
    // Implement chat message synchronization
    console.log('Syncing offline chat messages...');

    try {
        const offlineMessages = await getOfflineMessages();

        for (const message of offlineMessages) {
            await fetch('/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(message)
            });
        }

        await clearOfflineMessages();
        console.log('Chat messages synced successfully');
    } catch (error) {
        console.log('Chat sync failed:', error);
    }
}

async function getOfflineMessages() {
    // Get messages from IndexedDB or localStorage
    return JSON.parse(localStorage.getItem('offlineChatMessages') || '[]');
}

async function clearOfflineMessages() {
    localStorage.removeItem('offlineChatMessages');
}

// Push notification handling
self.addEventListener('push', (event) => {
    const options = {
        body: 'You have new clinical updates available',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Updates',
                icon: '/static/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/icons/xmark.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('AI Nurse Florence', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/clinical-workspace.html')
        );
    }
});
