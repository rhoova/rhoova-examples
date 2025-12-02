"""FastAPI application entry‑point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .websocket import router as ws_router
from fastapi.staticfiles import StaticFiles  # <--- Bu import gerekli
import os


app = FastAPI(title="Market Yield Dashboard API")

# CORS (broad for local testing; tighten for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.getcwd(), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Test HTML'i için basit bir route (Opsiyonel ama test için kolaylık sağlar)
from fastapi.responses import FileResponse
@app.get("/test")
async def read_test_html():
    return FileResponse('static/test.html')
    
    
# Basic root/health
@app.get("/")
def root():
    return {"message": "Market Yield Dashboard API", "try": ["/docs", "/health", "/ws (websocket)"]}

@app.get("/health")
def health():
    return {"ok": True}

# Include websocket routes
app.include_router(ws_router)
