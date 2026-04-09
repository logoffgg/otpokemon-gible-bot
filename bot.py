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
                await page.goto("https://otpokemon.com", wait_until="networkidle")

                print("🔥 Sniper active...")

                # 🔥 Inject observer (real-time events)
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

                    # 🔥 Get observer events
                    events = await page.evaluate("window.gibleEvents")

                    # 🔁 Fallback scan (important)
                    elements = await page.query_selector_all(".happening")

                    for el in elements:
                        text = await el.inner_text()
                        if not text.strip():
                            continue

                        key = re.sub(r'[^\w\s]', '', text.lower()).strip()

                        # 🔴 DETECT SERVER COLOR
                        is_red = False

                        # Try class-based detection
                        color_el = await el.query_selector("span, div")
                        if color_el:
                            class_name = await color_el.get_attribute("class") or ""
                            style = await color_el.get_attribute("style") or ""

                            # 🔴 Check class name
                            if "red" in class_name.lower():
                                is_red = True

                            # 🔴 Check inline style color (fallback)
                            if "rgb(255, 0, 0)" in style or "#ff0000" in style:
                                is_red = True

                        # 🔥 GIBLE RED ONLY
                        if is_red and "gible" in key and "defeat" in key:
                            if key not in sent_messages:
                                sent_messages.add(key)
                                print("🔴 GIBLE:", text)
                                send(f"🔴 GIBLE RED SERVER: {text}")

                        # 🐣 Easter dungeon (optional filter)
                        if "easter" in key and "finish" in key:
                            if key not in sent_messages:
                                sent_messages.add(key)
                                print("🐣 DUNGEON:", text)
                                send(f"🐣 EASTER DUNGEON: {text}")

                    # clear observer queue
                    await page.evaluate("window.gibleEvents = []")

                    await asyncio.sleep(2)

        except Exception as e:
            print("🔥 Browser crashed, restarting...", e)
            await asyncio.sleep(5)


asyncio.run(run())
