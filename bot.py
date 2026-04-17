import asyncio
from playwright.async_api import async_playwright
import requests
import os
import re
import time
import json
from collections import Counter

DISCORD_WEBHOOK = os.getenv("WEBHOOK")

sent_messages = set()
LOG_FILE = "spawns.json"

# ------------------ DISCORD ------------------
def send(msg):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except:
        pass

# ------------------ LOGGING ------------------
def load_logs():
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def log_spawn(location, text):
    logs = load_logs()

    logs.append({
        "location": location,
        "text": text,
        "time": time.time()
    })

    save_logs(logs)

# ------------------ PREDICTION ------------------
def predict_next():
    logs = load_logs()

    if len(logs) < 5:
        return ["?"]

    recent = logs[-50:]
    locations = [log["location"] for log in recent]

    count = Counter(locations)

    # Ensure all 15 locations exist
    for i in range(1, 16):
        loc = f"happening{i}"
        if loc not in count:
            count[loc] = 0

    sorted_locs = sorted(count.items(), key=lambda x: x[1])
    top3 = [loc.replace("happening", "") for loc, _ in sorted_locs[:3]]

    return top3

# ------------------ COOLDOWN ------------------
def get_ready_locations(cooldown=1200):
    logs = load_logs()
    now = time.time()

    last_seen = {}

    for log in logs:
        last_seen[log["location"]] = log["time"]

    ready = []

    for i in range(1, 16):
        loc = f"happening{i}"
        last_time = last_seen.get(loc, 0)

        if now - last_time > cooldown:
            ready.append(str(i))

    return ready

# ------------------ MAIN BOT ------------------
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

                # Wait for dynamic content
                await asyncio.sleep(3)

                print("🔥 Sniper system active (OTPokemon)...")

                last_ping = 0

                while True:
                    current_time = time.time()

                    # 🟢 HEARTBEAT + PREDICTION
                    if current_time - last_ping > 1800:
                        predicted = predict_next()
                        ready = get_ready_locations()

                        send(
                            f"🟢 Bot Online\n"
                            f"📊 Next likely caves: {', '.join(predicted)}\n"
                            f"⏳ Ready caves: {', '.join(ready)}"
                        )

                        last_ping = current_time

                    elements = await page.query_selector_all(".div-happening .happening")

                    for el in elements:
                        text = await el.inner_text()
                        if not text.strip():
                            continue

                        clean_text = text.lower()
                        key = re.sub(r'[^\w\s]', '', clean_text).strip()

                        element_id = await el.get_attribute("id")
                        location_number = element_id.replace("happening", "") if element_id else "?"

                        # Extract Pokémon name
                        bold = await el.query_selector("b")
                        pokemon = await bold.inner_text() if bold else ""

                        is_mundo_red = "mundo red" in clean_text

                        # 🔴 GIBLE DETECTION
                        if "gible" in pokemon.lower() and "defeated" in clean_text:
                            if key not in sent_messages:
                                sent_messages.add(key)

                                log_spawn(element_id, text)
                                predicted = predict_next()

                                print(f"🔥 GIBLE at {location_number}: {text}")

                                send(
                                    f"🔴 GIBLE FOUND\n"
                                    f"📍 Location: {location_number}\n"
                                    f"🌍 Server: {'Mundo Red' if is_mundo_red else 'Other'}\n\n"
                                    f"📊 Next likely: {', '.join(predicted)}\n"
                                    f"📜 {text}"
                                )

                        # 🐣 OPTIONAL EVENT
                        if "easter" in clean_text and "finish" in clean_text:
                            if key not in sent_messages:
                                sent_messages.add(key)
                                send(f"🐣 EASTER DUNGEON: {text}")

                    await asyncio.sleep(2)

        except Exception as e:
            print("🔥 Crash, restarting...", e)
            await asyncio.sleep(5)

asyncio.run(run())
