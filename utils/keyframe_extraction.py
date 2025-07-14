import os
import sys
import numpy as np
import cv2
import json
import concurrent.futures



# Get the list of videos in the data/videos directory
videos_list = sorted([f for f in os.listdir('data/videos') if f.endswith('.mp4')])

# Add TransNetV2 to your Python path
sys.path.append('models/TransNetV2/inference')

# Create output directory for keyframes
output_dir = "data/processed/keyframes"

from transnetv2 import TransNetV2

# The path to the video file
# video_name = "00001"
# video_path = f"data/videos/{video_name}.mp4"

# Initialize the TransNetV2 model
model = TransNetV2()


def extract_shots(video_path):
    """ TransNetV2 model to extract shots from a video
        Args: Video path
        Returns: list of scenes [(start_frame, end_frame), ...]
    """
    _, single_frame_predictions, _ = \
        model.predict_video(video_path)
    scenes = model.predictions_to_scenes(single_frame_predictions)
    return scenes


# Function to calculate frame quality
def calculate_frame_quality(frame):
    """Calculate frame quality based on sharpness and contrast"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0) # Reduce noise
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var() # Variance of Laplacian
    contrast = gray.std() 
    
    return sharpness + contrast * 0.5


def extract_keyframes(video_path, video_name, scenes):
    """ Extract keyframes based on shot quality
        Return video FPS, Duration, and keyframe
        start and end times.
    """
    # Open video to extract actual frames
    cap = cv2.VideoCapture(video_path)

    # Get the video FPS and Duration
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps
    
    shots_info = []

    # Extract best quality frame from each shot
    for i, (start_frame, end_frame) in enumerate(scenes):
        best_frame = None
        best_quality = 0
        best_frame_num = start_frame

        # Sample every 12th frame in the shot
        for frame_num in range(start_frame, end_frame, 12):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()

            if ret:
                # Find the best quality frame in the shot
                quality = calculate_frame_quality(frame)
                if quality > best_quality:
                    best_quality = quality
                    best_frame = frame.copy()
                    best_frame_num = frame_num

        if best_frame is not None:
            #Save the frame as an image
            filename = f"{video_name}_shot_{i}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, best_frame)
            print(f"Saved keyframe {i+1}/{len(scenes)}: {filename}")

            # Calculate times for the shot and keyframe
            start_time = start_frame / fps
            end_time = end_frame / fps
            keyframe_time = best_frame_num / fps

            # Save the Shot Information to later insert it to DB
            shots_info.append({
                "shot_name": f"shot_{i}",
                "start_time": start_time,
                "end_time": end_time,
                "keyframe_path": filepath,
                "keyframe_time": keyframe_time
            })

    cap.release()

    # Save video and shots info to JSON
    video_info = {
        "video_name": video_name,
        "fps": fps,
        "duration":duration,
        "shots": shots_info
    }
    # Save the JSON file to data/processed/video_shot_info
    output_json = f"data/processed/video_shot_info/{video_name}_shots.json"
    with open(output_json, 'w') as f:
        json.dump(video_info, f, indent=4)


for video_file in videos_list[0]:
    # Remove the .mp4 extension from the name
    video_name = video_file.split('.')[0]
    video_path = f"data/videos/{video_file}"
    print(f"Processing {video_file}...")
    scenes = extract_shots(video_path)
    extract_keyframes(video_path, video_name, scenes)


