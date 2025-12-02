# Real-Time Risk Monitoring System Powered by Rhoova
Bu proje, **Rhoova Risk Infrastructure** kullanılarak geliştirilmiş, veritabanısız (stateless), olay güdümlü (event-driven) ve gerçek zamanlı bir risk izleme sistemidir. Sistem, Python servisleri, Redis Pub/Sub, FastAPI WebSocket Gateway ve Cloudflare Wrangler frontend’i ile tam entegre çalışır.

## 🛠 Teknolojiler
- **Python** (Core + Background Services)
- **Redis** (Pub/Sub Message Broker)
- **FastAPI + WebSocket**
- **Cloudflare Wrangler (Frontend)**
- **Rhoova SDK** (Risk Engine)
- **Telegram Bot API** (Bildirimler)
- **Pytest** (Unit Test)

## 📂 Proje Yapısı
```
domain/                         
  models.py                     
  thresholds.py                 
  __init__.py

controllers/                    
  alert_controller.py
  threshold_controller.py
  yield_controller.py
  __init__.py

services/                       
  alert_service.py              
  services_alert_listener.py    
  publisher.py                  
  telegram_notifier.py          
  repository.py                 

app/                            
  main.py
  websocket.py
  ws_manager.py
  settings.py

utils/
  tradefiles.py                 

static/                         
  test.html
  test.js

tests/                          
  test_alerts.py

tools/
  publisher_test.py             

ui/                             
  dist/
  wrangler.jsonc
  package.json

rhoova_folder/                  

yielddata.csv                   
thresholds.json                 
requirements.txt                
```

## ✨ Özellikler
### Teknik Özellikler
✔ Veritabanısız mimari  
✔ Gerçek zamanlı hesaplama  
✔ Event-driven push yapısı  
✔ WebSocket canlı veri akışı  
✔ Excel/CSV entegrasyonu  
✔ API-first tasarım  

### Operasyonel
✔ Telegram bildirimleri  
✔ Limit aşımı alert sistemi  
✔ Test edilebilir altyapı  
✔ İzlenebilir servis yapısı  

## 🚀 Kurulum ve Çalıştırma

### 1. Redis Kurulumu
```
brew install redis
redis-server
```
Docker:
```
docker run --name redis -p 6379:6379 -d redis
```

### 2. Python Bağımlılıkları
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Servislerin Başlatılması
Terminal 1:
```
uvicorn app.main:app --reload --port 8000
```

Terminal 2:
```
python -m services.publisher
```

Terminal 3:
```
python -m services.services_alert_listener
```

Terminal 4:
```
cd ui
npm run start
```

## 🧪 Test & Debug
### Unit Test
```
pytest tests/
```

### Redis’e manuel test verisi basma
```
python tools/publisher_test.py
```

### WebSocket Testi
Tarayıcıdan aç:  
http://localhost:8000/static/test.html

## 📜 Lisans
MIT License
