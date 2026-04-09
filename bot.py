import asyncio
from playwright.async_api import async_playwright
import requests
import os
import re
import time

DISCORD_WEBHOOK = os.getenv("WEBHOOK")

sent_messages = set()

def send(msg):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except:
        pass

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

                # 🔥 Inject observer
                await page.evaluate("""
                    window.gibleEvents = [];

                    const elements = document.querySelectorAll('.happening');

                    elements.forEach(el => {
                        if (el.innerText && el.innerText.trim()) {
                            window.gibleEvents.push(el.innerText);
                        }

                        const observer = new MutationObserver(() => {
                            if (el.innerText && el.innerText.trim()) {
                                window.gibleEvents.push(el.innerText);
                            }
                        });

                        observer.observe(el, {
                            childList: true,
                            subtree: true,
                            characterData: true
                        });
                    });
                """)

                last_ping = 0

                while True:
                    current_time = time.time()

                    # 🟢 Heartbeat
                    if current_time - last_ping > 1800:
                        send("🟢 Bot online")
                        last_ping = current_time

                    # 🔥 Get events
                    events = await page.evaluate("window.gibleEvents")

                    if events:
                        for event in events:
                            key = re.sub(r'[^\w\s]', '', event.lower()).strip()

                            # 🔥 Gible
                            if "gible" in key and "defeat" in key:
                                if key not in sent_messages:
                                    sent_messages.add(key)
                                    print("🔥 DETECTED:", event)
                                    send(f"🔥 GIBLE: {event}")

                            # 🐣 Dungeon
                            if "easter" in key and "finish" in key:
                                if key not in sent_messages:
                                    sent_messages.add(key)
                                    print("🐣 DUNGEON:", event)
                                    send(f"🐣 DUNGEON: {event}")

                        # clear events
                        await page.evaluate("window.gibleEvents = []")

                    await asyncio.sleep(1)

        except Exception as e:
            print("🔥 Browser crashed, restarting...", e)
            await asyncio.sleep(5)

asyncio.run(run())
