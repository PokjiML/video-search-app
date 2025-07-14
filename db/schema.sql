-- videos table
CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    video_path TEXT NOT NULL,
    transcoded_path TEXT,
    duration REAL,
    fps REAL
);

-- shots table
CREATE TABLE IF NOT EXISTS shots (
    shot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shot_name = TEXT,
    video_id TEXT NOT NULL,
    start_time REAL, -- when the shot starts in seconds
    end_time REAL, -- when the shot ends in seconds
    keyframe_time REAL, -- exact time of the keyframe in seconds
    keyframe_path TEXT,
    brightness TEXT, -- 'dark', 'medium', 'bright'
    dominant_color TEXT,
    detected_objects TEXT, -- JSON array like ["person", "car"]
    FOREIGN KEY(video_id) REFERENCES videos(video_id)
);

-- CLIP embeddings
-- CLIP embeddings are stored in FAISS
