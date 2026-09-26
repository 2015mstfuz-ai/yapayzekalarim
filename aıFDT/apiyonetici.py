import json
import random
from pathlib import Path
from datetime import datetime, timedelta

API_DOSYASI = Path("api.json")

def mevcut_apileri_yukle():
    """Dosyayı yükler. Yapı yoksa veya bozulmuşsa temiz şablonu hazırlar."""
    varsayilan_yapi = {"etkin": {}, "suresidolmus": {}}
    
    if not API_DOSYASI.exists() or API_DOSYASI.stat().st_size == 0:
        return varsayilan_yapi
        
    try:
        veri = json.loads(API_DOSYASI.read_text(encoding="utf-8"))
        if not isinstance(veri, dict) or "etkin" not in veri or "suresidolmus" not in veri:
            return varsayilan_yapi
        return veri
    except json.JSONDecodeError:
        return varsayilan_yapi

def sureleri_guncelle_ve_kaydet(mevcut_veri):
    """Süresi 60 dakikayı geçen API'leri suresidolmus sözlüğüne taşır ve limit kontrolü yapar."""
    simdi = datetime.now()
    silinecekler = []
    
    # 1. Aşama: Süresi dolan etkin API'leri tespit et (60 dakika)
    for anahtar, api_bilgisi in mevcut_veri["etkin"].items():
        olusturma_zamani_str = api_bilgisi["olusturma_zamani"]
        olusturma_zamani = datetime.fromisoformat(olusturma_zamani_str)
        
        if simdi - olusturma_zamani > timedelta(minutes=60):
            silinecekler.append(anahtar)
            
    # 2. Aşama: Süresi dolanları 'suresidolmus' alanına taşı
    for anahtar in silinecekler:
        api_kodu = mevcut_veri["etkin"][anahtar]["kod"]
        
        yeni_sd_anahtar = f"api_{len(mevcut_veri['suresidolmus']) + 1}"
        mevcut_veri["suresidolmus"][yeni_sd_anahtar] = {
            "kod": api_kodu,
            "dolma_zamani": simdi.isoformat()
        }
        del mevcut_veri["etkin"][anahtar]
        
    # 3. Aşama: Kapasite Kontrolü (6 veya daha fazla ise en eski olanı siler)
    while len(mevcut_veri["suresidolmus"]) >= 6:
        anahtarlar = list(mevcut_veri["suresidolmus"].keys())
        en_eski_anahtar = anahtarlar[0]
        del mevcut_veri["suresidolmus"][en_eski_anahtar]
        
    API_DOSYASI.write_text(json.dumps(mevcut_veri, indent=4), encoding="utf-8")
    return mevcut_veri

def api_gonder(yeni_api):
    """Yeni üretilen API'yi üretim saatiyle birlikte 'etkin' sözlüğüne ekler."""
    mevcut_veri = mevcut_apileri_yukle()
    mevcut_veri = sureleri_guncelle_ve_kaydet(mevcut_veri)
    
    yeni_anahtar = f"api_{len(mevcut_veri['etkin']) + 1}"
    mevcut_veri["etkin"][yeni_anahtar] = {
        "kod": yeni_api,
        "olusturma_zamani": datetime.now().isoformat()
    }
    API_DOSYASI.write_text(json.dumps(mevcut_veri, indent=4), encoding="utf-8")

def apikontrol(api):
    """API kodunun benzersizliğini denetler."""
    mevcut_veri = mevcut_apileri_yukle()
    mevcut_veri = sureleri_guncelle_ve_kaydet(mevcut_veri)
    
    etkin_kodlar = [bilgi["kod"] for bilgi in mevcut_veri["etkin"].values()]
    dolmus_kodlar = [bilgi["kod"] for bilgi in mevcut_veri["suresidolmus"].values()]
    
    return (api in etkin_kodlar) or (api in dolmus_kodlar)

def api_dogrula(girilen_api):
    """API etkinse True döner."""
    mevcut_veri = mevcut_apileri_yukle()
    mevcut_veri = sureleri_guncelle_ve_kaydet(mevcut_veri)
    
    etkin_kodlar = [bilgi["kod"] for bilgi in mevcut_veri["etkin"].values()]
    return girilen_api in etkin_kodlar

if __name__ == "__main__":
    mevcut_veri = mevcut_apileri_yukle()
    sureleri_guncelle_ve_kaydet(mevcut_veri)
    
    # Kullanıcı arayüz metinleri senin yazdığın orijinal Türkçe haline getirildi
    soru = input("API mı almak istiyorsunuz? Evet ise 'Evet' yazın. Hayır ise 'Hayır' yazın: ")
    if soru.strip().lower() == "evet":
        rastgele_api = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4)) + str(random.randint(10000, 99999))
        while apikontrol(rastgele_api):
            rastgele_api = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4)) + str(random.randint(10000, 99999))
        
        api_gonder(rastgele_api)
        print(f"Başarıyla yeni API oluşturuldu. AI'ye girebilirsiniz: {rastgele_api}")
    else:
        print("İşlem iptal edildi.")
