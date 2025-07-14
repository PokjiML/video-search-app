import streamlit as st
from db.db_utils import get_all_videos, get_video_by_id, get_shots_by_video, get_shot_by_id, search_shots_by_object
from utils.search_utils import gather_all_unique_objects
from utils.CLIP_search import load_search_components, load_clip_model, encode_query, search_clip_index
from collections import defaultdict
import dres_api

st.set_page_config(page_title="Video Search Dashboard", layout="wide")
st.title("🎬 Video Search Dashboard")

# Sidebar: Video selection and search
st.sidebar.header("Video Selection")

# Load CLIP model and FAISS index once
@st.cache_resource
def get_search_components():
    return load_search_components()

@st.cache_data
def load_videos():
    return get_all_videos()

@st.cache_data
def load_objects_and_shots(videos):
    return gather_all_unique_objects(videos, get_shots_by_video)

# Load all videos
videos = load_videos()

# Gather all unique detected objects, colors and brightness levels
object_options, all_shots = load_objects_and_shots(videos)

dominant_colors = sorted({shot.get('dominant_color') for shot in all_shots if shot.get('dominant_color')})
brightness_options = ['Dark', 'Medium', 'Light']

selected_objects = st.sidebar.multiselect("Filter videos by detected object", object_options)
selected_colors = st.sidebar.multiselect("Filter by dominant color", dominant_colors)
selected_brightness = st.sidebar.multiselect("Filter by brightness", brightness_options)

# CLIP semantic search
st.sidebar.header("Semantic Search")
user_query = st.sidebar.text_input("Search by description (CLIP)", "")

# Load search components
model, processor, device, faiss_index, shot_names = get_search_components()

# Determine video ordering based on CLIP search
if user_query and faiss_index is not None:
    # Encode the user query
    query_emb = encode_query(user_query, processor, model, device)

    # Search the FAISS index
    ordered_video_ids, ordered_shots = search_clip_index(query_emb, 
                                    faiss_index, shot_names, all_shots)
    
    # Create a video ordering map for display purposes
    video_order = {vid: idx for idx, vid in enumerate(ordered_video_ids)}

    # Reorder videos list for display
    videos_sorted = sorted(videos, key=lambda v: video_order.get(v['video_id'], float('inf')))

    st.sidebar.success(f"Found {len(ordered_video_ids)} relevant videos")
else:
    videos_sorted = videos
    ordered_video_ids = []
    ordered_shots = []



# Filter the videos based on selected filters
if selected_objects or selected_colors or selected_brightness:
    filtered_video_ids = set()

    # Group shots by video_id for efficient lookup
    shots_by_video = defaultdict(list)
    for shot in all_shots:
        shots_by_video[shot['video_id']].append(shot)

    for video in videos_sorted:
        video_id = video['video_id']
        shots = shots_by_video.get(video_id, [])

        # For each selected object, check if any shot in this video contains it
        object_match = True
        for obj in selected_objects:
            found = False
            for shot in shots:
                shot_objs = shot.get('detected_objects', [])
                normalized_objs = []
                if isinstance(shot_objs, str):
                    normalized_objs = [o.strip(" []'\"") for o in shot_objs.split(',') if o.strip(" []'\"")]
                elif isinstance(shot_objs, list):
                    for o in shot_objs:
                        if isinstance(o, str):
                            normalized_objs.extend([x.strip(" []'\"") for x in o.split(',') if x.strip(" []'\"")])
                if obj in normalized_objs:
                    found = True
                    break
            if not found:
                object_match = False
                break

        # For color
        color_match = (not selected_colors) or all(
            any(shot.get('dominant_color') == color for shot in shots)
            for color in selected_colors
        )

        # For brightness
        brightness_match = (not selected_brightness) or all(
            any(shot.get('brightness') == brightness for shot in shots)
            for brightness in selected_brightness
        )
        
        if object_match and color_match and brightness_match:
            filtered_video_ids.add(video_id)

    videos_to_show = [v for v in videos_sorted if v['video_id'] in filtered_video_ids]
else:
    videos_to_show = videos_sorted


# Main area: Show videos with thumbnails, play on click
if user_query and faiss_index is not None:
    st.subheader(f"Videos (ordered by similarity to: '{user_query}')")
else:
    st.subheader("Videos")

if videos_to_show:
    cols = st.columns(min(3, len(videos_to_show)))
    for idx, video in enumerate(videos_to_show):
        with cols[idx % len(cols)]:
            # Add similarity ranking if CLIP search was performed
            if user_query and video['video_id'] in ordered_video_ids:
                similarity_rank = ordered_video_ids.index(video['video_id']) + 1
                st.markdown(f"**Video: {video['video_id']}**  #{similarity_rank}")
            else:
                st.markdown(f"**Video: {video['video_id']}**")
            
            st.write(f"Duration: {int(video['duration'])}s")
            
            # Get shots for this video
            shots = [shot for shot in all_shots if shot['video_id'] == video['video_id']]
            
            # Order shots by CLIP relevance if search was performed, otherwise by time
            if user_query and ordered_shots:
                # Create a mapping of shot_name to CLIP relevance order
                clip_shot_order = {}
                for i, clip_shot in enumerate(ordered_shots):
                    if clip_shot and clip_shot.get('video_id') == video['video_id']:
                        clip_shot_order[clip_shot.get('shot_name')] = i
                
                # Sort shots by CLIP relevance first, then by time for shots not in CLIP results
                shots = sorted(shots, key=lambda s: (
                    clip_shot_order.get(s.get('shot_name'), float('inf')),  # CLIP order
                    s.get('start_time', 0)  # Fallback to time order
                ))
            else:
                # Default: order by time
                shots = sorted(shots, key=lambda s: s.get('start_time', 0))

            # Filter shots by selected criteria
            filtered_shots = []
            for shot in shots:
                shot_objs = shot.get('detected_objects', [])
                normalized_objs = []
                if isinstance(shot_objs, str):
                    normalized_objs = [o.strip(" []'\"") for o in shot_objs.split(',') if o.strip(" []'\"")]
                elif isinstance(shot_objs, list):
                    for o in shot_objs:
                        if isinstance(o, str):
                            normalized_objs.extend([x.strip(" []'\"") for x in o.split(',') if x.strip(" []'\"")])
                object_match = all(obj in normalized_objs for obj in selected_objects) if selected_objects else True

                # Color filter
                color_match = (not selected_colors) or (shot.get('dominant_color') in selected_colors)

                # Brightness filter
                brightness_match = (not selected_brightness) or (shot.get('brightness') in selected_brightness)
    
                # If all conditions match, add to filtered shots
                if object_match and color_match and brightness_match:
                    filtered_shots.append(shot)
            
            # Show keyframe of the most relevant shot (CLIP-ordered or first shot)
            keyframe_shot = filtered_shots[0] if filtered_shots else (shots[0] if shots else None)
            
            if keyframe_shot and keyframe_shot.get('keyframe_path'):
                caption = "Most relevant shot" if user_query else "Keyframe of first shot"
                st.image(keyframe_shot['keyframe_path'], caption=caption, use_column_width=True)
            
            with st.expander("Show video and all shots"):
                try:
                    st.video(video['transcoded_path'])
                except Exception:
                    st.info("Video file not found or cannot be displayed.")
                
                # Show all keyframes for this video
                st.markdown("**Keyframes:**")
                if filtered_shots:
                    for shot in filtered_shots:
                        if shot.get('keyframe_path'):
                            keyframe_time = shot.get('keyframe_time', None)
                            shot_caption = f"Shot {shot.get('shot_name', '')}"
                            
                            # Add relevance indicator for CLIP search
                            if user_query and shot.get('shot_name') in [s.get('shot_name') for s in ordered_shots if s and s.get('video_id') == video['video_id']]:
                                shot_caption += "Most important"
                            
                            if keyframe_time:
                                st.markdown(f"**{shot_caption}** at {keyframe_time}s")
                            
                            st.image(
                                shot['keyframe_path'],
                                caption=shot_caption,
                                use_column_width=True
                            )
else:
    if user_query:
        st.info("No videos found matching your search query and selected filters.")
    else:
        st.info("No videos found for the selected filter(s).")



# # DRES API integration

username = "Example_username"
password = "Example_password"

if "dres_client" not in st.session_state:
    st.session_state.dres_client = None

# Login form (run once)
if st.sidebar.button("Login to DRES"):
    client = dres_api.DresClient(username, password)
    success, msg = client.login()
    if success:
        st.session_state.dres_client = client
        st.sidebar.success(msg)
    else:
        st.sidebar.error(msg)


# Submission form
if st.session_state.dres_client:
    st.sidebar.header("DRES Submission")
    # Choose video and times for submission
    video_options = [v['video_id'] for v in videos]
    media_item_name = st.sidebar.selectbox("Select video for DRES submission", video_options)
    collection_name = "IVADL"  # Or make this selectable if needed
    start_time = st.sidebar.number_input("Start time (ms)", min_value=0, value=0)
    end_time = st.sidebar.number_input("End time (ms)", min_value=0, value=1000)
    if st.sidebar.button("Submit to DRES"):
        client = st.session_state.dres_client
        success, msg = client.submit(media_item_name, collection_name, start_time, end_time)
        if success:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)