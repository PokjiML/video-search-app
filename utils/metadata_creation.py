import json
import os
from color_detection import get_dominant_color
from YOLO_object_detection import get_objects

# List of videos inside 'data/videos' folder
videos_list = sorted([f for f in os.listdir('data/videos') if f.endswith('.mp4')])


def create_metadata(video_name, shot_name, input_path):
    # Get dominant color and brightness
    color, brightness = get_dominant_color(input_path)

    # Load image for object detection
    objects = get_objects(input_path)

    # Prepare metadata dictionary
    metadata = {
        "video_id": video_name,
        "shot_name": shot_name,
        "keyframe_path": input_path,
        "dominant_color": color,
        "brightness": brightness,
        "detected_objects": objects
    }
    
    # Save to JSON
    output_path = f'data/processed/metadata/{shot_name}_{video_name}_metadata.json'
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=4)



### ONLY TAKE 5 VIDEOS FOR TESTING
for video_file in videos_list[100:]:
    video_name = video_file.split('.')[0]

    # Get all shots from the video
    keyframes = [f for f in os.listdir('data/processed/keyframes') if f.startswith(video_name)]

    for shot in keyframes:
        input_path = f'data/processed/keyframes/{shot}'
        shot_name = shot[6:] # Remove 'video_name_' prefix
        shot_name = shot_name.split('.')[0] # Remove file extension
        create_metadata(video_name, shot_name, input_path)
    
    print(f"Metadata created for all shots in {video_file}")