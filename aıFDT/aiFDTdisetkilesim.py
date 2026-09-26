import json
import sys
from pathlib import Path
# Ücretsiz yapay zeka entegrasyonu için g4f kütüphanesini ekledik
try:
    import g4f
except ImportError:
    print("\n[!] Hata: Yapay zeka kütüphanesi eksik! Lütfen terminale 'pip install g4f' yazarak kurun.")
    input("\nKapatmak icin Enter'a basin...")
    sys.exit()

# api_yonetici.py dosyasini dinamik olarak bagliyoruz
try:
    api_yonetici = __import__("api_yonetici")
except ImportError:
    print("\n[!] Hata: 'api_yonetici.py' dosyasi bu kodla ayni klasorde olmalidir!")
    input("\nKapatmak icin Enter'a basin...")
    sys.exit()

BELLEK_DOSYASI = Path("ai_fdt_bellek.json")

def bellek_yukle():
    """Bellek dosyasini okur, dosya yoksa veya bossa bos mesaj listesi doner."""
    if not BELLEK_DOSYASI.exists() or BELLEK_DOSYASI.stat().st_size == 0:
        return {"konusma_gecmisi": []}
    try:
        veri = json.loads(BELLEK_DOSYASI.read_text(encoding="utf-8"))
        if "konusma_gecmisi" not in veri:
            return {"konusma_gecmisi": []}
        return veri
    except json.JSONDecodeError:
        return {"konusma_gecmisi": []}

def gecmise_ekle(rol, mesaj):
    """Kullanici veya AI mesajini bellek dosyasina ekler."""
    bellek = bellek_yukle()
    # Yapay zekanin anlayacagi formatta (role ve content) ekliyoruz
    bellek["konusma_gecmisi"].append({"role": rol, "content": mesaj})
    BELLEK_DOSYASI.write_text(json.dumps(bellek, indent=4), encoding="utf-8")

# --- ANA PROGRAM AKISI ---
girilen_api = input("aiFDT icin api yoneticisinden API aliniz. API anahtarini girin: ").strip()

# API Doğrulaması
if api_yonetici.api_dogrula(girilen_api):
    print("\n[+] API Dogrulamasi Basarili! Yapay Zeka Sistemine Giris Yapildi.")
    print("[*] Unutmayin, bu API anahtarinin omru 60 dakikadir.")
    print("[*] Sohbetten cikmak icin 'cikis' yazabilirsiniz.\n" + "="*50)
    
    # --- YAPAY ZEKA SOHBET DÖNGÜSÜ ---
    while True:
        kullanici_mesaji = input("\nSiz: ").strip()
        
        if kullanici_mesaji.lower() == "cikis":
            print("\nYapay zeka sohbeti sonlandirildi. Gorusmek uzere!")
            break
            
        if not kullanici_mesaji:
            continue
            
        # 1. Kullanicinin mesajini belleğe kaydet
        gecmise_ekle("user", kullanici_mesaji)
        
        # 2. Tüm konuşma geçmişini yapay zekaya gönder (Böylece geçmişi hatırlar)
        mevcut_bellek = bellek_yukle()
        
        print("Yapay Zeka dusunuyor...", end="\r")
        
        try:
            # Ücretsiz GPT-3.5/GPT-4 modellerini kullanarak cevap üretiyoruz
            cevap = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4, # veya g4f.models.gpt_35_turbo
                messages=mevcut_bellek["konusma_gecmisi"]
            )
            
            print(f"AI: {cevap}")
            
            # 3. Yapay zekanin cevabını da belleğe kaydet
            gecmise_ekle("assistant", cevap)
            
        except Exception as e:
            print(f"AI: Maalesef su an cevap uretirken bir hata olustu. (Hata: {e})")

else:
    print("\n[-] Hatali, gecersiz veya suresi dolmus API anahtari!")

input("\nProgrami sonlandirmak icin Enter'a basin...")
