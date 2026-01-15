
import psycopg2
from db import get_connection
from datetime import datetime

def check_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        print("--- DATABASE DIAGNOSTICS ---")
        
        # 1. Total Count
        cur.execute("SELECT COUNT(*) FROM ai_usage_events")
        print(f"Total Events: {cur.fetchone()[0]}")
        
        # 2. Time Range
        cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM ai_usage_events")
        min_ts, max_ts = cur.fetchone()
        print(f"Earliest Event: {min_ts}")
        print(f"Latest Event:   {max_ts}")
        
        # 3. Last 24h Count
        cur.execute("SELECT COUNT(*) FROM ai_usage_events WHERE timestamp >= NOW() - INTERVAL '24 hours'")
        recent_count = cur.fetchone()[0]
        print(f"Events Last 24h: {recent_count}")
        
        # 4. Check Timezone Config
        cur.execute("SHOW timezone")
        print(f"DB Timezone: {cur.fetchone()[0]}")
        print(f"Python Local Time: {datetime.now()}")
        print(f"Python UTC Time: {datetime.utcnow()}")

        # 5. Sample Rows (Last 5)
        cur.execute("SELECT timestamp, tool_id FROM ai_usage_events ORDER BY timestamp DESC LIMIT 5")
        print("\nLatest 5 Events:")
        for row in cur.fetchall():
            print(f"- {row[0]} | {row[1]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    check_db()
