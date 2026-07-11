import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

categories = {
    "Bosses": "https://v-rising.fandom.com/wiki/V_Blood",
    "Items": "https://v-rising.fandom.com/wiki/Items",
    "Weapons": "https://v-rising.fandom.com/wiki/Weapons",
    "Structures": "https://v-rising.fandom.com/wiki/Structures",
    "Blood_Types": "https://v-rising.fandom.com/wiki/Blood_Types"
}

output_file = "v_rising_bot_memory.txt"


def run_scraper():
    print(f"\n[SCRAPER] Extraction engine started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    })

    try:
        session.get("https://v-rising.fandom.com/wiki/V_Rising_Wiki")
        time.sleep(2)

        with open(output_file, "w", encoding="utf-8") as file:
            for category_name, target_link in categories.items():
                response = session.get(target_link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    file.write(f"\n=== CATEGORY: {category_name.upper()} ===\n")

                    content_area = soup.find(["main", "div"], id=["content", "mw-content-text"])
                    target_area = content_area if content_area else soup
                    parsed_elements = target_area.find_all(["p", "h2", "h3", "li"])

                    lines_scraped = 0
                    for element in parsed_elements:
                        clean_text = element.text.strip()
                        if clean_text and len(clean_text) > 10 and not clean_text.startswith("V Rising Wiki"):
                            file.write(clean_text + "\n")
                            lines_scraped += 1
                    print(f"-> [SUCCESS] Scraped {lines_scraped} lines from {category_name}.")
                time.sleep(2)
        print("[SCRAPER SUCCESS] Memory file updated successfully.")
    except Exception as e:
        print(f"[SCRAPER ERROR] Extraction failed: {e}")


if __name__ == "__main__":
    run_scraper()