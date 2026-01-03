#!/usr/bin/env python3
"""
Check database contents
"""

import sqlite3
import os
import sys

# Add backend path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'w2', 'sth-db-query', 'backend'))

from app.core.config import settings

def check_database():
    db_path = settings.database_url.replace('sqlite+aiosqlite:///', '')
    print('Database path:', db_path)
    print('Database exists:', os.path.exists(db_path))

    if not os.path.exists(db_path):
        print('Database file does not exist!')
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('Tables:', tables)

    # Check database connections
    cursor.execute('SELECT COUNT(*) FROM database_connections')
    count = cursor.fetchone()[0]
    print('Database connections count:', count)

    if count > 0:
        cursor.execute('SELECT id, name, url FROM database_connections')
        connections = cursor.fetchall()
        print('Connections:', connections)

    # Check metadata
    cursor.execute('SELECT COUNT(*) FROM database_metadata')
    meta_count = cursor.fetchone()[0]
    print('Metadata count:', meta_count)

    if meta_count > 0:
        cursor.execute('SELECT connection_id, object_type, object_name FROM database_metadata LIMIT 5')
        metadata = cursor.fetchall()
        print('Metadata samples:', metadata)

    conn.close()

if __name__ == "__main__":
    check_database()
