from ultralytics import YOLO
import torch
import cv2


model = YOLO('models/yolov8n.pt')

def get_objects(input_path):
    """Returns list of unique object classes detected
    in the keyframe """

    frame = cv2.imread(input_path)

    results = model(frame)
    detected_classes = set()

    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                class_name = model.names[int(box.cls)]
                detected_classes.add(class_name)

    return list(detected_classes)