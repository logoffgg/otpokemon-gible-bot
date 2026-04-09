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

                # 🔥 Inject real-time observer
                await page.evaluate("""
                    window.gibleEvents = [];

                    const target = document.querySelector('.div-happening');

                    const observer = new MutationObserver(mutations => {
                        mutations.forEach(mutation => {
                            mutation.addedNodes.forEach(node => {
                                if (node.innerText) {
                                    window.gibleEvents.push(node.innerText);
                                }
                            });
                        });
                    });

                    if (target) {
                        observer.observe(target, { childList: true, subtree: true });
                    }
                """)

                last_ping = 0

                while True:
                    current_time = time.time()

                    # 🟢 Heartbeat
                    if current_time - last_ping > 1800:
                        send("🟢 Bot online")
                        last_ping = current_time

                    # 🔥 Get live events
                    events = await page.evaluate("window.gibleEvents")

                    if events:
                        for event in events:
                            clean = re.sub(r'[^\w\s]', '', event.lower())

                            # 🔥 Gible detection
                            if "gible" in clean and "defeat" in clean:
                                if event not in sent_messages:
                                    sent_messages.add(event)
                                    print("🔥 DETECTED:", event)
                                    send(f"🔥 GIBLE: {event}")

                            # 🐣 Easter dungeon
                            if "easter" in clean and "finish" in clean:
                                if event not in sent_messages:
                                    sent_messages.add(event)
                                    print("🐣 DUNGEON:", event)
                                    send(f"🐣 DUNGEON: {event}")

                        # clear processed events
                        await page.evaluate("window.gibleEvents = []")

                    await asyncio.sleep(1)

        except Exception as e:
            print("🔥 Browser crashed, restarting...", e)
            await asyncio.sleep(5)

asyncio.run(run())
