# Video Search App

The app that lets the user extract important information for videos database.  
It extracts keyframes from every shot inside the video and analyse their contents.  
Based on the informations retrieved user can query and filter to find the specific fragment of the video from the whole database with high precision.

---

## Installation and set up

The project uses conda virtual environment for managing packages and libraries.

The environment can be installed with conda via `environment.yml` file with command:
```bash
conda env create -f environment.yml
```

In order to run, the user should first activate the environment with:

```bash
conda activate video_search_env
```

And then, in the main folder where the app.py is, run the following command:

```bash
streamlit run app.py
```

The application will launch on localhost afterwards.
Directory structure

Folders:

    /data → folder storing the video files, transcoded video files, and all the processed data (embeddings, keyframes, etc.)

    /db → folder contains python scripts which create and insert data into the sql db. There’s also a py script which creates a FAISS index for embeddings. The database schema and .db files are stored here.

    /models → folder storing pre trained YOLOv8 and TransNetV2 which are used for inference.

    /utils → folder which contains all the python scripts that detect keyframes and extract the information from the shots.

Files:

    dres_api.py - provides a class which handles login to the DRES system and submission of video_id, start_time, end_time.

    app.py - the most important script. It imports many other python files and extracted data. It uses Streamlit to generate the frontend and the logic of the website.

The app after running will automatically launch local host website.

There’s a Semantic Search section which lets the user search for the relevant fragment with text query (e.g. “Person with a red helmet riding on a bike in the forest”).

On the left there will also be three filters to choose from:

    Filter by detected objects in each shot

    Filter by overall brightness level

    Filter by dominant color in given shots

The videos will be sorted by the similarity.
The user can open and play the videos and search the shots with a labeled timestamp.


## Technical Report
### 1. Shot Detection

The TransNetV2 model was used for boundary shot detection.
Downloaded from the TransNetV2 repository.
Inference was performed locally with tensorflow.
### 2. Keyframe extraction

TransNetV2 detected the shot boundaries.
To select the best keyframe from every shot, CV2 was used.

The program goes through every 12th keyframe for efficiency. For every selected keyframe, it first applies Gaussian Blur to reduce noise, then the variance of Laplacian and contrast of the image are extracted. They were used to calculate the final quality score for each keyframe. The keyframe with the best quality was selected.

sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()  # Variance of Laplacian
contrast = gray.std()
score = sharpness + contrast * 0.05

### 3. Content Based
• CLIP

Every keyframe in the database has the extracted embeddings from CLIP.
They are later used in the web application where the user can write a query. Every keyframe is then sorted by similarity between the query and given images. The movies and shots are sorted according to the keyframes order.
• Brightness

The brightness of every shot is calculated from the HSV color range.
It takes the median of the Value channel from the keyframe and then it maps the brightness.

median_v = np.median(v_channel)
if median_v < 60: return "Dark"
elif median_v < 160: return "Medium"
else: return "Bright"

• Dominant color

To get the dominant color first the image is converted to HSV scale.
Then the image is flattened to 2D array and fed into KMeans algorithm which creates 5 clusters. Each cluster represents a dominant color with the HSV value. Then pick the cluster with the highest number of pixels inside it. Later the picked HSV dominant color is mapped into one of the names like “red”, “yellow”, etc.
If the color is too dark (low Saturation) then the image is mapped to black/gray/white.
• Detected objects (YOLO)

Yolov8n is used for object detection in each keyframe. The objects are saved in the database for every keyframe.
User can later filter out the videos and shots based on the detected object inside them.
### 4. Database

The application uses SQLite database. Inside it the paths to the videos and keyframes are stored alongside their metadata.

There are two main tables:

Videos table stores columns such as:

    video_id

    video_path

    transcoded_path

    duratio

    fps

Shots table stores columns such as:

    shot_id

    video_id

    shot_name

    start_time

    end_time

    keyframe_path

    keyframe_time

    brightness

    dominant_color

    detected_objects

For CLIP embeddings, they are stored as FAISS index which is a library especially designed for fast similarity search, especially on high dimensional vectors.
### 5. Frontend

The whole backend and frontend logic of the web app was built with python library Streamlit.

The whole page functionality is inside the file app.py which uses many functions from the utils folder, and dres_api.py.
### 6. API communication

The submission to DRES via API was achieved with the python requests library which directly sends information to the evaluation server after successful login.

The whole functionality is encapsulated inside the DresClient class inside dres_api.py which is imported by the app.py (the main program).
Demonstration

Fig 1. Screenshot from the Video Search System

The Video Search system lets users filter the videos by detected objects inside them, brightness and dominating color of keyframes inside the videos.
The user can also write the wanted video description and the videos will be ordered by the similarity to the given text.

There’s also the option to login to DRES and to submit the selected video with start time and end time in milliseconds.

