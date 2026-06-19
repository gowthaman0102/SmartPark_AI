import numpy as np


def calculate_congestion(image, boxes):

    """
    Calculate:

    - Vehicle Density
    - Road Occupancy
    - Congestion Score

    Returns:
    density_score
    occupancy_percent
    congestion_score
    """

    # ==========================================
    # DEBUG
    # ==========================================

    print("BOX COUNT:", len(boxes))

    # ==========================================
    # IMAGE SIZE
    # ==========================================

    h, w = image.shape[:2]

    image_area = h * w

    # Safety check
    if image_area <= 0:
        return 0.0, 0.0, 0.0

    # ==========================================
    # VEHICLE AREA
    # ==========================================

    vehicle_area = 0

    for box in boxes:

        try:

            x1, y1, x2, y2 = box

            width = max(0, x2 - x1)
            height = max(0, y2 - y1)

            area = width * height

            vehicle_area += area

        except Exception as e:

            print("BOX ERROR:", e)

    print("TOTAL VEHICLE AREA:", vehicle_area)

    # ==========================================
    # ROAD OCCUPANCY
    # ==========================================

    occupancy_percent = (
        vehicle_area / image_area
    ) * 100

    occupancy_percent = round(
        min(occupancy_percent, 100),
        2
    )

    # ==========================================
    # VEHICLE DENSITY
    # ==========================================

    vehicle_count = len(boxes)

    density_score = round(
        min(vehicle_count * 2.5, 100),
        2
    )

    # ==========================================
    # FINAL CONGESTION SCORE
    # ==========================================

    congestion_score = round(
        (
            occupancy_percent * 0.60
            +
            density_score * 0.40
        ),
        2
    )

    # ==========================================
    # DEBUG OUTPUT
    # ==========================================

    print("DENSITY SCORE:", density_score)
    print("OCCUPANCY %:", occupancy_percent)
    print("CONGESTION SCORE:", congestion_score)

    return (
        density_score,
        occupancy_percent,
        congestion_score
    )