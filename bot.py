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
    while True:  # 🔁 auto-restart if browser crashes
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
                await page.goto("https://otpokemon.com", wait_until="networkidle")

                print("🔥 Sniper active...")

                # 🔥 Inject observer (real-time)
                await page.evaluate("""
                    window.gibleEvents = [];

                    const elements = document.querySelectorAll('.happening');

                    elements.forEach(el => {
                        // capture existing
                        if (el.innerText && el.innerText.trim()) {
                            window.gibleEvents.push(el.innerText);
                        }

                        // listen for changes
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

                    # 🟢 Heartbeat every 30 minutes
                    if current_time - last_ping > 1800:
                        send("🟢 Bot online | Gible sniper active")
                        last_ping = current_time

                    # 🔥 Get real-time events
                    events = await page.evaluate("window.gibleEvents")

                    # 🔁 FALLBACK: scan DOM directly (VERY IMPORTANT)
                    fallback_elements = await page.query_selector_all(".happening")
                    fallback_events = []
                    for el in fallback_elements:
                        text = await el.inner_text()
                        if text.strip():
                            fallback_events.append(text)

                    # merge both sources
                    all_events = list(set(events + fallback_events))

                    if all_events:
                        for event in all_events:
                            key = re.sub(r'[^\w\s]', '', event.lower()).strip()

                            # 🔥 Gible detection
                            if "gible" in key and "defeat" in key:
                                if key not in sent_messages:
                                    sent_messages.add(key)
                                    print("🔥 GIBLE:", event)
                                    send(f"🔥 GIBLE SNIPED: {event}")

                            # 🐣 Easter dungeon
                            if "easter" in key and "finish" in key:
                                if key not in sent_messages:
                                    sent_messages.add(key)
                                    print("🐣 DUNGEON:", event)
                                    send(f"🐣 EASTER DUNGEON: {event}")

                    # clear real-time queue
                    await page.evaluate("window.gibleEvents = []")

                    await asyncio.sleep(2)

        except Exception as e:
            print("🔥 Browser crashed, restarting...", e)
            await asyncio.sleep(5)


asyncio.run(run())
