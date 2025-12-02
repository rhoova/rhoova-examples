# Real-Time Risk Dashboard (UI)
Bu modül, **Rhoova Risk Monitoring System**’in son kullanıcı arayüzüdür.  
Cloudflare Wrangler ile servis edilir ve backend’e **WebSocket** üzerinden bağlanır.

## 📋 Ön Gereksinimler
- **Node.js**: v18+ önerilir  
- **Cloudflare hesabı**: Deploy için gereklidir  

## 🚀 Kurulum ve Geliştirme
`ui` klasörüne girdikten sonra:

### 1. Bağımlılıkları yükleyin
```bash
npm install
```

### 2. Geliştirme modunda çalıştırın
```bash
npm run dev
```
Arayüz: http://localhost:8788  
Backend WS: ws://localhost:8000/ws

## ⚡ Alternatif: Hızlı Önizleme (Node.js Olmadan)
```bash
python -m http.server 8788
```

## ☁️ Dağıtım (Deployment)
```bash
npx wrangler login
npm run deploy
```

## 📦 Veri Formatları (Payload Specs)

### 1. Tekil Veri Güncellemesi (Yield Update)
```json
{
  "tenor": "2Y",
  "value": 0.33,
  "instrument": "OIS",
  "currency": "TRY",
  "valuationDate": "2025-02-25",
  "publishedAt": "2025-08-24T18:24:07Z"
}
```

### 2. Toplu Tick Verisi
```json
{
  "type": "tick",
  "yields": { "2Y": 4.24, "5Y": 5.10 },
  "ts": "2025-08-24T18:25:00Z"
}
```

### 3. Alarm (Alert) Mesajı
```json
{
  "type": "alert",
  "data": {
    "tenor": "5Y",
    "message": "Threshold exceeded: 5.12 > 5.00"
  }
}
```

### 4. Pozisyonlar (Positions)
```json
{
  "rows": [
    {
      "TradeID": "T1",
      "ISIN": "US123",
      "Notional": 500,
      "Side": "Buy"
    }
  ]
}
```

## ⚙️ Konfigürasyon
Varsayılan WebSocket URL:  
```
ws://localhost:8000/ws
```

URL parametresi ile değiştirebilirsiniz:  
```
http://localhost:8788/?ws=ws://192.168.1.50:8000/ws
```

Failover: UI ana kanala bağlanamazsa `/ws/yield` ve `/ws/alerts` kanallarını dener.

