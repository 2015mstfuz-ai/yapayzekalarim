# aıFDT — Proje Özeti

aıFDT, Windows üzerinde çalışan, konsol tabanlı yerel bir yapay zeka sohbet uygulamasıdır. Kullanıcı önce kısa ömürlü bir erişim kodu alır, sonra bu kodla sohbete girer. Cevaplar ücretsiz `g4f` kütüphanesi üzerinden üretilir; konuşma geçmişi JSON dosyasında tutulur.
---
## Ne işe yarar

İki ayrı programdan oluşur:

1. **API yöneticisi** (`apiyonetici.py`) — sohbete girmek için gereken yerel erişim kodunu üretir ve saklar.
2. **Sohbet programı** (`aiFDTdisetkilesim.py`) — kodu doğrular, ardından kullanıcıyla konuşur ve geçmişi hatırlar.

Her iki program da PyInstaller ile konsol `.exe` olarak paketlenmek üzere hazırlanmıştır (`apiyonetici.spec`, `aiFDTdisetkilesim.spec`).
---
## Çalışma akışı

1. Kullanıcı `apiyonetici` programını açar ve `Evet` yazarsa yeni bir kod üretilir.
2. Kod biçimi: 4 rastgele harf + 5 haneli sayı (örnek biçim: `AbCd12345`). Aynı kod daha önce kullanılmışsa yenisi üretilir.
3. Kod `api.json` içindeki `etkin` listesine, oluşturulma saatiyle birlikte yazılır.
4. Kullanıcı `aiFDTdisetkilesim` programını açar ve bu kodu girer.
5. Kod hâlâ etkinse sohbet başlar. `cikis` yazılınca döngü biter.
6. Her kullanıcı mesajı ve yapay zeka cevabı belleğe eklenir; sonraki turda tüm geçmiş modele gönderilir.
---
## API ömrü ve depolama

- Bir kod **60 dakika** geçerlidir.
- Süre dolunca kod `etkin` listesinden çıkarılıp `suresidolmus` listesine taşınır.
- Süresi dolmuş kayıtlar **en fazla 5** tutulur; sayı 6’ya ulaşınca en eski kayıt silinir.
- Dosya: `api.json`
  - `etkin`: geçerli kod ve `olusturma_zamani`
  - `suresidolmus`: eski kod ve `dolma_zamani`

Doğrulama yalnızca `etkin` listedeki kodlar için başarılı olur.
---
## Yapay zeka ve bellek

- Kütüphane: `g4f` (`pip install g4f` gerekir).
- Model: `g4f.models.gpt_4` (yorumda `gpt_35_turbo` alternatifi de not edilmiş).
- Mesaj biçimi: `{"role": "user" | "assistant", "content": "..."}`.
- Bellek dosyası kodda `ai_fdt_bellek.json` olarak aranır. Beklenen yapı `konusma_gecmisi` listesidir. Dosya yoksa, boşsa veya bozuksa boş listeyle devam edilir.
---
## Klasördeki dosyalar

| Dosya | Rol |
| --- | --- |
| `apiyonetici.py` | API |
| `aiFDTdisetkilesim.py` | Yapayzekanın ana beyni ve kullanıcı ile etkileşim kodları |
| `api.json` | API deposu |
| `aiFDTbellek.json` | Bellek dosyası (şu an `kullanici_bilgileri.ad` alanı var) |
| `apiyonetici.spec` | API yöneticisinin PyInstaller tanımı |
| `aiFDTdisetkilesim.spec` | Sohbet programının PyInstaller tanımı (`g4f` gizli import) 
---
## Dikkat edilmesi gereken noktalar

- Sohbet programı `api_yonetici` modülünü import eder; dosya adı ise `apiyonetici.py`. Bu iki isim Python’da eşleşmez, bu yüzden program “dosya aynı klasörde olmalı” hatasıyla kapanabilir.
- Kod `ai_fdt_bellek.json` okur/yazar. Klasördeki bellek dosyasının adı `aiFDTbellek.json` ve içeriği konuşma geçmişi değil, kullanıcı adı kaydıdır. Sohbet bu dosyayı kullanmaz; kendi dosyasını ayrıca oluşturur.
- Erişim kodları yerel ve kısa ömürlüdür. Üçüncü taraf bir API anahtarı değildir; asıl model çağrısı `g4f` üzerinden yapılır.
