from flask import Flask, jsonify, render_template_string
import json
import time
from collections import Counter

app = Flask(__name__)

LOG_FILE = "spawns.json"

# ------------------ LOAD LOGS ------------------
def load_logs():
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# ------------------ PREDICTION ------------------
def predict_next(logs):
    if len(logs) < 5:
        return ["?"]

    recent = logs[-50:]
    locations = [log["location"] for log in recent]

    count = Counter(locations)

    for i in range(1, 16):
        loc = f"happening{i}"
        if loc not in count:
            count[loc] = 0

    sorted_locs = sorted(count.items(), key=lambda x: x[1])
    return [loc.replace("happening", "") for loc, _ in sorted_locs[:3]]

# ------------------ COOLDOWN ------------------
def get_ready_locations(logs, cooldown=1200):
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

# ------------------ API ------------------
@app.route("/data")
def data():
    logs = load_logs()

    return jsonify({
        "logs": logs[-20:],
        "predicted": predict_next(logs),
        "ready": get_ready_locations(logs)
    })

# ------------------ UI ------------------
@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>🔥 Gible Dashboard</title>
    <style>
        body {
            font-family: Arial;
            background: #0f172a;
            color: white;
            padding: 20px;
        }
        h1 { color: #22c55e; }
        .box {
            background: #1e293b;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
        }
        .green { color: #22c55e; }
        .red { color: #ef4444; }
    </style>
</head>
<body>

<h1>🔥 Gible Sniper Dashboard</h1>

<div class="box">
    <h2>📊 Next Likely Caves</h2>
    <div id="predicted"></div>
</div>

<div class="box">
    <h2>⏳ Ready Caves</h2>
    <div id="ready"></div>
</div>

<div class="box">
    <h2>📜 Recent Spawns</h2>
    <div id="logs"></div>
</div>

<script>
async function loadData() {
    const res = await fetch('/data');
    const data = await res.json();

    document.getElementById('predicted').innerHTML =
        data.predicted.map(x => `<span class="green">#${x}</span>`).join(" ");

    document.getElementById('ready').innerHTML =
        data.ready.map(x => `<span class="red">#${x}</span>`).join(" ");

    document.getElementById('logs').innerHTML =
        data.logs.reverse().map(log =>
            `<div>#${log.location.replace("happening","")} - ${log.text}</div>`
        ).join("");
}

// Refresh every 5 seconds
setInterval(loadData, 5000);
loadData();
</script>

</body>
</html>
""")

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
