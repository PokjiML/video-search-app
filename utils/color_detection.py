import cv2
import numpy as np
from sklearn.cluster import KMeans


def get_dominant_color(image_path, k=5):
    """ Extract dominant colors using KMeans clustering"""
    # Load image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Convert to HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # Reshape for KMeans
    data = hsv_image.reshape((-1, 3))
    data = np.float32(data)

    # Apply KMeans
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(data)

    # Get HSV colors and convert back to RGB
    dominant_colors_hsv = kmeans.cluster_centers_

    # Get cluster sizes to find most dominant color
    labels = kmeans.labels_
    unique, counts = np.unique(labels, return_counts=True)
    most_dominant_idx = unique[np.argmax(counts)]
    most_dominant_hsv = dominant_colors_hsv[most_dominant_idx]

    # Map to basic color names and get brightness
    mapped_color = map_hsv_to_color(most_dominant_hsv)
    brightness = get_image_brightness(hsv_image)

    return mapped_color, brightness


def map_hsv_to_color(hsv):
    """ Map HSV color to basic color name """
    h, s, v = hsv
    
    # Handle achromatic colors first
    if s < 40:  # Very low saturation
        if v < 60:
            return "Black"
        elif v > 200:
            return "White"
        else:
            return "Gray"
    
    # Handle very dark colors
    if v < 40:
        return "Black"
    
    # Handle very bright, saturated colors
    if v > 220 and s < 60:
        return "White"
    
    # Color mapping
    if h < 10 or h > 170: 
        return "Red"
    elif 10 <= h < 22:  
        return "Orange"  
    elif 22 <= h < 38:  
        return "Yellow"
    elif 38 <= h < 85:  
        return "Green"
    elif 85 <= h < 128:  
        return "Blue"
    elif 128 <= h < 145:  
        return "Purple"
    else:  
        return "Pink"
    

def get_image_brightness(hsv_image):
    """ Compute overall image brightness from mean V channel."""
    v_channel = hsv_image[:, :, 2]
    median_v = np.median(v_channel)

    if median_v < 60:
        return "Dark"
    elif median_v < 160:
        return "Medium"
    else:
        return "Bright"
