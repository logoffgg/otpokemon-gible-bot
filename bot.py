import requests
import time
import re
from bs4 import BeautifulSoup
import os

DISCORD_WEBHOOK = os.getenv("WEBHOOK")

sent_messages = set()
last_ping = 0

def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

print("🔥 Lightweight sniper active...")

while True:
    try:
        current_time = time.time()

        # 🟢 Heartbeat
        if current_time - last_ping > 1800:
            send("🟢 Bot online | Lightweight mode active")
            print("🟢 Heartbeat sent")
            last_ping = current_time

        # 🌐 Fetch page
        res = requests.get("https://otpokemon.com")
        soup = BeautifulSoup(res.text, "html.parser")

        all_texts = []

        # 🔥 Get all 5 happening boxes
        for i in range(1, 6):
            div = soup.select_one(f".div-happening-{i}")
            if div:
                lines = div.get_text("\n").split("\n")
                all_texts.extend(lines)

        print("EVENTS:", all_texts)

        for text in all_texts:
            clean = re.sub(r'[^\w\s]', '', text.lower()).strip()

            # 🔥 Gible
            if "gible" in clean and "defeat" in clean:
                if text not in sent_messages:
                    sent_messages.add(text)
                    print("🔥 DETECTED:", text)
                    send(f"🔥 GIBLE SNIPED: {text}")

            # 🐣 Easter Dungeon
            if "easter" in clean and "dungeon" in clean and "finish" in clean:
                if text not in sent_messages:
                    sent_messages.add(text)
                    print("🐣 DUNGEON:", text)
                    send(f"🐣 EASTER DUNGEON: {text}")

        time.sleep(2)

    except Exception as e:
        print("Error:", e)
        time.sleep(4)
