
import requests
import time
import sys

# TODO: Update with your actual Worker URL
WORKER_URL = "https://sentience-sandbox.medhaaraj.workers.dev" 
BACKEND_URL = "http://localhost:8000/telemetry/ingest"

def poll_worker():
    print(f"Polling Sandbox at {WORKER_URL}...")
    try:
        # Fetch logs from Cloudflare
        resp = requests.get(WORKER_URL)
        if resp.status_code != 200:
            print(f"Worker Error: {resp.status_code} - {resp.text}")
            return

        data = resp.json()
        logs = data.get("logs", [])
        
        if not logs:
            print("No new logs.")
            return

        print(f"Received {len(logs)} logs. Ingesting...")
        
        # Ingest into Backend
        for log in logs:
            # Normalize log entry for ingest endpoint
            payload = {
                "timestamp": log["timestamp"],
                "user": log["user"],
                "domain": log["domain"],
                "method": log["method"],
                "status": log["status"],
                "bytes": log.get("bytes", 0)
            }
            
            try:
                ingest_resp = requests.post(BACKEND_URL, json=payload)
                if ingest_resp.status_code != 200:
                    print(f"  Ingest Failed: {ingest_resp.text}")
            except Exception as e:
                print(f"  Ingest Error: {e}")

        print(f"Processed {len(logs)} events.")

    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    # Valid URL set
    # if "YOUR_SUBDOMAIN" in WORKER_URL: ...
        
    while True:
        poll_worker()
        print("Sleeping 10s...")
        time.sleep(10)
