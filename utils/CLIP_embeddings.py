import os
import sys
import torch
import transformers
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel

# Check for CUDA availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Move model to GPU
model.to(device)

# Define keyframe path from video and shot names
videos_list = sorted([f for f in os.listdir('data/videos') if f.endswith('.mp4')])

# Directory containing keyframes
keyframes_dir = 'data/processed/keyframes'


# Load and preprocess image
def extract_clip_embeddings(shot_name):
    """ Arg: shot name video_name_shot_20.jpg string """
    image = Image.open(f'data/processed/keyframes/{shot_name}')
    inputs = processor(images=image, return_tensors="pt")

    inputs = inputs.to(device)

    with torch.no_grad():
        # Extract CLIP embeddings
        image_features = model.get_image_features(**inputs)
        # Normalize embeddings
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

    # Convert to numpy
    embeddings_np = image_features.cpu().numpy()

    # Define output path for embeddings
    output_path = f'data/processed/embeddings/{shot_name}_embeddings.npy'

    # Save embeddings
    np.save(output_path, embeddings_np)



### TAKE ONLY 5 F VIDEOS FOR NOW
for video_file in videos_list[100:]:
    video_name = video_file.split('.')[0]

    # Get all shots from the video
    keyframes = [f for f in os.listdir(keyframes_dir) if f.startswith(video_name)]

    for shot in keyframes:
        extract_clip_embeddings(shot)

    print(f"Extracted embeddings for shots in {video_name}")
        