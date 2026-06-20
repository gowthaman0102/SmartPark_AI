from ultralytics import YOLO
import cv2

print("SMARTPARK YOLO DETECTOR LOADED")

import streamlit as st

@st.cache_resource
def get_yolo_model():
    return YOLO("yolov8n.pt")

VEHICLE_CLASSES = [
    "car",
    "bus",
    "truck",
    "motorcycle"
]


def detect_vehicles(image):

    model = get_yolo_model()

    results = model(
        image,
        imgsz=640,        # reduced from 1280 — uses 4x less memory
        conf=0.25,        # raised from 0.15 — filters weak detections early
        iou=0.45,
        verbose=False
    )

    annotated = image.copy()

    total_count = 0

    counts = {
        "car": 0,
        "bus": 0,
        "truck": 0,
        "motorcycle": 0
    }

    detected_vehicles = []

    for result in results:

        for box in result.boxes:

            cls_id = int(box.cls[0])

            label = model.names[cls_id]

            if label not in VEHICLE_CLASSES:
                continue

            confidence = float(box.conf[0])

            if confidence < 0.25:
                continue

            x1, y1, x2, y2 = (
                box.xyxy[0]
                .cpu()
                .numpy()
                .astype(int)
            )

            total_count += 1
            counts[label] += 1

            detected_vehicles.append({
                "bbox": (x1, y1, x2, y2),
                "label": label
            })

    return (
        annotated,
        total_count,
        counts,
        detected_vehicles
    )


def track_vehicles(image):

    model = get_yolo_model()

    results = model.track(
        image,
        persist=True,
        imgsz=640,        # reduced from 1280 — uses 4x less memory
        conf=0.25,        # raised from 0.10
        iou=0.45,
        verbose=False
    )

    annotated = image.copy()

    tracked_vehicles = []

    for result in results:

        if result.boxes is None:
            continue

        if result.boxes.id is None:
            continue

        for box, track_id in zip(
            result.boxes,
            result.boxes.id
        ):

            cls_id = int(box.cls[0])

            label = model.names[cls_id]

            if label not in VEHICLE_CLASSES:
                continue

            x1, y1, x2, y2 = (
                box.xyxy[0]
                .cpu()
                .numpy()
                .astype(int)
            )

            track_id = int(track_id.item())

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            tracked_vehicles.append({
                "track_id": track_id,
                "label": label,
                "bbox": (x1, y1, x2, y2),
                "center": (center_x, center_y)
            })

    return (
        annotated,
        tracked_vehicles
    )
