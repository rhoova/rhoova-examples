import os
import sys
import pandas as pd
import numpy as np
import json
import re
import traceback

# --- 1. YAPAY ZEKA KÜTÜPHANELERİ VE HATA ÖNLEYİCİ ---
try:
    from langchain_openai import ChatOpenAI
    from langchain_community.document_loaders import PyPDFLoader
    from pypdf import PdfReader
    from langchain_core.tools import tool
    
    # LangChain versiyon uyumluluğu
    try:
        from langchain_core.pydantic_v1 import BaseModel, Field
    except ImportError:
        from pydantic import BaseModel, Field

    try:
        from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
    except ImportError:
        from langchain.schema import HumanMessage, SystemMessage, ToolMessage
    HAS_AI = True
except ImportError as e:
    HAS_AI = False
    print(f"⚠️ UYARI: AI Modülleri yüklenemedi. Hata: {e}")
    
    # --- SAHTE SINIFLAR (Kodun çökmemesi için) ---
    class BaseModel:
        pass
    
    def Field(description="", default=None):
        return None
    
    def tool(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

# --- 2. TOOL (ARAÇ) PARAMETRE ŞEMASI ---
class ShockInput(BaseModel):
    if HAS_AI:
        shock_bps: int = Field(description="Uygulanacak faiz şoku (Baz Puan/BPS cinsinden). Örn: 100, -50.")
        scenario_name: str = Field(description="Senaryonun kısa adı. Örn: 'Enflasyon Şoku', 'Faiz İndirimi'.", default="Analiz")
    else:
        shock_bps = 0
        scenario_name = ""

class RhoovaUltimateEngine:
    def __init__(self, openai_api_key):
        self.df = pd.DataFrame()
        self.use_real_data = False
        self.active_portfolio = "ALL"
        self.last_error = None
        self.pdf_content = ""
        self.pdf_name = ""
        self.last_ai_error = None 
        
        # Portföyü Yükle
        self.reload_portfolio()
        
        if HAS_AI and openai_api_key:
            try:
                # 1. LLM Başlat
                self.llm = ChatOpenAI(model="gpt-4o", temperature=0.5, openai_api_key=openai_api_key)
                
                # 2. Tool'ları Tanımla ve LLM'e Bağla (Bind)
                self.tools = [self.calculate_portfolio_shock]
                self.llm_with_tools = self.llm.bind_tools(self.tools)
            except Exception as e:
                print(f"AI Başlatma Hatası: {e}")
                self.llm = None
        else:
            self.llm = None

    # --- ÖNEMLİ: Frontend'in Beklediği Liste Fonksiyonu ---
    def get_portfolio_list(self):
        """Frontend'deki dropdown menüsünü doldurur."""
        if self.df is None or self.df.empty: return []
        if 'portfolio_name' not in self.df.columns: return ["Genel Portföy"]
        return sorted(self.df['portfolio_name'].astype(str).unique().tolist())

    # --- 3. FUNCTION CALLING TOOL (AJAN KULLANIMI İÇİN) ---
    @tool("calculate_portfolio_shock", args_schema=ShockInput)
    def calculate_portfolio_shock(self, shock_bps: int, scenario_name: str = "Otomatik Analiz"):
        """
        Portföy üzerinde finansal stres testi yapar.
        Kullanıcı 'faiz artarsa', 'şok uygula' dediğinde bu aracı kullan.
        """
        print(f"🤖 AJAN DEVREDE: Hesaplama Fonksiyonu Tetiklendi -> {shock_bps} bps")
        result = self.calculate_logic(shock_bps)
        return {
            "type": "scenario_result",
            "scenario": scenario_name,
            "shock_applied": {"method": "parallel", "shockValues": [{"tenor": "all", "shockValue": shock_bps}]},
            "summary": result["summary"],
            "details": result["details"]
        }

    # --- 4. AJAN BEYNİ (KARAR MEKANİZMASI) ---
    def run_agent_analysis(self, user_input: str):
        """
        Kullanıcı sorusunu alır, Tool mu yoksa RAG mı gerektiğine karar verir.
        """
        if not HAS_AI or not self.llm: 
            return {"status": "error", "message": "AI modülü yüklü değil veya API Key eksik."}

        try:
            # Sistem Mesajı (Prompt)
            sys_msg = f"Sen uzman bir Risk Yöneticisisin. Elinde '{self.pdf_name}' adlı bir rapor ve portföy hesaplama aracı var."
            messages = [SystemMessage(content=sys_msg), HumanMessage(content=user_input)]
            
            # LLM Karar Veriyor
            ai_response = self.llm_with_tools.invoke(messages)
            
            # Karar: Tool Çağırma mı?
            if ai_response.tool_calls:
                tool_call = ai_response.tool_calls[0]
                args = tool_call["args"]
                
                # Hesaplama Aracını Çalıştır
                result_data = self.calculate_logic(args.get('shock_bps', 0))
                
                formatted_data = {
                    "type": "scenario_result",
                    "scenario": args.get('scenario_name', 'Analiz'),
                    "shock_applied": {"method": "parallel", "shockValues": [{"tenor": "all", "shockValue": args.get('shock_bps', 0)}]},
                    "summary": result_data["summary"],
                    "details": result_data["details"]
                }
                return {"status": "success", "mode": "function_call", "data": formatted_data}
            
            # Karar: Doküman Analizi mi?
            if self.pdf_content:
                doc_result = self.query_and_generate_scenario(user_input)
                
                # --- KRİTİK DÜZELTME: PDF'ten senaryo çıktıysa hesapla ve grafik çizdir ---
                scenario = doc_result.get("scenario")
                if scenario and isinstance(scenario, dict) and scenario.get("bps", 0) != 0:
                    print(f"📄 PDF Senaryosu Algılandı: {scenario.get('bps')} bps")
                    
                    # 1. Hesapla
                    bps = scenario.get("bps")
                    calc_result = self.calculate_logic(bps)
                    
                    # 2. Grafik Verisi Olarak Paketle (Function Call gibi davran)
                    formatted_data = {
                        "type": "scenario_result",
                        "scenario": scenario.get("name", "Rapor Bazlı Analiz"),
                        "shock_applied": {"method": "parallel", "shockValues": [{"tenor": "all", "shockValue": bps}]},
                        "summary": calc_result["summary"],
                        "details": calc_result["details"],
                        # PDF açıklamasını da taşıyoruz
                        "ai_explanation": doc_result.get("answer_html")
                    }
                    
                    return {
                        "status": "success", 
                        "mode": "function_call", # Bu sayede main.py grafik çizecek
                        "data": formatted_data
                    }
                
                # Senaryo yoksa sadece metni dön
                return {
                    "status": "success",
                    "mode": "text", 
                    "answer": doc_result 
                }
            else:
                # Düz Sohbet
                return {"status": "success", "mode": "text", "answer": ai_response.content}
                
        except Exception as e:
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    # --- 5. HESAPLAMA MANTIĞI (Core Engine) ---
    def calculate_logic(self, bps, currency_filter="ALL"):
        if self.df is None or self.df.empty:
            return {"summary": {"pnl_str": "0", "before": "0"}, "details": []}
            
        df = self.df.copy()
        if self.active_portfolio != "ALL": df = df[df['portfolio_name'] == self.active_portfolio]
        if currency_filter != "ALL" and 'currency' in df.columns:
            df = df[df["currency"].astype(str).str.upper() == currency_filter]
        
        try: shock_rate = float(bps) / 10000.0
        except: shock_rate = 0
        
        # Duration veya Basit Yüzde hesabı
        if "termToMatByYear" in df.columns:
            df["change"] = df["cashflowPv"] * np.exp(-1 * shock_rate * df["termToMatByYear"]) - df["cashflowPv"]
            df["after_shock_pv"] = df["cashflowPv"] + df["change"]
        else:
            df["change"] = df["cashflowPv"] * (1 - shock_rate) - df["cashflowPv"]
            df["after_shock_pv"] = df["cashflowPv"] + df["change"]
        
        total_pnl = df["change"].sum()
        total_pv = df["cashflowPv"].sum()
        total_pv_after = df["after_shock_pv"].sum()
        
        grouped = df.groupby("positionId")[["cashflowPv", "after_shock_pv", "change"]].sum().reset_index()
        grouped["abs_change"] = grouped["change"].abs()
        details = grouped.sort_values(by="abs_change", ascending=False).head(10).to_dict(orient="records")
        
        return {
            "summary": {
                "before": f"{total_pv:,.0f}",
                "after": f"{total_pv_after:,.0f}",
                "pnl_str": f"{total_pnl:,.0f}",
                "pnl_raw": total_pnl,
                "Impact (P&L)": f"{total_pnl:,.0f}"
            },
            "details": details
        }

    # --- 6. PROFESYONEL PİYASA YORUMCUSU ---
    def generate_market_commentary(self, bps, pnl_str, top_move, user_query):
        """
        macro_agent.py içindeki 'Chief Risk Strategist' promptu ile güçlendirilmiş yorumcu.
        """
        if not HAS_AI or not self.llm: return f"Şok uygulandı: {bps}bps. Etki: {pnl_str}."
        
        # Sayısal veriyi metne döküyoruz
        context_data = f"""
        SENARYO/SORU: {user_query}
        UYGULANAN ŞOK: {bps} bps
        TOPLAM P&L ETKİSİ: {pnl_str}
        EN KRİTİK HAREKET (EN ÇOK DEĞİŞEN POZİSYON): {top_move}
        """

        # Macro Agent'tan alınan profesyonel prompt
        prompt = f"""
        Sen dünyanın önde gelen yatırım bankalarından birinde çalışan Kıdemli Piyasa Risk Stratejistisin (Chief Risk Strategist).
        
        GÖREVİN:
        Sana verilen portföy stres testi sonuçlarını ("DURUM") analiz etmek ve Yatırım Komitesi için kısa, çarpıcı ve profesyonel bir yorum yazmak.
        
        ANALİZ ÇERÇEVESİ:
        1. **Nedensellik:** Bu şok (bps hareketi) neden portföyü böyle etkiledi? (Duration, Convexity, Kur etkisi vb.)
        2. **Risk Uyarıları:** Bu senaryo gerçekleşirse likidite veya teminat (margin call) riski doğar mı?
        3. **Aksiyon:** Portföy yöneticisine ne önerirsin? (Hedge et, pozisyon azalt vb.)
        
        KURALLAR:
        - Asla "Ben bir yapay zekayım" deme.
        - Finansal jargon kullan (Mark-to-Market, DV01, Yield Curve Twist vb.) ama net ol.
        - Cevabı HTML formatında verme, sadece düz metin (paragraf) olarak ver. Backend bunu HTML'e çevirecek.
        - Maksimum 3-4 cümle ile vurucu bir özet yap.
        
        --------------------------------------------------
        DURUM (Sayısal Veriler):
        {context_data}
        --------------------------------------------------
        
        STRATEJİST GÖRÜŞÜ:
        """
        
        try: 
            return self.llm.invoke([SystemMessage(content=prompt)]).content
        except: 
            return "Yorum oluşturulamadı."

    # --- 7. PDF VE SENARYO YÖNETİMİ ---
    def ingest_pdf(self, file_path):
        if not HAS_AI: return False, "AI Modülü Eksik"
        print(f"📄 [AI] PDF İşleniyor: {file_path}")
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            if not pages: return False, "PDF boş."
            
            formatted_text = ""
            for i, page in enumerate(pages):
                formatted_text += f"\n--- SAYFA {i+1} ---\n{page.page_content}\n"
            
            if len(formatted_text.strip()) < 50:
                reader = PdfReader(file_path)
                formatted_text = "\n".join([f"\n--- SAYFA {i+1} ---\n{p.extract_text()}" for i, p in enumerate(reader.pages)])

            if len(formatted_text.strip()) < 50: return False, "Metin okunamadı."
            self.pdf_content = formatted_text[:60000] 
            self.pdf_name = os.path.basename(file_path)
            return True, "Rapor başarıyla okundu."
        except Exception as e: 
            self.last_ai_error = str(e)
            return False, f"Hata: {str(e)}"
    
    # --- SENARYO FONKSİYONU GÜNCELLENDİ (UZUN ALINTI MODU) ---
    def suggest_scenarios_from_pdf(self):
        """
        PDF yüklendiğinde otomatik olarak 3 senaryo önerir.
        """
        if not HAS_AI or not self.pdf_content: return []
        
        print("🧠 AI: PDF üzerinden senaryo üretiliyor...")
        prompt = f"""
        GÖREV: Bu finansal rapordan ({self.pdf_name}) en kritik 3 risk senaryosunu çıkar.
        
        ÖNEMLİ KURALLAR:
        1. "bps" (Baz Puan) değerini metindeki riskin ciddiyetine göre SEN BELİRLE.
           - Örneğin: Küçük riskler için 50-100, büyük krizler için 200-500 arası ver.
           - Faiz artışı/enflasyon riski için POZİTİF (+), Faiz indirimi/Resesyon için NEGATİF (-) değer kullan.
        2. ASLA bütün senaryolara 100 yazma. Metni analiz et ve farklılaştır.
        3. "source_quote" (Kanıt) alanı ÇOK ÖNEMLİDİR.
           - Rapordaki ilgili cümleyi **OLDUĞU GİBİ, KESMEDEN VE KISALTMADAN** al.
           - Eğer cümle kısaysa, bağlamı korumak için bir önceki veya bir sonraki cümleyi de ekle.
           - Yarım yamalak alıntılar yapma (Örn: "...faiz artabilir" YERİNE "Kurul, enflasyonist baskılar nedeniyle faiz artırımına gidebilir." yaz).
        
        RAPOR İÇERİĞİ (ÖZET):
        {self.pdf_content[:20000]}...
        
        ÇIKTI FORMATI (SADECE JSON LİSTESİ):
        [
          {{ "name": "Senaryo Adı", "bps": 250, "reason": "Gerekçe...", "source_quote": "Metinden kopyalanmış UZUN ve TAM cümle...", "page_number": "s. X" }},
          {{ "name": "Başka Senaryo", "bps": -150, "reason": "...", "source_quote": "Tam cümle...", "page_number": "..." }}
        ]
        """
        try:
            res = self.llm.invoke([SystemMessage(content=prompt)]).content
            
            # Markdown temizliği (```json ... ``` gibi blokları kaldırır)
            clean_res = res.replace("```json", "").replace("```", "").strip()
            
            # JSON Listesini Regex ile bul
            match = re.search(r'\[.*\]', clean_res, re.DOTALL)
            
            if match:
                return json.loads(match.group(0))
            else:
                return []
        except Exception as e:
            print(f"Senaryo Üretme Hatası: {e}")
            return []

    # --- 8. SORGU CEVAPLAMA YARDIMCILARI ---
    def _get_source_prompt_template(self):
        return """
        CEVAP FORMATI (HTML):
        <div class='ai-answer'>
            <p>...Cevap...</p>
            <div style="margin-top:15px; padding:12px; background:rgba(255,255,255,0.05); border-left:3px solid #fbbf24; border-radius:0 8px 8px 0;">
                <div style="font-size:0.75rem; color:#fbbf24; font-weight:bold; margin-bottom:4px;">🔍 KAYNAK (SAYFA X):</div>
                <div style="font-size:0.85rem; color:#cbd5e1; font-style:italic;">"...Alıntı..."</div>
            </div>
        </div>
        """

    def query_and_generate_scenario(self, question):
        if not HAS_AI: return {"answer_html": "AI modülü eksik.", "scenario": None}
        
        prompt = f"""
        Sen bir Finansal Risk Uzmanısın. Soru: "{question}"
        Rapor: "{self.pdf_name}"
        İçerik: {self.pdf_content[:30000]}...
        
        GÖREV:
        1. Soruyu cevapla ve rapordan **gerçek bir alıntı** yap.
        2. Alıntı yaparken cümlenin tamamını al, kesme.
        3. Eğer soruda bir riskten bahsediliyorsa bir senaryo önerisi (JSON) oluştur.
        
        ÇIKTI FORMATI (JSON):
        {{
            "answer_html": "...HTML formatında cevap...",
            "scenario": {{ "bps": 100, "name": "...", "reason": "..." }}
        }}
        
        {self._get_source_prompt_template()}
        """
        try:
            res = self.llm.invoke([SystemMessage(content=prompt)]).content
            clean_res = res.replace("```json", "").replace("```", "").strip()
            match = re.search(r'\{.*\}', clean_res, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                return {"answer_html": res, "scenario": None}
        except Exception as e:
            return {"answer_html": f"Analiz hatası: {str(e)}", "scenario": None}

    # --- 9. VERİ YÖNETİMİ ---
    def reload_portfolio(self):
        print("🔄 Motor: Portföy taranıyor...")
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            integration_path = os.path.join(current_dir, "rhoova_integration")
            if integration_path not in sys.path: sys.path.append(integration_path)
            
            try:
                import rhoova_integration.portfolio as user_portfolio
                import importlib
                importlib.reload(user_portfolio)
                real_df = user_portfolio.loadportfolio()
            except ImportError:
                print("⚠️ Entegrasyon modülü bulunamadı, Demo veri yükleniyor.")
                self.load_demo_data()
                return False, "Modül yok"

            if not real_df.empty:
                self.df = real_df
                if 'portfolio_name' not in self.df.columns: self.df['portfolio_name'] = 'Main Portfolio'
                self.use_real_data = True
                print(f"✅ Motor: {len(self.df)} kayıt yüklendi (Gerçek).")
                return True, f"{len(self.df)} işlem başarıyla yüklendi."
            else:
                self.load_demo_data()
                return False, "Boş veri"
        except Exception as e:
            self.last_error = str(e)
            self.use_real_data = False
            self.load_demo_data()
            return False, f"Hata: {str(e)}"

    def load_demo_data(self):
        data = { "positionId": ["DEMO_BOND_1", "DEMO_IRS_1"], "cashflowPv": [1000000, -500000], "termToMatByYear": [2.5, 5.0], "currency": ["TRY", "USD"], "portfolio_name": ["Demo"] }
        self.df = pd.DataFrame(data)