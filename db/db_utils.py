import sqlite3
from typing import List, Dict, Any, Optional

DB_PATH = 'db/video_analysis.db'

def get_connection(db_path: str = DB_PATH):
    """ Create and return a new database connectino """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Get dict like rows
    return conn

def get_all_videos() -> List[Dict[str, Any]]:
    """ Get all videos from the database """
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM videos")
        return [dict(row) for row in cur.fetchall()]
    
def get_video_by_id(video_id: str) -> Optional[Dict[str, Any]]:
    """ Fetch a single video by its ID """
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
        return [dict(row) for row in cur.fetchall()]
    
def get_shots_by_video(video_id: str) -> List[Dict[str, Any]]:
    """ Fetch all shots for a given video ID """
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM shots WHERE video_id = ? ORDER BY start_time", (video_id,))
        return [dict(row) for row in cur.fetchall()]

def get_shot_by_id(shot_id: str) -> Optional[Dict[str, Any]]:
    """ Fetch a single shot by its ID """
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM shots WHERE id = ?", (shot_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
def search_shots_by_object(obj: str) -> List[Dict[str, Any]]:
    """ Search for shots containing a specific object """
    query = "SELECT * FROM shots WHERE detected_objects LIKE ?"
    pattern = f'%"{obj}"%'
    with get_connection() as conn:
        cur = conn.execute(query, (pattern,))
        return [dict(row) for row in cur.fetchall()]
