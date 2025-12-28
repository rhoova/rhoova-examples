# backend/debug_ai.py
import sys
import os

print(f"🐍 Python Çalışma Yolu: {sys.executable}")
print("-" * 30)

try:
    print("1️⃣  Test: pypdf...")
    from pypdf import PdfReader
    print("   ✅ Başarılı.")
except ImportError as e:
    print(f"   ❌ HATA: {e}")

try:
    print("\n2️⃣  Test: langchain-core (Pydantic)...")
    from langchain_core.pydantic_v1 import BaseModel, Field
    print("   ✅ Başarılı.")
except ImportError as e:
    print(f"   ❌ HATA: {e}")
    print("   💡 İPUCU: Pydantic versiyon uyumsuzluğu olabilir.")

try:
    print("\n3️⃣  Test: langchain-openai...")
    from langchain_openai import ChatOpenAI
    print("   ✅ Başarılı.")
except ImportError as e:
    print(f"   ❌ HATA: {e}")

try:
    print("\n4️⃣  Test: langchain-community...")
    from langchain_community.document_loaders import PyPDFLoader
    print("   ✅ Başarılı.")
except ImportError as e:
    print(f"   ❌ HATA: {e}")

print("-" * 30)
print("🏁 Test Bitti.")