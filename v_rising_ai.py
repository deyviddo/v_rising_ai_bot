import discord
from discord.ext import commands
from google import genai  # Google'ın yepyeni, modern 2026 kütüphanesi
import os
from dotenv import load_dotenv

# V RİSİNG BOTU - MODERN ÇAĞ BAŞLIYOR

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not GEMINI_API_KEY or not DISCORD_TOKEN:
    raise ValueError("HATA: .env dosyasında anahtarlar bulunamadı! Lütfen kontrol et.")

# Yeni kütüphanede istemci (client) bu şekilde ayağa kaldırılır
client = genai.Client(api_key=GEMINI_API_KEY)
HAFIZA_DOSYASI = "v_rising_bot_hafizasi.txt"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    if bot.user:
        print(f"\n[GÜVENLİ AKTİF] Modern Bot başarıyla açıldı: {bot.user.name}")


@bot.command()
async def sor(ctx, *, kullanici_sorusu: str):
    gecici_mesaj = await ctx.send("Kan havuzundan bilgiler çekiliyor, beklemede kal...")

    oyun_bilgisi = ""
    if os.path.exists(HAFIZA_DOSYASI):
        with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
            oyun_bilgisi = f.read()

    sistem_talimati = (
        "Sen harika bir V Rising oyun uzmanı ve Discord rehberisin. "
        "Aşağıda sana oyuna ait canlı Wiki'den kazıdığımız gerçek verileri veriyorum. "
        "Kullanıcının sorusuna cevap verirken ÖNCELİKLE bu belgedeki bilgileri kullan.\n\n"
        f"=== KESİN OYUN BİLGİSİ VERİTABANI ===\n{oyun_bilgisi}"
    )

    try:
        # Yeni kütüphaneye uygun kusursuz model çağrısı
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=kullanici_sorusu,
            config={"system_instruction": sistem_talimati}
        )

        await gecici_mesaj.delete()

        cevap_metni = response.text
        # ZIRH: Eğer gelen cevap 2000 karakterden uzunsa parçalara bölerek gönder
        if len(cevap_metni) > 1900:
            # Metni 1900 karakterlik güvenli parçalara ayırıyoruz
            parcalar = [cevap_metni[i:i + 1900] for i in range(0, len(cevap_metni), 1900)]
            for parca in parcalar:
                await ctx.send(f"🧛‍♂️ **V Rising Oyuncusu:**\n\n{parca}")
        else:
            await ctx.send(f"🧛‍♂️ **V Rising Oyuncusu:**\n\n{cevap_metni}")

    except Exception as e:
        try:
            await gecici_mesaj.delete()
        except:
            pass
        await ctx.send(f"Bir hata oluştu kanka, büyü başarısız: {e}")


bot.run(DISCORD_TOKEN)