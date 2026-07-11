import os
import discord
from discord.ext import commands, tasks
from google import genai
from dotenv import load_dotenv
import subprocess
from datetime import datetime

# V RISING DISCORD BOT - SUBPROCESS AUTOMATION VERSION

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not GEMINI_API_KEY or not DISCORD_TOKEN:
    raise ValueError("ERROR: API keys not found in .env file! Please check your configurations.")

client = genai.Client(api_key=GEMINI_API_KEY)
MEMORY_FILE = "v_rising_bot_hafizasi.txt"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# --- BACKGROUND SCRAPER TRIGGER TASK ---
@tasks.loop(hours=24)
async def auto_trigger_scraper():
    print(f"\n[AUTOMATION] Triggering external wiki_scraper.py at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    try:
        subprocess.Popen(["python", "wiki_scraper.py"])
        print("[AUTOMATION SUCCESS] wiki_scraper.py successfully launched in the background.")
    except Exception as e:
        print(f"[AUTOMATION ERROR] Could not trigger scraper file: {e}")


@auto_trigger_scraper.before_loop
async def before_scraper_loop():
    await bot.wait_until_ready()


# --- BOT EVENTS & COMMANDS ---
@bot.event
async def on_ready():
    if bot.user:
        print(f"\n[SECURE ACTIVE] Bot is listening to Discord: {bot.user.name}")
        if not auto_trigger_scraper.is_running():
            auto_trigger_scraper.start()


@bot.command()
async def ask(ctx, *, user_question: str):
    temporary_message = await ctx.send("Extracting knowledge from the blood pool, please stand by...")

    game_knowledge = ""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            game_knowledge = f.read()

    system_instruction = (
        "You are the ultimate expert V Rising game specialist, PvP champion, and a helpful Discord guide. "
        "Below is the authentic real-time data scraped from the official game Wiki (use it for exact stats, boss locations, craft recipes, and items).\n\n"
        f"=== OFFICIAL WIKI DATABASE ===\n{game_knowledge}\n\n"
        "INSTRUCTIONS FOR ANSWERING:\n"
        "1. For specific queries like boss health, drop rates, or crafting ingredients, strictly use the OFFICIAL WIKI DATABASE provided above.\n"
        "2. For tactical queries, boss fight strategies, PvP builds, weapon combos, or base layouts, combine the Wiki data with your deep, advanced AI knowledge of V Rising mechanics.\n"
        "3. If a question cannot be answered using the Wiki database, use your general knowledge to provide an extensive, strategic answer.\n"
        "4. LANGUAGE RULE: Always respond in the exact same language that the user used to ask the question. If the question is in Turkish, respond in Turkish. If it is in English, respond in English. Keep the tone helpful and legendary."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_question,
            config={"system_instruction": system_instruction}
        )

        await temporary_message.delete()
        response_text = response.text

        if len(response_text) > 1900:
            chunks = [response_text[i:i + 1900] for i in range(0, len(response_text), 1900)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response_text)

    except Exception as e:
        try:
            await temporary_message.delete()
        except:
            pass
        await ctx.send(f"An error occurred, spell failed: {e}")


bot.run(DISCORD_TOKEN)