# Rhoova: Cognitive Risk Layer (PoC) 🧠 + ⚙️

> **⚠️ DEMO / PROOF OF CONCEPT (PoC) UYARISI**
> Bu proje, **Rhoova Risk Altyapısı**'nın Üretken Yapay Zeka (Generative AI) ile entegre edildiğinde neler yapabileceğini gösteren bir **kavram kanıtı (Proof of Concept)** çalışmasıdır.
> Buradaki kodlar ve mimari, üretim ortamında (production) kullanılmak üzere değil; vizyonu somutlaştırmak ve iş mantığını sergilemek amacıyla hazırlanmıştır.

## 📖 Proje Hakkında

**"Risk Yönetimi ve Yapay Zeka Entegrasyonu**

Rhoova Cognitive Risk Layer; finansal risk yönetimini sadece sayısal hesaplamalardan ibaret olmaktan çıkarıp, **"okuyan, anlayan ve strateji öneren"** bir asistan yapısına dönüştürür.

Geleneksel dashboard'ların aksine bu proje, **Server-Driven UI** ve **Hibrit Mimari** kullanarak, karmaşık finansal raporları sohbet arayüzü içinde dinamik ve görsel olarak sunar.

## 🏗️ Sistem Mimarisi: Hibrit Yapı

Proje, dağıtık bir ön yüz ve merkezi bir zeka katmanından oluşur:

### 1. Frontend & Gateway (Edge Layer)
* **Teknoloji:** Cloudflare Workers (`wrangler`)
* **Görevi:** Statik arayüzü sunar (`index.html`, `style.css`, `app.js`) ve API isteklerini Python motoruna yönlendirir.
* **Konum:** `src/index.js` (Proxy) + `public/` (UI)

### 2. Backend & Intelligence (Core Layer)
* **Teknoloji:** Python (FastAPI), LangChain, Pandas
* **Görevi:** İş mantığını yürütür ve **Görselleştirme Katmanını** (`templates.py`) yönetir.
* **Entegrasyon:** `rhoova_integration` modülü üzerinden gerçek portföy verilerine ve hesaplama motoruna bağlanır.

## 🚀 Temel Yetenekler

### ✅ 1. Otonom Rapor Analizi (RAG)
Kullanıcı sisteme PDF yüklediğinde sistem devreye girer. Dokümanı tarar, içeriği analiz eder ve otomatik risk senaryoları önerir.

### ✅ 2. Text-to-Shock & Stratejist Yorumu
*"Faizler 200 bps artarsa ne olur?"* sorusuna karşılık sistem:
1.  Hesaplamayı yapar (Matematiksel Motor).
2.  Sonuçları yorumlar (AI Asistanı).
3.  Elde edilen veriyi görselleştirir.

### ✅ 3. Server-Driven UI (Sunucu Yönetimli Görselleştirme)
Proje, frontend karmaşasından kaçınmak için **`backend/templates.py`** kullanır.
* Python backend, P&L (Kar/Zarar) durumuna göre dinamik stillere sahip **HTML Dashboard Kartları** üretir.
* Frontend sadece bu HTML'i ekrana basar. Bu sayede yeni rapor formatları için frontend değişikliği gerekmez.

## 🛠️ Kurulum ve Çalıştırma

Sistemi ayağa kaldırmak için **iki ayrı terminal** penceresi kullanmalısınız.

### Adım 1: Backend (Python) Başlatma

1.  `backend` klasörüne (veya ana dizine) gidin ve sanal ortamı kurun:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

2.  Bağımlılıkları yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

3.  `.env` dosyasını oluşturun ve API anahtarınızı ekleyin:
    ```env
    OPENAI_API_KEY="sk-..."
    ```

4.  Sunucuyu başlatın (**Port 8000** zorunludur):
    ```bash
    python backend/main.py
    ```
    *(Not: `public_docs` klasörü otomatik oluşturulacaktır.)*

### Adım 2: Frontend (Cloudflare) Başlatma

1.  Yeni bir terminal açın ve proje ana dizininde:
    ```bash
    npm install
    ```

2.  Gateway'i başlatın:
    ```bash
    npx wrangler dev
    ```

3.  Size verilen yerel adrese (Genellikle `http://localhost:8787`) tarayıcıdan gidin.

## 📂 Proje Dosya Ağacı

```text
rhoova-cognitive-poc/
├── .env                       # API Anahtarları
├── requirements.txt           # Python kütüphaneleri
├── wrangler.toml              # Cloudflare konfigürasyonu
│
├── src/                       # EDGE GATEWAY
│   └── index.js               # API Proxy ve Statik Sunucu
│
├── public/                    # FRONTEND (UI)
│   ├── css/style.css          # Arayüz stilleri
│   ├── js/app.js              # Client-side mantık
│   └── index.html             # Ana Sayfa
│
├── public_docs/               # 📂 YÜKLENEN DOSYALAR
│                              # (Kullanıcı raporları burada saklanır)
│
└── backend/                   # BACKEND (CORE)
    ├── main.py                # FastAPI Sunucu Giriş Noktası
    ├── rhoova_ai_engine.py    # Ana Orkestratör (Engine)
    ├── templates.py           # 🎨 HTML Görselleştirme & Rapor Motoru
    │
    └── rhoova_integration/    # 🔌 ENTEGRASYON KATMANI
        ├── __init__.py
        └── portfolio.py       # Gerçek veri bağlantıları ve adaptörler
