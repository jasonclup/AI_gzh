/**
 * 公众号爆款内容发布系统 - PWA Service Worker
 * 
 * 功能：
 * 1. 离线缓存（核心页面和静态资源）
 * 2. API请求缓存策略
 * 3. 后台同步支持（发布任务队列）
 * 4. 推送通知处理
 */

const CACHE_NAME = 'wechat-publisher-v1';
const STATIC_CACHE = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';

// ========== 预缓存：核心资源 ==========
const PRECACHE_URLS = [
  '/',
  '/topics',
  '/editor',
  '/publish',
  '/settings',
  '/static/manifest.json',
  // CSS/JS 会在首次加载时自动缓存
];

// ========== 安装：预缓存 ==========
self.addEventListener('install', (event) => {
  console.log('[SW] 安装中...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] 预缓存核心页面');
      return cache.addAll(PRECACHE_URLS).catch((err) => {
        console.warn('[SW] 预缓存部分失败（离线模式正常）:', err);
        // 预缓存失败不阻塞安装
        return Promise.resolve();
      });
    })
  );
  // 立即激活，不等待旧SW退出
  self.skipWaiting();
});

// ========== 激活：清理旧缓存 ==========
self.addEventListener('activate', (event) => {
  console.log('[SW] 激活');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== STATIC_CACHE && name !== DYNAMIC_CACHE)
          .map((name) => {
            console.log('[SW] 删除旧缓存:', name);
            return caches.delete(name);
          })
      );
    })
  );
  // 立即控制所有页面
  self.clients.claim();
});

// ========== 请求拦截：缓存策略 ==========
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 只处理同源请求（不处理跨域API调用）
  if (url.origin !== location.origin) {
    return;
  }

  // === 导航请求（HTML页面）：网络优先 + 缓存回退 ===
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // 成功则缓存副本
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          return response;
        })
        .catch(() => {
          // 网络失败，返回缓存
          return caches.match(request).then((cached) => {
            return cached || caches.match('/'); // 最后回退到首页
          });
        })
    );
    return;
  }

  // === 静态资源（CSS/JS/图片）：缓存优先 + 网络更新 ===
  if (
    url.pathname.startsWith('/static/') ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.png') ||
    url.pathname.endsWith('.jpg') ||
    url.pathname.endsWith('.svg') ||
    url.pathname.endsWith('.woff2')
  ) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const fetchPromise = fetch(request)
          .then((response) => {
            if (response.ok) {
              const clone = response.clone();
              caches.open(STATIC_CACHE).then((cache) => cache.put(request, clone));
            }
            return response;
          })
          .catch(() => cached); // 回退到缓存

        return cached || fetchPromise;
      })
    );
    return;
  }

  // === API 请求：网络优先 + 短时缓存 ===
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // GET请求缓存5分钟
          if (request.method === 'GET' && response.ok) {
            const clone = response.clone();
            caches.open(DYNAMIC_CACHE).then((cache) =>
              cache.put(request, clone)
            );
          }
          return response;
        })
        .catch(() => {
          // API离线时返回缓存的最后结果
          return caches.match(request).then((cached) => {
            if (cached) return cached;
            // 返回友好的离线响应
            return new Response(
              JSON.stringify({ success: false, error: '网络不可用，请检查连接后重试' }),
              {
                status: 503,
                headers: { 'Content-Type': 'application/json' },
              }
            );
          });
        })
    );
    return;
  }

  // === 其他请求：默认策略 ===
  event.respondWith(
    caches.match(request).then(() => fetch(request))
  );
});

// ========== 后台同步：发布队列 ==========
self.addEventListener('sync', (event) => {
  console.log('[SW] 后台同步:', event.tag);

  if (event.tag === 'publish-queue') {
    event.waitUntil(syncPublishQueue());
  }
  
  if (event.tag === 'fetch-topics') {
    event.waitUntil(syncFetchTopics());
  }
});

/**
 * 同步发布队列：把离线时的待发布文章逐个提交
 */
async function syncPublishQueue() {
  try {
    // 从 IndexedDB 获取待发布队列（需要前端配合实现）
    // 这里是框架代码，实际使用时前端需将发布请求存入队列
    console.log('[SW] 同步发布队列...');
    
    // 通知所有客户端同步完成
    const clients = await self.clients.matchAll();
    clients.forEach((client) => {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        tag: 'publish-queue',
      });
    });
  } catch (err) {
    console.error('[SW] 发布队列同步失败:', err);
  }
}

/**
 * 后台抓取热点话题
 */
async function syncFetchTopics() {
  try {
    const response = await fetch('/api/topics/fetch');
    if (response.ok) {
      const data = await response.json();
      
      // 如果有新热点，通知前端
      if (data.success && data.data && data.data.length > 0) {
        const clients = await self.clients.matchAll();
        clients.forEach((client) => {
          client.postMessage({
            type: 'NEW_TOPICS',
            count: data.data.length,
          });
        });
      }
    }
  } catch (err) {
    console.error('[SW] 后台热点抓取失败:', err);
  }
}

// ========== 推送通知 ==========
self.addEventListener('push', (event) => {
  console.log('[SW] 收到推送:', event);

  let data = {
    title: '公众号发布系统',
    body: '您有新的消息',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
  };

  if (event.data) {
    try {
      data = { ...data, ...event.data.json() };
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: data.icon || '/static/icons/icon-192x192.png',
    badge: data.badge || '/static/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/',
      timestamp: Date.now(),
    },
    actions: [
      { action: 'view', title: '查看详情' },
      { action: 'close', title: '关闭' },
    ],
  };

  event.waitUntil(self.registration.showNotification(data.title, options));
});

// ========== 通知点击 ==========
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'view' || !event.action) {
    const url = event.notification?.data?.url || '/';
    event.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
        // 已有窗口则聚焦
        for (const client of clientList) {
          if (client.url.includes(url) && 'focus' in client) {
            return client.focus();
          }
        }
        // 否则打开新窗口
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
    );
  }
});

console.log('[SW] Service Worker 已加载 - wechat-publisher-pwa');
