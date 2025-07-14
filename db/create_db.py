import sqlite3
import os

def create_database(db_path="db/video_analysis.db", schema_path="db/schema.sql"):
    
    # If DB already exists, remove it
    if os.path.exists(db_path):
        os.remove(db_path)

    with open(schema_path, "r") as f:
        schema = f.read()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    
    print(f"Database created at {db_path}")

if __name__ == "__main__":
    create_database()