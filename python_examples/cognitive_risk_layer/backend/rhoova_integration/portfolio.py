import json
import os
import sys
import pandas as pd
import numpy as np
import warnings
from dotenv import load_dotenv # Ortam değişkenleri için

# --- PATH AYARLARI ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

# .env dosyasını yükle (Bir üst klasörde olabilir)
# Eğer main.py çalışıyorsa zaten yüklüdür ama garanti olsun diye buraya da ekliyoruz.
env_path = os.path.join(os.path.dirname(CURRENT_DIR), '.env')
load_dotenv(env_path)

try:
    import tradefiles
    from positionfiles import bondpositions, irspositions, forwardpositions, swappositions, vanillaoptionpositions
    from taskfiles import bond_task, irs_task, forward_task, swap_task, vanillaoption_task
    from rhoova.Client import *
except ImportError as e:
    print(f"⚠️ Import Hatası: {e}")
    # Kritik kütüphane yoksa durdurma, belki sadece data check yapılıyordur
    pass

warnings.filterwarnings("ignore")

# --- API CONFİGURASYONU (.ENV'den OKUMA) ---
RHOOVA_KEY = os.getenv("RHOOVA_API_KEY")
RHOOVA_SECRET = os.getenv("RHOOVA_API_SECRET")

if not RHOOVA_KEY or not RHOOVA_SECRET:
    print("❌ HATA: Rhoova API anahtarları .env dosyasında bulunamadı!")
    # Hata vermemek için dummy config, ama çalışmayacaktır.
    config = ClientConfig("error", "error")
else:
    config = ClientConfig(RHOOVA_KEY, RHOOVA_SECRET)
    
api = Api(config)

def clean_column_names(df):
    """Excel kolon isimlerini standartlaştırır."""
    new_columns = {}
    for col in df.columns:
        clean_col = str(col).strip()
        lower_col = clean_col.lower()
        
        if lower_col in ['portfolio name', 'portfolioname', 'portfolio', 'fund', 'book', 'portfoy_adi']:
            new_columns[col] = 'portfolio_name'
        elif lower_col in ['settlement date', 'settlementdate', 'valör', 'valor', 'settlement_date']:
            new_columns[col] = 'settlementDate'
        elif lower_col in ['trade id', 'tradeid', 'id', 'trade_id', 'deal_no', 'dealno']:
            new_columns[col] = 'trade_id'
        elif lower_col in ['position id', 'positionid', 'position_id', 'pos_id']:
            new_columns[col] = 'position_id'
        elif lower_col in ['isin code', 'isincode', 'isin', 'code', 'securityid']:
            new_columns[col] = 'isin_code'
        else:
            new_columns[col] = clean_col
    df.rename(columns=new_columns, inplace=True)
    return df

def loadportfolio():
    print(f"📂 Veriler Yükleniyor... (Konum: {CURRENT_DIR})")

    # CONFIG
    configdirectory = os.path.join(CURRENT_DIR, "config")
    try:
        with open(os.path.join(configdirectory, "usd6m.json"), "r") as f: USD6M = json.load(f)
        with open(os.path.join(configdirectory, "try6m.json"), "r") as f: TRY6M = json.load(f)
        yielddata = pd.read_csv(os.path.join(CURRENT_DIR, "data/yielddata/yielddata.csv")).replace(np.nan, '', regex=True)
        marketdata = pd.read_csv(os.path.join(CURRENT_DIR, "data/marketdata/marketdata.csv")).replace(np.nan, '', regex=True)
        voldata = pd.read_csv(os.path.join(CURRENT_DIR, "data/volatilitydata/voldata.csv")).replace(np.nan, '', regex=True)
    except FileNotFoundError as e:
        print(f"❌ Veri Dosyası Eksik: {e}")
        return pd.DataFrame()

    # --- 1. DOSYALARI OKU ---
    positions_path = os.path.join(CURRENT_DIR, "positions.xlsx")
    portfolio_path = os.path.join(CURRENT_DIR, "portfolio.xlsx")
    
    trade_id_to_portfolio = {} 

    try:
        # A) POSITIONS (İŞLEMLER)
        df_pos = pd.read_excel(positions_path, engine='openpyxl')
        df_pos = clean_column_names(df_pos)
        
        if 'trade_id' not in df_pos.columns:
            if 'isin_code' in df_pos.columns: df_pos['trade_id'] = df_pos['isin_code']
            else: df_pos['trade_id'] = df_pos.index.astype(str)
            
        if 'settlementDate' not in df_pos.columns: 
            df_pos['settlementDate'] = "2024-01-28"

        # B) PORTFOLIO (TANIMLAR)
        if os.path.exists(portfolio_path):
            df_port = pd.read_excel(portfolio_path, engine='openpyxl')
            df_port = clean_column_names(df_port)
            
            # Eşleşme Anahtarı
            if 'position_id' not in df_port.columns and 'trade_id' in df_port.columns:
                df_port['position_id'] = df_port['trade_id']

            # --- C) KESİN EŞLEŞTİRME (INNER JOIN) ---
            if 'position_id' in df_port.columns and 'portfolio_name' in df_port.columns:
                df_pos['match_key'] = df_pos['trade_id'].astype(str).str.strip()
                df_port['match_key'] = df_port['position_id'].astype(str).str.strip()
                
                # SADECE İKİ DOSYADA DA OLANLARI AL (INNER JOIN)
                merged = pd.merge(df_pos, df_port[['match_key', 'portfolio_name']], on='match_key', how='inner')
                
                # Raporla
                print(f"📊 TOPLAM İŞLEM: {len(df_pos)}")
                print(f"✅ KABUL EDİLEN (Eşleşen): {len(merged)}")
                print(f"🗑️ REDDEDİLEN (Tanımsız): {len(df_pos) - len(merged)}")
                
                trade_id_to_portfolio = dict(zip(merged['trade_id'].astype(str).str.strip(), merged['portfolio_name']))
                positionslist = merged.drop(columns=['match_key'])
            else:
                print("❌ 'portfolio.xlsx' eksik kolon içeriyor.")
                return pd.DataFrame() # Hata varsa boş dön
        else:
            print("⚠️ 'portfolio.xlsx' bulunamadı. İşlem yapılamıyor.")
            return pd.DataFrame() # Dosya yoksa boş dön

    except Exception as e:
        print(f"❌ Dosya Hatası: {e}")
        return pd.DataFrame()

    # --- 2. TRADE SPEC HAZIRLIĞI ---
    def get_trade_spec(trade_list):
        details_dir = os.path.join(CURRENT_DIR, "positionsdetail/")
        pf = tradefiles.findFiles(strings=list(set(trade_list)), dir=details_dir, subDirs=True, fileContent=True, fileExtensions=False)
        spec={}
        for key, values in pf.items():
            wb = pd.read_excel(values)
            if "bondsdefinition" in values: spec[key] = bondpositions.bond_position_trade(key,wb)
            elif "irsdefinition" in values: spec[key] = irspositions.irs_position_trade(key,wb)
            elif "forwarddefinition" in values: spec[key] = forwardpositions.forward_position_trade(key,wb)
            elif "swapdefinition" in values: spec[key] = swappositions.swap_position_trade(key,wb)
            elif "vanillaoptiondefinition" in values: spec[key] = vanillaoptionpositions.option_position_trade(key,wb)
        return spec      

    # Arama anahtarları (Sadece filtrelenmiş listeden)
    search_keys = []
    if 'isin_code' in positionslist.columns: search_keys.extend(positionslist['isin_code'].dropna().astype(str).tolist())
    if 'trade_id' in positionslist.columns: search_keys.extend(positionslist['trade_id'].dropna().astype(str).tolist())
        
    trade_def = get_trade_spec(list(set(search_keys)))
    trades_list = []
    
    # --- 3. TASK OLUŞTURMA ---
    print("🔨 Görevler oluşturuluyor...")
    for index, row in positionslist.iterrows():
        code = row.get('isin_code')
        if not code: code = row.get('trade_id')
        
        position = trade_def.get(code)
        if not position and 'trade_id' in row: position = trade_def.get(row['trade_id'])

        if not position: continue
        
        try:
            p_type = position.get("type", "")
            if p_type in ["fixedRateBondDefinition", "floatingBondDefinition"]:  
                trades_list.append(bond_task.create_bond_task(row, position))
            elif p_type == "IRSDefinition":
                trades_list.append(irs_task.create_irs_task(row, position))
        except AttributeError:
            continue

    if not trades_list:
        print("⚠️ Filtreleme sonrası işlenecek uygun pozisyon kalmadı.")
        return pd.DataFrame()

    # --- 4. API CALL ---
    riskdata = {
      "id": "PORTFOLIO1", "name": "PORTFOLIO 1", "method": "cashflows", "forRisk": False,
      "valuationDate": "2021-01-28", "valuationCurrency": "TRY", "tasks": trades_list,
      "curves": [USD6M, TRY6M],
      "yieldData": yielddata.to_dict('records'),
      "marketData": marketdata.to_dict('records'),
      "volatilityData": voldata.to_dict('records'),
    }

    try:
        print(f"🚀 API İsteği Gönderiliyor ({len(trades_list)} filtrelenmiş işlem)...")
        res = api.createTask(CalculationType.PORTFOLIO, riskdata, True)
        
        if(res["result"]):
            result = json.loads(res["result"])
            cf_df = pd.DataFrame(result.get("cashflows"))
            
            if not cf_df.empty:
                # Sonuçları İsimlendir
                cf_df['clean_id'] = cf_df['positionId'].astype(str).str.strip()
                
                # Sadece eşleşenler gittiği için hepsi bulunmalı
                cf_df['portfolio_name'] = cf_df['clean_id'].map(trade_id_to_portfolio).fillna("Bilinmeyen")
                
                cf_df.drop(columns=['clean_id'], inplace=True)
                print(f"🎉 Başarılı. Toplam {len(cf_df)} nakit akışı üretildi.")
                return cf_df
            else:
                print("⚠️ API boş veri döndü.")
                return pd.DataFrame()
        else:
            print(f"❌ API Hatası: {res}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ İletişim Hatası: {e}")
        return pd.DataFrame()