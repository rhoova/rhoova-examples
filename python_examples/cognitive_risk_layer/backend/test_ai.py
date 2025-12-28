# test_ai.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. .env Okuma Testi
load_dotenv(".env")
key = os.getenv("OPENAI_API_KEY")

print("-" * 30)
if key:
    print(f"✅ Anahtar Bulundu: {key[:5]}...{key[-3:]}")
else:
    print("❌ HATA: .env dosyasından anahtar okunamadı!")
    exit()

# 2. Bağlantı Testi
print("🔄 OpenAI Bağlantısı deneniyor...")
try:
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=key)
    cevap = llm.invoke("Merhaba, test 1-2-3").content
    print(f"✅ BAŞARILI! Cevap: {cevap}")
except Exception as e:
    print(f"❌ BAĞLANTI HATASI:\n{e}")