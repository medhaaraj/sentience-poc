
import requests
import time
import sys

# Configuration
SANDBOX_WORKER_URL = "https://sentience-sandbox.medhaaraj.workers.dev/telemetry/generate"
BACKEND_API_URL = "http://localhost:8000/telemetry/ingest"

def fetch_logs_from_sandbox(count=5):
    """
    Poll the Cloudflare Sandbox (via Worker) for synthetic logs
    """
    try:
        response = requests.post(
            SANDBOX_WORKER_URL,
            json={"count": count},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("logs", [])
        else:
            print(f"   Sandbox Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"   Connection Error (Sandbox): {e}")
        return []

def ingest_log_to_backend(log):
    """
    Send a single log entry to the Sentinel Backend
    """
    try:
        # Transform if necessary (our formats match currently)
        payload = {
            "user": log["user"],
            "domain": log["domain"]
        }
        
        response = requests.post(
            BACKEND_API_URL,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, str(e)

def run_consumer_loop(interval=5, batch_size=3):
    """
    Main loop: Poll -> Ingest -> Sleep
    """
    print(f"Starting Telemetry Consumer")
    print(f"   Sandbox: {SANDBOX_WORKER_URL}")
    print(f"   Backend: {BACKEND_API_URL}")
    print("-" * 50)

    total_ingested = 0
    
    try:
        while True:
            # 1. Fetch
            print(f"Polling Sandbox for {batch_size} logs...")
            logs = fetch_logs_from_sandbox(batch_size)
            
            if not logs:
                print("   No logs received (or error)")
                time.sleep(interval)
                continue
                
            # 2. Ingest
            success_count = 0
            for log in logs:
                success, result = ingest_log_to_backend(log)
                if success:
                    success_count += 1
                    # print(f"   ✓ {log['user']} -> {log['domain']} [{result.get('tool_id', 'unknown')}]")
                else:
                    print(f"   ✗ Failed: {result}")
            
            total_ingested += success_count
            print(f"   Processed batch: {success_count}/{len(logs)} successful (Total: {total_ingested})")
            
            # 3. Sleep
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nConsumer stopped by user")

if __name__ == "__main__":
    run_consumer_loop()
