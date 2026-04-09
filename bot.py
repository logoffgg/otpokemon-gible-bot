import asyncio
from playwright.async_api import async_playwright
import requests
import os
import re
import time

DISCORD_WEBHOOK = os.getenv("WEBHOOK")

sent_messages = set()

def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

async def run():
    while True:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu"
                    ]
                )

                page = await browser.new_page()
                await page.goto("https://otpokemon.com")
                await asyncio.sleep(5)

                print("🔥 Sniper active...")

                last_ping = 0

                while True:
                    current_time = time.time()

                    # 🟢 Heartbeat
                    if current_time - last_ping > 1800:
                        send("🟢 Bot online")
                        last_ping = current_time

                    # 🔥 Wait until feed has content
                    container = None
                    text = ""

                    for _ in range(10):
                        container = await page.query_selector(".div-happening")
                        if container:
                            text = await container.inner_text()
                            if text.strip():
                                break
                        await asyncio.sleep(1)

                    # 🎯 Process events
                    if container and text.strip():
                        lines = text.split("\n")
                        print("EVENTS:", lines)

                        for t in lines:
                            clean = re.sub(r'[^\w\s]', '', t.lower())

                            # 🔥 Gible
                            if "gible" in clean and "defeat" in clean:
                                if t not in sent_messages:
                                    sent_messages.add(t)
                                    print("🔥 DETECTED:", t)
                                    send(f"🔥 GIBLE: {t}")

                            # 🐣 Dungeon
                            if "easter" in clean and "finish" in clean:
                                if t not in sent_messages:
                                    sent_messages.add(t)
                                    print("🐣 DUNGEON:", t)
                                    send(f"🐣 DUNGEON: {t}")

                    await asyncio.sleep(2)

        except Exception as e:
            print("🔥 Browser crashed, restarting...", e)
            await asyncio.sleep(5)

asyncio.run(run())
