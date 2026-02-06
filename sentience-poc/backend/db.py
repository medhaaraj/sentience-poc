"""
Database connection management
Handles PostgreSQL connections with retry logic
"""
import psycopg2
import time


import os

def get_connection():
    """
    Establish connection to PostgreSQL database
    Retries until successful (for Docker startup timing)
    
    Returns:
        psycopg2 connection object
    """
    db_host = os.environ.get("DB_HOST", "127.0.0.1")
    db_name = os.environ.get("DB_NAME", "sentience")
    db_user = os.environ.get("DB_USER", "sentience")
    db_pass = os.environ.get("DB_PASS", "sentience")
    db_port = os.environ.get("DB_PORT", "5433")

    # If running inside docker (DB_HOST is 'db'), default port should be 5432
    if db_host == "db" and "DB_PORT" not in os.environ:
        db_port = "5432"

    while True:
        try:
            return psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_pass,
                port=db_port
            )
        except Exception as e:
            print(f"Waiting for database to be ready at {db_host}:{db_port}... Error: {e}")
            time.sleep(1)
