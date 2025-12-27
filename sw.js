// sw.js
const CACHE_NAME = 'birthday-manager-v1';

// 1. 安装阶段：可以在这里做些初始化，但为了不卡顿，我们什么都不强制预缓存
self.addEventListener('install', (event) => {
    // 强制立即接管页面，不需要等待用户刷新
    self.skipWaiting();
    console.log('[Service Worker] Installed');
});

// 2. 激活阶段：清理旧缓存
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        console.log('[Service Worker] Clearing Old Cache');
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
    // 让 Service Worker 立即控制所有页面
    return self.clients.claim();
});

// 3. 拦截网络请求 (核心逻辑：边用边缓存)
self.addEventListener('fetch', (event) => {
    // 只处理 HTTP/HTTPS 请求 (过滤掉 chrome-extension:// 等协议)
    if (!event.request.url.startsWith('http')) {
        return;
    }

    event.respondWith(
        // A. 尝试从网络获取 (Network First)
        fetch(event.request)
            .then((response) => {
                // 如果网络请求成功：
                
                // 1. 检查响应是否有效
                if (!response || response.status !== 200 || response.type !== 'basic' && response.type !== 'cors') {
                    return response;
                }

                // 2. 复制一份响应（因为流只能读取一次）
                const responseToCache = response.clone();

                // 3. 将这一份存入缓存 (边用边存!)
                caches.open(CACHE_NAME)
                    .then((cache) => {
                        // 这里的 put 是异步的，不会阻塞页面显示
                        cache.put(event.request, responseToCache);
                    });

                // 4. 返回原始响应给页面使用
                return response;
            })
            .catch(() => {
                // B. 如果网络断开或请求失败，尝试从缓存获取
                console.log('[Service Worker] Network failed, looking in cache for:', event.request.url);
                return caches.match(event.request)
                    .then((cachedResponse) => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        // 如果缓存里也没有（比如没访问过的图片），可以在这里返回一个默认的离线占位图
                        // return caches.match('/offline-image.png');
                    });
            })
    );
});