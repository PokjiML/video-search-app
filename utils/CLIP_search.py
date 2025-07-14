import numpy as np
import torch
import faiss
from transformers import CLIPProcessor, CLIPModel
import os

def load_clip_model():
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    return model, processor, device

def encode_query(query, processor, model, device):
    """ Encode users query with CLIP embeddings"""
    with torch.no_grad():
        inputs = processor(text=[query], return_tensors="pt", padding=True).to(device)
        text_features = model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy().astype('float32')
    

def load_search_components():
    """Load CLIP model and FAISS index for search functionality"""
    # Load CLIP model
    model, processor, device = load_clip_model()
    
    # Load FAISS index and shot names
    faiss_index_path = 'db/faiss/faiss_clip.index'
    shot_names_path = 'db/faiss/shot_names.npy'
    
    if os.path.exists(faiss_index_path) and os.path.exists(shot_names_path):
        faiss_index = faiss.read_index(faiss_index_path)
        shot_names = np.load(shot_names_path)
        return model, processor, device, faiss_index, shot_names
    else:
        return model, processor, device, None, None


def search_clip_index(query_emb, faiss_index, shot_names, all_shots):
    """ Return the most similar videos_id and ordered shot list """
    D, I = faiss_index.search(query_emb, len(shot_names))
    
    # Create mapping from FAISS shot names to database shots
    # FAISS format: "00001_shot_0.jpg"
    # DB format: shot_name="shot_0", video_id="00001"
    shot_name_to_shot = {}
    for shot in all_shots:
        shot_name = shot.get('shot_name')  # e.g., "shot_0"
        video_id = shot.get('video_id')    # e.g., "00001"
        if shot_name and video_id:
            # Create the FAISS format key: "00001_shot_0.jpg"
            faiss_key = f"{video_id}_{shot_name}.jpg"
            shot_name_to_shot[faiss_key] = shot
    
    # Check how many shots match
    matching_shots = sum(1 for name in shot_names if name in shot_name_to_shot)
    print(f"Matching shots: {matching_shots} out of {len(shot_names)}")
    
    # Create shot index to video mapping
    shot_to_video = {}
    for idx in range(len(shot_names)):
        shot_name = shot_names[idx]  # e.g., "00001_shot_0.jpg"
        shot_data = shot_name_to_shot.get(shot_name)
        if shot_data and 'video_id' in shot_data:
            shot_to_video[idx] = shot_data['video_id']
        else:
            print(f"Warning: No shot data found for shot_name: {shot_name}")
    
    seen_videos = set()
    ordered_video_ids = []
    ordered_shots = []
    
    for idx in I[0]:
        video_id = shot_to_video.get(idx)
        shot_name = shot_names[idx]
        shot_data = shot_name_to_shot.get(shot_name)
        
        if video_id and video_id not in seen_videos and shot_data:
            ordered_video_ids.append(video_id)
            ordered_shots.append(shot_data)
            seen_videos.add(video_id)
            
    print(f"Final results: {len(ordered_video_ids)} videos, {len(ordered_shots)} shots")
    return ordered_video_ids, ordered_shots