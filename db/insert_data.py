import sqlite3
import json
import os

def add_video_from_json(
        db_path,
        video_shot_info_path,
        video_path,
        transcoded_path=None,
):
    """ Insert data to Videos table from JSON file"""
    # Load JSON info
    with open(video_shot_info_path, 'r') as f:
        info = json.load(f)
    video_id = info['video_name']
    fps = info['fps']
    duration = info['duration']

    # Connect to DB
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Insert into videos table
    cur.execute(
        """
        INSERT OR REPLACE INTO videos (video_id, video_path, transcoded_path, duration, fps)
        VALUES (?, ?, ?, ?, ?)
        """,
        (video_id, video_path, transcoded_path, duration, fps)
    )

    conn.commit()
    conn.close()

    

def add_shots_from_json(
        db_path, 
        video_shot_info_path,
        metadata_dir,
        ):
    """ Insert data to Shots table from JSON file"""
    
    # Load video and shot info (fps, duration, keyframe time, etc.)
    with open(video_shot_info_path, 'r') as f:
        info = json.load(f)
    video_id = info['video_name']
    shots = info['shots']

    # Connect to DB
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Insert shots from metadata JSON files
    for shot in shots:
        shot_name = shot['shot_name']
        metadata_path = os.path.join(metadata_dir,
                                     f"{shot_name}_{video_id}_metadata.json")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        cur.execute(
            """
            INSERT OR REPLACE INTO shots (
                shot_name, video_id, start_time, end_time, keyframe_time,
                keyframe_path, brightness, dominant_color, detected_objects
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (shot_name, video_id, shot['start_time'], shot['end_time'],
             shot['keyframe_time'], metadata['keyframe_path'],
             metadata['brightness'], metadata['dominant_color'],
             json.dumps(metadata.get('detected_objects', []))
            )
        )

    conn.commit()
    conn.close()
    



videos_list = sorted([f for f in os.listdir('data/videos') if f.endswith('.mp4')])

# USE ONLY THE FIRST 5 VIDEOS FOR NOW
for video_file in videos_list[15:]:
    video_name = video_file.split('.')[0]

    add_video_from_json(
    db_path='db/video_analysis.db',
    video_shot_info_path=f'data/processed/video_shot_info/{video_name}_shots.json',
    video_path=f'data/videos/{video_name}.mp4',
    transcoded_path=f'data/transcoded/{video_name}.mp4'
    )

    add_shots_from_json(
    db_path='db/video_analysis.db',
    video_shot_info_path=f'data/processed/video_shot_info/{video_name}_shots.json',
    metadata_dir='data/processed/metadata'
    )
