"""
Database connection management
Handles PostgreSQL connections with retry logic
"""
import psycopg2
import time


def get_connection():
    """
    Establish connection to PostgreSQL database
    Retries until successful (for Docker startup timing)
    
    Returns:
        psycopg2 connection object
    """
    while True:
        try:
            return psycopg2.connect(
                host="db",  # Docker service name
                database="sentience",
                user="sentience",
                password="sentience"
            )
        except psycopg2.OperationalError:
            print("Waiting for database to be ready...")
            time.sleep(1)