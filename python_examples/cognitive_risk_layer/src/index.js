/**
 * RHOOVA GATEWAY (Proxy)
 * Frontend isteklerini karşılar, statik dosyaları sunar,
 * API isteklerini yerel Python sunucusuna (veya ilerde canlı sunucuya) iletir.
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 1. API veya Upload isteği mi? (Python'a yönlendir)
    if (url.pathname.startsWith('/api') || url.pathname.startsWith('/upload-doc')) {
      
      // Localhost Python Sunucusu
      const pythonServer = "http://127.0.0.1:8000";
      
      // Hedef URL'i oluştur (Örn: http://127.0.0.1:8000/api/chat)
      const targetUrl = pythonServer + url.pathname + url.search;

      // Orijinal isteği kopyala ama URL'i değiştir
      const proxyRequest = new Request(targetUrl, {
        method: request.method,
        headers: request.headers,
        body: request.body
      });

      try {
        // Python sunucusuna git
        return await fetch(proxyRequest);
      } catch (e) {
        return new Response(JSON.stringify({ 
            error: "Python Engine'e ulaşılamadı. main.py çalışıyor mu?",
            details: e.message 
        }), { status: 502, headers: {'Content-Type': 'application/json'} });
      }
    }

    // 2. Değilse Statik Dosya Sun (Frontend)
    return env.ASSETS.fetch(request);
  },
};