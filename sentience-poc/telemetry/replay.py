import json
import time
import requests

URL = "http://localhost:8000/telemetry/ingest"

with open("swg_logs.jsonl") as f:
    for line in f:
        event = json.loads(line)
        r = requests.post(URL, json=event)
        print(event, "->", r.json())
        time.sleep(0.5)
