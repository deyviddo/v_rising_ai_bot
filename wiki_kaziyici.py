import requests
from bs4 import BeautifulSoup
import time

kategoriler = {
    "Bosslar": "https://v-rising.fandom.com/wiki/V_Blood",
    "Eşyalar": "https://v-rising.fandom.com/wiki/Items",
    "Silahlar": "https://v-rising.fandom.com/wiki/Weapons",
    "Yapılar": "https://v-rising.fandom.com/wiki/Structures",
    "Kan_Tipleri": "https://v-rising.fandom.com/wiki/Blood_Types"
}

dosya_adi = "v_rising_bot_hafizasi.txt"

print("V Rising Nihai Veri Çözücü Motor Başlatılıyor...")

session = requests.Session()

# Sıkıştırma (gzip, br) isteklerini headers'dan çıkarttık ki veri şifreli/bozuk gelmesin!
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive"
})

print("Güvenlik sistemi yumuşatılıyor...")
session.get("https://v-rising.fandom.com/wiki/V_Rising_Wiki")
time.sleep(2)

with open(dosya_adi, "w", encoding="utf-8") as dosya:
    for kategori_adi, hedef_link in kategoriler.items():
        print(f"\n[İSTEK] {kategori_adi} sayfası temiz metin olarak indiriliyor...")

        try:
            response = session.get(hedef_link)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                dosya.write(f"\n=== KATEGORİ: {kategori_adi.upper()} ===\n")

                # Fandom'ın yeni yapısı: İçerikler artık 'main' etiketinin veya 'mw-content-text' divinin içinde.
                icerik_alani = soup.find(["main", "div"], id=["content", "mw-content-text"])

                # Eğer özel alanı bulamazsa tüm sayfayı tara
                hedef_alan = icerik_alani if icerik_alani else soup

                metinler = hedef_alan.find_all(["p", "h2", "h3", "li"])

                eklenen_sayac = 0
                for metin in metinler:
                    temiz_metin = metin.text.strip()

                    # Gereksiz yan menü elemanlarını ve çok kısa çöp metinleri eliyoruz
                    if temiz_metin and len(temiz_metin) > 10 and not temiz_metin.startswith("V Rising Wiki"):
                        dosya.write(temiz_metin + "\n")
                        eklenen_sayac += 1

                if eklenen_sayac > 0:
                    print(f"-> [BAŞARILI] {kategori_adi} kategorisinden {eklenen_sayac} satır temiz veri kazındı.")
                else:
                    print(f"-> [UYARI] {kategori_adi} sayfasında anlamlı metin bulunamadı.")

            else:
                print(f"-> [REDDEDİLDİ] Kod: {response.status_code}")

        except Exception as e:
            print(f"Hata: {e}")

        print("Radar koruması için 3 saniye bekleniyor...")
        time.sleep(3)

print(f"\n[İŞLEM BİTTİ] Şimdi '{dosya_adi}' dosyasını aç, tamamen okunabilir Türkçe/İngilizce rehber olacak!")