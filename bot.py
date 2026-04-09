import asyncio
from playwright.async_api import async_playwright
import requests

import os
DISCORD_WEBHOOK = os.getenv("WEBHOOK")

sent_messages = set()

def send_to_discord(message):
    data = {"content": f"🔥 GIBLE SNIPED: {message}"}
    requests.post(DISCORD_WEBHOOK, json=data)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://otpokemon.com")
        requests.post(DISCORD_WEBHOOK, json={"content": "🟢 Bot is now online"})

        print("🔥 Sniper active... waiting for Gible")

        # Inject observer into the page (REAL-TIME DOM listener)
        await page.evaluate("""
        window.gibleEvents = [];

        const target = document.querySelector('.div-happening');

        if (target) {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.innerText) {
                            window.gibleEvents.push(node.innerText);
                        }
                    });
                });
            });

            observer.observe(target, { childList: true, subtree: true });
        }
        """)

        while True:
            try:
                events = await page.evaluate("window.gibleEvents")

                if events:
                    for text in events:
                        text_lower = text.lower()

                        if "defeated a special" in text_lower and "Gible" in text_lower:
                            if text not in sent_messages:
                                sent_messages.add(text)
                                print("🔥 SNIPED:", text)
                                send_to_discord(text)

                    # Clear processed events
                    await page.evaluate("window.gibleEvents = []")

                await asyncio.sleep(0.5)  # ⚡ near real-time

            except Exception as e:
                print("Error:", e)
                await asyncio.sleep(2)

asyncio.run(run())
