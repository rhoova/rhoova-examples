/**
 * RHOOVA AI FRONTEND - FINAL GOLD MASTER (FIXED)
 * Özellikler:
 * - Orijinal yapı korundu.
 * - 'Simüle Et' butonlarındaki tırnak işareti hatası giderildi.
 */

const chatWindow = document.getElementById('chatWindow');
const userInput = document.getElementById('userInput');
const fileInput = document.getElementById('fileInput');

// Doğrudan Python Backend'e bağlan
const API_BASE_URL = "http://127.0.0.1:8000"; 

let isWelcomeScreenVisible = true;
let statusCheckInterval = null;

// --- BAŞLANGIÇ ---
window.onload = function() {
    console.log("Rhoova AI Başlatıldı.");
    
    // 1. İlk Durum Kontrolü
    checkSystemStatus(); 
    
    // 2. Sürekli Takip (Backend açılınca yakalamak için)
    statusCheckInterval = setInterval(checkSystemStatus, 3000);
};

// --- OLAY DİNLEYİCİLERİ ---
if (userInput) {
    // Textarea otomatik yükseklik ayarı
    userInput.addEventListener('input', function() {
        this.style.height = 'auto'; 
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Enter tuşu ile gönderme (Shift+Enter alt satır)
    userInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); // Alt satıra geçmeyi engelle
            sendMessage();      // Mesajı gönder
        }
    });
}

// --- SİSTEM DURUMU VE PORTFÖY KONTROLÜ ---
async function checkSystemStatus() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/status`);
        if (res.ok) {
            const data = await res.json();
            
            // Sol menüdeki ışığı güncelle
            updateSidebarStatus("loaded", data.position_count, data.active_portfolio);
            
            // Eğer portföy yüklüyse ve ekranda henüz seçim butonları yoksa getir
            if (data.portfolio_loaded) {
                const buttonsExist = document.getElementById('portfolio-buttons');
                if (!buttonsExist && isWelcomeScreenVisible) {
                    fetchAndShowPortfolios();
                }
            }
        } else {
             updateSidebarStatus("demo", 0);
        }
    } catch (e) {
        // Backend kapalıysa sessizce "Bağlanıyor..." moduna geç
        updateSidebarStatus("connecting", 0);
    }
}

function updateSidebarStatus(state, count, activeName) {
    const statusRow = document.getElementById('portfolioStatusRow');
    const statusDot = document.getElementById('portfolioDot');
    const statusText = document.getElementById('portfolioText');

    if (!statusRow) return;
    statusRow.style.opacity = '1'; 

    if (state === "loaded") {
        // DURUM: YÜKLÜ (Mor/Yeşil)
        statusDot.style.background = '#8b5cf6'; 
        statusDot.style.boxShadow = '0 0 8px #8b5cf6';
        statusDot.classList.add('pulse-green');
        
        const countStr = new Intl.NumberFormat('tr-TR').format(count);
        const pName = activeName === "ALL" ? "Tümü" : (activeName || "Yüklü");
        
        statusText.innerHTML = `${pName} (${countStr})`;
        statusText.style.color = "#a78bfa";
        
    } else if (state === "connecting") {
        // DURUM: BAĞLANTI YOK (Gri)
        statusDot.style.background = '#64748b';
        statusDot.style.boxShadow = 'none';
        statusDot.classList.add('pulse-blue');
        statusText.innerHTML = "Bağlanıyor...";
        statusText.style.color = "#64748b";
        
    } else {
        // DURUM: BEKLİYOR (Sarı)
        statusDot.style.background = '#fbbf24';
        statusDot.style.boxShadow = 'none';
        statusDot.classList.remove('pulse-green');
        statusText.innerHTML = "Bekleniyor...";
        statusText.style.color = "#94a3b8";
    }
}

// --- PORTFÖY LİSTESİNİ GETİR VE GÖSTER ---
async function fetchAndShowPortfolios() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/portfolios`);
        const data = await res.json();
        
        const welcomeScreen = document.querySelector('.welcome-screen');
        if (!welcomeScreen) return;

        const oldContainer = document.getElementById('portfolio-buttons');
        if(oldContainer) oldContainer.remove();

        const container = document.createElement('div');
        container.id = 'portfolio-buttons';
        container.style.marginTop = "25px";
        container.innerHTML = `<p style="font-size:0.85rem; color:#94a3b8; margin-bottom:10px; border-top:1px solid rgba(255,255,255,0.1); padding-top:15px;">Çalışılacak portföyü seçiniz:</p>`;
        
        let buttonsHtml = `<div style="display:flex; gap:10px; flex-wrap:wrap; justify-content:center;">`;
        buttonsHtml += `<button onclick="selectPortfolio('ALL')" style="padding:8px 12px; background:#3b82f6; border:none; border-radius:6px; color:white; cursor:pointer; font-size:0.85rem;">Tüm Portföyler</button>`;
        
        data.portfolios.forEach(p => {
            if (p !== "Genel Portföy") {
                buttonsHtml += `<button onclick="selectPortfolio('${p}')" style="padding:8px 12px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); border-radius:6px; color:#e2e8f0; cursor:pointer; font-size:0.85rem;">${p}</button>`;
            }
        });
        buttonsHtml += `</div>`;
        
        container.innerHTML += buttonsHtml;
        welcomeScreen.appendChild(container);
    } catch(e) {}
}

async function selectPortfolio(name) {
    addMessage("user", `Seçim: <strong>${name}</strong>`);
    try {
        await fetch(`${API_BASE_URL}/api/set-portfolio`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ portfolio_name: name })
        });
        addMessage("ai", `✅ <strong>${name}</strong> aktif edildi.`);
        checkSystemStatus();
    } catch(e) {
        addMessage("ai", "⚠️ Seçim yapılamadı.");
    }
}

// --- DOSYA SEÇİMİ ---
if (fileInput) {
    fileInput.addEventListener('change', async function() {
        if (this.files.length > 0) {
            removeWelcomeScreen();
            const file = this.files[0];
            
            // PDF İSE -> AI ANALİZİ
            if (file.name.toLowerCase().endsWith('.pdf')) {
                uploadRealFile(file);
                return;
            }

            // EXCEL İSE -> PORTFÖY YENİLEME
            addMessage("user", `📎 Excel: <strong>${file.name}</strong>`);
            uploadLocalExcel();
        }
    });
}

// --- 1. EXCEL YÜKLEME FONKSİYONU (Hata Gösterimli) ---
async function uploadLocalExcel() {
    const loadingId = addMessage("ai", `
        <div style="display:flex; align-items:center; gap:10px;">
            <i class="fa-solid fa-rotate fa-spin" style="color:#3b82f6;"></i>
            <div><strong>Veriler Tazeleniyor...</strong><br><span style="font-size:0.8rem; color:#94a3b8;">Yerel dosya okunuyor.</span></div>
        </div>
    `);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/reload-local`, { method: 'POST' });
        const data = await response.json();
        
        document.getElementById(loadingId).remove();
        
        if (response.ok && data.status === 'ok') {
            addMessage("ai", `✅ <strong>Başarılı</strong><br>Portföy verileri güncellendi.`);
            fetchAndShowPortfolios(); 
            checkSystemStatus();
        } else {
            // KIRMIZI HATA KUTUSU
            addMessage("ai", `
                <div style="color:#ef4444; border:1px solid #ef4444; padding:12px; border-radius:8px; background:rgba(239,68,68,0.1);">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:5px;">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <strong>Yükleme Hatası</strong>
                    </div>
                    <div style="font-size:0.9rem; color:#fca5a5;">
                        ${data.message}
                    </div>
                </div>
            `);
        }
    } catch(e) { 
        document.getElementById(loadingId)?.remove();
        addMessage("ai", "⚠️ Sunucuya ulaşılamadı."); 
    }
}

// --- 2. PDF YÜKLEME VE SENARYO FONKSİYONU ---
async function uploadRealFile(file) {
    addMessage("user", `📎 Rapor: <strong>${file.name}</strong>`);
    const loadingId = addMessage("ai", `<div style="display:flex; align-items:center; gap:10px;"><i class="fa-solid fa-brain fa-pulse"></i> Rapor Okunuyor...</div>`);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/upload-doc`, { method: 'POST', body: formData });
        const data = await response.json();
        document.getElementById(loadingId).remove();
        
        if (data.status === 'ok') {
            let html = `<div style="margin-bottom:15px;">✅ <strong>Rapor Okundu.</strong><br><span style="font-size:0.9rem; color:#94a3b8;">Önerilen Senaryolar:</span></div>`;
            
            if (data.scenarios && data.scenarios.length > 0) {
                html += `<div class="scenario-list">`;
                data.scenarios.forEach(sc => {
                    const btnColor = sc.bps > 0 ? '#ef4444' : '#3b82f6';
                    
                    // Link
                    let pageLink = "";
                    if (sc.page_number && data.filename) {
                        const pageNum = sc.page_number.replace(/\D/g,''); 
                        const pdfUrl = `${API_BASE_URL}/files/${data.filename}#page=${pageNum}`;
                        pageLink = `<a href="${pdfUrl}" target="_blank" style="color:#fbbf24; text-decoration:underline; font-size:0.8rem; margin-left:5px;">Kaynak (${sc.page_number}) ↗</a>`;
                    }

                    const quoteHtml = sc.source_quote 
                        ? `<div style="margin-top:10px; padding:8px; background:rgba(0,0,0,0.2); border-left:3px solid #fbbf24; font-style:italic; color:#fbbf24; font-size:0.85rem;">"${sc.source_quote}" ${pageLink}</div>` 
                        : '';

                    // --- [DÜZELTME] GÜVENLİ İSİM OLUŞTURMA ---
                    // Eğer isimde ' varsa (örn: Fed'in), bunu kaçış karakteriyle düzeltiyoruz.
                    // Yoksa HTML bozulur ve buton çalışmaz.
                    const safeName = (sc.name || "Senaryo").replace(/'/g, "\\'");
                    // ------------------------------------------

                    html += `
                    <div class="scenario-card">
                        <div class="scenario-icon" style="background:${btnColor}20; color:${btnColor};"><i class="fa-solid fa-bolt"></i></div>
                        <div class="scenario-info">
                            <div class="scenario-title">${sc.name}</div>
                            <div class="scenario-desc">${sc.reason}</div>
                            ${quoteHtml}
                        </div>
                        <button onclick="triggerMacro('${safeName} (Rapor)', ${sc.bps})" style="background:${btnColor}; color:white; border:none; padding:8px 16px; border-radius:8px; font-weight:bold; cursor:pointer; font-size:0.9rem;">Simüle Et (${sc.bps} bps)</button>
                    </div>`;
                });
                html += `</div>`;
            }
            addMessage("ai", html);
        } else {
            // HATA MESAJI
             addMessage("ai", `
                <div style="color:#ef4444; border:1px solid #ef4444; padding:12px; border-radius:8px; background:rgba(239,68,68,0.1);">
                    ❌ <strong>Analiz Hatası</strong><br>${data.message}
                </div>
            `);
        }
    } catch(e) {
        document.getElementById(loadingId)?.remove();
        addMessage("ai", "⚠️ İletişim hatası.");
    }
}

// --- TETİKLEYİCİ VE MESAJLAR ---
function triggerMacro(scenarioName, bps) {
    removeWelcomeScreen();
    addMessage("user", `<strong>${scenarioName}</strong> senaryosu çalıştırılıyor...`);
    sendToBackend(`Makro senaryo (${scenarioName}): ${bps} bps şok uygula`);
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    removeWelcomeScreen();
    addMessage("user", text);
    userInput.value = '';
    userInput.style.height = 'auto';
    sendToBackend(text);
}

async function sendToBackend(commandText) {
    const loadingId = addMessage("ai", `<i class="fa-solid fa-brain fa-pulse"></i> Hesaplama yapılıyor...`);
    try {
        const res = await fetch(`${API_BASE_URL}/api/chat`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ question: commandText }) });
        const data = await res.json();
        document.getElementById(loadingId).remove();
        if(data.status === 'ok') {
            const msgId = addMessage("ai", data.reply);
            if (data.chart_data) renderChart(msgId, data.chart_data);
        } else { addMessage("ai", `⚠️ Hata: ${data.message || "Bilinmiyor"}`); }
    } catch(e) { 
        document.getElementById(loadingId)?.remove(); 
        addMessage("ai", "⚠️ Hata."); 
    }
}

function renderChart(containerId, chartData) {
    const div = document.getElementById(containerId).querySelector('.message-content');
    const canvas = document.createElement("div"); canvas.className = "chart-wrapper";
    const cid = "chart_" + Date.now(); canvas.innerHTML = `<canvas id="${cid}"></canvas>`; div.appendChild(canvas);
    const ctx = document.getElementById(cid).getContext('2d');
    const bg = chartData.values.map(v => v < 0 ? 'rgba(239,68,68,0.6)' : 'rgba(16,185,129,0.6)');
    new Chart(ctx, { type: 'bar', data: { labels: chartData.labels, datasets: [{ label: 'P&L', data: chartData.values, backgroundColor: bg }] }, options: { responsive: true, maintainAspectRatio: false, scales: { x: {display: false}, y: {beginAtZero: true} }, plugins: {legend: {display: false}} } });
}

function addMessage(sender, htmlContent) {
    const div = document.createElement('div'); div.className = `message ${sender}-message`;
    div.innerHTML = `<div class="message-content">${htmlContent}</div>`;
    const id = "msg_" + Date.now(); div.id = id;
    chatWindow.appendChild(div); chatWindow.scrollTop = chatWindow.scrollHeight;
    return id;
}

function removeWelcomeScreen() {
    if (isWelcomeScreenVisible) { document.querySelector('.welcome-screen').style.display = 'none'; isWelcomeScreenVisible = false; }
}

if (userInput) {
    userInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
}