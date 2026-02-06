import psycopg2
import sys

print("Attempting connection to 127.0.0.1:5432...")
try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="sentience",
        user="sentience",
        password="sentience",
        port=5432,
        connect_timeout=3
    )
    print("SUCCESS: Connected!")
    conn.close()
except Exception as e:
    print(f"FAILURE: {e}")
