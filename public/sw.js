/**
 * PEP HUB Service Worker v3.1.0 — Regional Norte
 * Proteção Rigorosa de Sessão, Network-First para Scripts & Deploy Transparente sem CTRL+F5
 */

const CACHE_NAME = 'pephub-cache-v3.1.0';

const PRECACHE_ASSETS = [
  '/offline.html',
  '/manifest.webmanifest',
  '/css/app-mobile.css',
  '/js/app-mobile.js',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-maskable-192.png',
  '/icons/icon-maskable-512.png',
  '/icons/apple-touch-icon.png',
  '/icons/favicon.png',
  '/icons/icon.svg'
];

// Instalação do Service Worker e Precache do Shell
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[ServiceWorker] Pre-caching Core Shell & Assets v3.0.0');
      return cache.addAll(PRECACHE_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Ativação e Limpeza Automática de Caches Antigos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('[ServiceWorker] Removendo cache obsoleto:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Permite acionar skipWaiting ou purgar caches via mensagem do cliente
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data && event.data.type === 'LOGOUT') {
    caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k))));
  }
});

// Estratégia de Roteamento e Interceptação de Requisições
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);

  // Ignorar requisições não-GET (POST, PUT, DELETE vão direto para a rede)
  if (req.method !== 'GET') {
    return;
  }

  // Ignorar URLs externas
  if (url.origin !== self.location.origin) {
    return;
  }

  // 1. API Dinâmica (/api/*): Network-First com Fallback Offline
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(req)
        .then(networkResponse => {
          if (networkResponse && networkResponse.status === 200) {
            const resClone = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(req, resClone));
          }
          return networkResponse;
        })
        .catch(() => {
          return caches.match(req).then(cached => {
            if (cached) return cached;
            return new Response(
              JSON.stringify({
                offline: true,
                message: 'Você está no modo offline. Reconecte-se para sincronizar os dados mais recentes.'
              }),
              {
                headers: { 'Content-Type': 'application/json; charset=utf-8' },
                status: 200
              }
            );
          });
        })
    );
    return;
  }

  // 2. Arquivos de Áudio do Podcast (.mp3): Cache-First
  if (url.pathname.endsWith('.mp3')) {
    event.respondWith(
      caches.match(req).then(cached => {
        if (cached) return cached;
        return fetch(req).then(networkResponse => {
          if (networkResponse && networkResponse.status === 200) {
            const resClone = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(req, resClone));
          }
          return networkResponse;
        });
      })
    );
    return;
  }

  // 3. Documentos HTML e Navegações: Network-Only Obrigatório (Garante Validação de Sessão Server-Side)
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(req).catch(async () => {
        const fallback = await caches.match('/offline.html');
        return fallback || new Response('Offline - Reconecte-se para acessar o PEP HUB.', {
          status: 503,
          headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
      })
    );
    return;
  }

  // 4. Recursos de Código e Estilo (JS e CSS): Network-First (Deploy imediato sem CTRL+F5)
  if (/\.(js|css)$/i.test(url.pathname)) {
    event.respondWith(
      fetch(req)
        .then(networkResponse => {
          if (networkResponse && networkResponse.status === 200) {
            const resClone = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(req, resClone));
          }
          return networkResponse;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // 5. Imagens, Fontes e Ícones: Stale-While-Revalidate Otimizado
  event.respondWith(
    caches.match(req).then(cachedResponse => {
      const fetchPromise = fetch(req)
        .then(networkResponse => {
          if (networkResponse && networkResponse.status === 200) {
            const resClone = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(req, resClone));
          }
          return networkResponse;
        })
        .catch(() => cachedResponse);

      return cachedResponse || fetchPromise;
    })
  );
});

// Suporte a Notificações Push Corporativas
self.addEventListener('push', event => {
  let data = {
    title: 'PEP HUB · Regional Norte',
    body: 'Atualização de indicadores operacionais disponível.',
    url: '/'
  };

  if (event.data) {
    try {
      data = Object.assign(data, event.data.json());
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: '/icons/icon-192.png',
    badge: '/icons/favicon.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/'
    },
    actions: [
      { action: 'open', title: 'Abrir Painel' },
      { action: 'close', title: 'Fechar' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Ação de Clique na Notificação Push
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'close') return;

  const targetUrl = event.notification.data.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      for (let client of windowClients) {
        if (client.url.includes(targetUrl) && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
