#!/usr/bin/env python
"""
Script to wait for PostgreSQL database to be ready before starting the application.
This prevents connection errors when the app starts before the DB is fully initialized.
"""

import sys
import time
import psycopg2
from psycopg2 import OperationalError
import os

def wait_for_db(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    timeout: int = 30,
    interval: int = 2
) -> bool:
    """
    Wait for PostgreSQL database to be ready.
    
    Args:
        host: Database host
        port: Database port
        user: Database user
        password: Database password
        database: Database name
        timeout: Maximum time to wait in seconds
        interval: Time between connection attempts in seconds
    
    Returns:
        True if database is ready, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            connection = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=5
            )
            connection.close()
            print(f"✓ Database is ready! Connected successfully to {host}:{port}")
            return True
        except OperationalError as e:
            elapsed = time.time() - start_time
            print(f"✗ Database not ready yet ({elapsed:.1f}s elapsed) - {str(e)[:100]}")
            time.sleep(interval)
        except Exception as e:
            print(f"✗ Unexpected error: {str(e)}")
            time.sleep(interval)
    
    print(f"✗ Failed to connect to database after {timeout} seconds")
    return False

if __name__ == "__main__":
    # Get database configuration from environment variables
    db_host = os.getenv("POSTGRES_SERVER", "localhost")
    db_port = int(os.getenv("POSTGRES_PORT", "5432"))
    db_user = os.getenv("POSTGRES_USERNAME", "fastapi_user")
    db_password = os.getenv("POSTGRES_PASSWORD", "fastapi_password")
    db_name = os.getenv("POSTGRES_DATABASE", "fastapi_db")
    
    print(f"Waiting for database at {db_host}:{db_port}...")
    
    if wait_for_db(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    ):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
