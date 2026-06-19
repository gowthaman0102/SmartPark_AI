from ultralytics import YOLO
import cv2

print("SMARTPARK YOLO DETECTOR LOADED")

model = YOLO("yolov8x.pt")

VEHICLE_CLASSES = [
    "car",
    "bus",
    "truck",
    "motorcycle"
]


def detect_vehicles(image):

    results = model(
        image,
        imgsz=1280,
        conf=0.15,
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

    detected_boxes = []

    for result in results:

        for box in result.boxes:

            cls_id = int(box.cls[0])

            label = model.names[cls_id]

            if label not in VEHICLE_CLASSES:
                continue

            confidence = float(box.conf[0])

            if confidence < 0.15:
                continue

            x1, y1, x2, y2 = (
                box.xyxy[0]
                .cpu()
                .numpy()
                .astype(int)
            )

            total_count += 1
            counts[label] += 1

            detected_boxes.append(
                (x1, y1, x2, y2)
            )

            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                3
            )

            cv2.putText(
                annotated,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    return (
        annotated,
        total_count,
        counts,
        detected_boxes
    )


def track_vehicles(image):

    results = model.track(
        image,
        persist=True,
        imgsz=1280,
        conf=0.10,
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

            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                3
            )

            cv2.putText(
                annotated,
                f"{label} #{track_id}",
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    return (
        annotated,
        tracked_vehicles
    )