"""
Reads one temperature entry at a time (rotating) from the JSON file,
publishes it to ntfy.sh via HTTPS POST.

Device subscribes at:  GET https://ntfy.sh/home-temperature-fitbit-data-7x3k
"""

import json
import os
import urllib.request

NTFY_TOPIC = "home-temperature-fitbit-data-7x3k"
NTFY_URL   = f"https://ntfy.sh/{NTFY_TOPIC}"
JSON_FILE  = "responses/daily-sleep-temperature-derivations.json"
STATE_FILE = "state.json"

with open(JSON_FILE) as f:
    data = json.load(f)

points = data["dataPoints"]
total  = len(points)

if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)
else:
    state = {"index": 0}

index = state["index"] % total
entry = points[index]["dailySleepTemperatureDerivations"]

payload = {
    "index":              index,
    "total":              total,
    "date":               f"{entry['date']['year']}-{entry['date']['month']:02d}-{entry['date']['day']:02d}",
    "nightlyTemperature": entry["nightlyTemperatureCelsius"],
    "baseline":           entry["baselineTemperatureCelsius"],
    "sigma":              entry["relativeNightlyStddev30dCelsius"]
}

message = json.dumps(payload).encode("utf-8")

print(f"Publishing entry {index + 1}/{total}  →  topic: {NTFY_TOPIC}")
print(f"Payload: {message.decode()}")

req = urllib.request.Request(
    url     = NTFY_URL,
    data    = message,
    headers = {
        "Content-Type": "application/json",
        "Title":        f"Temp entry {index + 1}/{total}",
    },
    method  = "POST"
)

with urllib.request.urlopen(req, timeout=10) as resp:
    print(f"Published. HTTP {resp.status}")

state["index"] = (index + 1) % total
with open(STATE_FILE, "w") as f:
    json.dump(state, f)

print(f"Next run will send entry {state['index'] + 1}/{total}")
print(f"Device polls: {NTFY_URL}/json")
