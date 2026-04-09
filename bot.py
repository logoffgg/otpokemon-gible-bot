import asyncio
from playwright.async_api import async_playwright
import requests
import os
import re
import time

DISCORD_WEBHOOK = os.getenv("WEBHOOK")

sent_messages = set()

def send_to_discord(message):
    requests.post(DISCORD_WEBHOOK, json={"content": f"🔥 GIBLE SNIPED: {message}"})

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()

        await page.goto("https://otpokemon.com")

        print("🔥 Sniper active...")

        last_ping = 0

        while True:
            try:
                current_time = time.time()

                # 🟢 Heartbeat every 30 minutes
                if current_time - last_ping > 1800:
                    requests.post(DISCORD_WEBHOOK, json={
                        "content": "🟢 Bot online | Monitoring Gible Cave | No crashes detected"
                    })
                    print("🟢 Heartbeat sent")
                    last_ping = current_time

                all_texts = []

                # 🔥 Loop through ALL happening boxes (1–5)
                for i in range(1, 6):
                    selector = f".div-happening-{i}"
                    container = await page.query_selector(selector)

                    if container:
                        text = await container.inner_text()
                        lines = text.split("\n")
                        all_texts.extend(lines)

                # 🎯 Process all events
                for text in all_texts:
                    clean = re.sub(r'[^\w\s]', '', text.lower())

                    if "defeated" in clean and "gible" in clean:
                        if text not in sent_messages:
                            sent_messages.add(text)
                            print("🔥 DETECTED:", text)
                            send_to_discord(text)

                await asyncio.sleep(1)

            except Exception as e:
                print("Error:", e)
                await asyncio.sleep(3)

asyncio.run(run())
