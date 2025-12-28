import os
import shutil
import sys
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import templates 

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from rhoova_ai_engine import RhoovaUltimateEngine

# --- 1. AYARLAR VE .ENV YÜKLEME ---
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print(f"⚠️  UYARI: API Key bulunamadı! Lütfen şu dosyayı kontrol edin: {env_path}")

# --- 2. FASTAPI KURULUMU ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("public_docs", exist_ok=True)
app.mount("/files", StaticFiles(directory="public_docs"), name="files")

engine = RhoovaUltimateEngine(openai_api_key=OPENAI_API_KEY)

class ChatRequest(BaseModel):
    question: str

class PortfolioSelectRequest(BaseModel):
    portfolio_name: str

# --- 5. ENDPOINTLER ---

@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "portfolio_loaded": engine.use_real_data,
        "position_count": len(engine.df) if engine.df is not None else 0,
        "active_portfolio": engine.active_portfolio
    }

@app.get("/api/portfolios")
async def get_portfolios():
    return {"portfolios": engine.get_portfolio_list()}

@app.post("/api/set-portfolio")
async def set_portfolio(req: PortfolioSelectRequest):
    engine.active_portfolio = req.portfolio_name
    return {"status": "ok"}

@app.post("/api/reload-local")
async def reload_local():
    success, msg = engine.reload_portfolio()
    if success:
        return {"status": "ok", "message": "Yenilendi"}
    else:
        return {"status": "error", "message": f"Yükleme Başarısız: {msg}"}

@app.post("/api/upload-doc")
async def upload_document(file: UploadFile = File(...)):
    print(f"📂 Dosya Yükleniyor: {file.filename}")
    file_location = f"public_docs/{file.filename}"
    
    with open(file_location, "wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)
    
    try:
        if file.filename.lower().endswith(".pdf"):
            success, msg = engine.ingest_pdf(file_location)
            if success:
                scenarios = engine.suggest_scenarios_from_pdf()
                return {"status": "ok", "message": msg, "scenarios": scenarios, "filename": file.filename}
            else:
                return {"status": "error", "message": msg}
        else:
            engine.reload_portfolio()
            if os.path.exists(file_location): os.remove(file_location)
            return {"status": "ok", "message": "Portföy verileri güncellendi."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/chat")
async def chat_with_agent(req: ChatRequest):
    """
    Kullanıcı mesajını alır ve OTONOM AJAN'a (run_agent_analysis) iletir.
    """
    
    # 1. Ajanı Çalıştır
    analysis_result = engine.run_agent_analysis(req.question)
    
    # Hata Kontrolü
    if analysis_result.get("status") == "error":
        return {"status": "error", "reply": f"Sistem Hatası: {analysis_result.get('message')}"}

    # DURUM A: Ajan Hesaplama Aracı (Tool) Kullandı
    if analysis_result.get("mode") == "function_call":
        data = analysis_result.get("data", {})
        
        details = data.get("details", [])
        summary = data.get("summary", {})
        
        chart_data = {
            "labels": [str(d['positionId']) for d in details], 
            "values": [d.get('change', 0) for d in details]
        }
        
        pnl_str = summary.get("pnl_str", "0")
        try:
            pnl_raw = float(str(summary.get("pnl_str", "0")).replace(",",""))
        except:
            pnl_raw = 0
            
        total_pv = summary.get("before", "0")
        
        # En büyük hareketi bul (Yorum için)
        top_pos = details[0] if details else {"positionId": "Yok", "change": 0}
        sign = "+" if top_pos.get('change', 0) > 0 else ""
        top_move = f"{top_pos.get('positionId')} ({sign}{top_pos.get('change', 0):,.0f} TL)"
        
        # Şok miktarını al
        shock_val = 0
        try:
            shock_val = data.get("shock_applied", {}).get("shockValues", [{}])[0].get("shockValue", 0)
        except: pass

        # --- YENİ EKLENTİ: PDF Açıklaması mı yoksa Standart Yorum mu? ---
        if data.get("ai_explanation"):
            # Eğer PDF analizinden gelen özel bir açıklama varsa onu kullan
            story = f"<strong>RAPOR ANALİZİ:</strong><br>{data.get('ai_explanation')}<br><hr style='border:0; border-top:1px solid rgba(255,255,255,0.1); margin:10px 0;'><strong>RİSK ETKİSİ:</strong><br>"
            story += engine.generate_market_commentary(shock_val, pnl_str, top_move, req.question)
        else:
            # Yoksa standart yorum üret
            story = engine.generate_market_commentary(shock_val, pnl_str, top_move, req.question)
        # ----------------------------------------------------------------

        # HTML Şablonunu Doldur
        reply_html = templates.generate_analysis_html(
            bps=shock_val, 
            portfolio_name=engine.active_portfolio,
            total_pv=total_pv, 
            pnl_str=pnl_str, 
            pnl_raw=pnl_raw,
            details=details, 
            story_title=f"OTONOM ANALİZ: {data.get('scenario')}", 
            story_text=story, 
            story_color="#8b5cf6"
        )
        
        return {"status": "ok", "reply": reply_html, "chart_data": chart_data}

    # DURUM B: Ajan Sohbet Etti / Doküman Okudu
    else:
        raw_answer = analysis_result.get("answer")
        
        if isinstance(raw_answer, dict):
            final_html = raw_answer.get("answer_html", str(raw_answer))
        else:
            final_html = str(raw_answer)

        source = engine.pdf_name or 'Genel Bilgi'
        if engine.pdf_name:
             pdf_url = f"http://127.0.0.1:8000/files/{engine.pdf_name}"
             source = f"<a href='{pdf_url}' target='_blank' style='color:#a78bfa; text-decoration:underline;'>{engine.pdf_name} ↗</a>"
        
        reply_html = templates.generate_ai_response_html(source, final_html)
        return {"status": "ok", "reply": reply_html}

if __name__ == "__main__":
    print("🔥 Rhoova Final Engine Başlatılıyor...")
    uvicorn.run(app, host="0.0.0.0", port=8000)