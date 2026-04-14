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
                await page.goto("https://www.ryudophoenix.com/gible-cave", wait_until="networkidle")

                print("🔥 Sniper active...")

                # Inject observer
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
                        send("🟢 Bot online | Red Gible sniper active")
                        last_ping = current_time

                    # Fallback scan
                    elements = await page.query_selector_all(".happening")

                    for el in elements:
                        text = await el.inner_text()
                        if not text.strip():
                            continue

                        clean_text = text.lower()
                        key = re.sub(r'[^\w\s]', '', clean_text).strip()

                        # 🔴 NEW LOGIC (TEXT-BASED)
                        is_mundo_red = "mundo red" in clean_text

                        # 🔥 GIBLE RED ONLY (based on text)
                        if is_mundo_red and "gible" in clean_text and "defeat" in clean_text:
                            if key not in sent_messages:
                                sent_messages.add(key)
                                print("🔴 GIBLE (MUNDO RED):", text)
                                send(f"🔴 GIBLE MUNDO RED: {text}")

                        # 🐣 Easter dungeon (optional)
                        if "easter" in clean_text and "finish" in clean_text:
                            if key not in sent_messages:
                                sent_messages.add(key)
                                print("🐣 DUNGEON:", text)
                                send(f"🐣 EASTER DUNGEON: {text}")

                    await asyncio.sleep(2)

        except Exception as e:
            print("🔥 Browser crashed, restarting...", e)
            await asyncio.sleep(5)


asyncio.run(run())
