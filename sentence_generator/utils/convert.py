import json
import sqlite3
from settings import ISOCODES
import os

def json_to_sqlite(json_file, db_file, table_name):
    # Read JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create table
    if isinstance(data[0], dict):
        columns = ', '.join([f"{k} TEXT" for k in data[0].keys()])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
    else:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (value TEXT)")
    
    # Insert data
    if isinstance(data[0], dict):
        for item in data:
            placeholders = ', '.join(['?' for _ in item.values()])
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", list(item.values()))
    else:
        for item in data:
            cursor.execute(f"INSERT INTO {table_name} (value) VALUES (?)", (item,))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Data successfully converted from {json_file} to {db_file}")

def from_json(lang, filepath):
    json_file = filepath
    db_file = os.path.join("instance", ISOCODES[lang]+'.db')
    table_name = 'sentences'

    # Convert JSON to SQLite
    json_to_sqlite(json_file, db_file, table_name)
