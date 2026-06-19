from collections import defaultdict
import math

vehicle_positions = defaultdict(list)
stationary_frames = defaultdict(int)


def update_vehicle(track_id, center):

    vehicle_positions[track_id].append(center)

    if len(vehicle_positions[track_id]) > 300:
        vehicle_positions[track_id].pop(0)


def check_illegal_parking(
    track_id,
    fps=30,
    threshold_seconds=5,
    movement_threshold=50
):

    history = vehicle_positions[track_id]

    if len(history) < 10:
        return False, 0

    recent_history = history[-20:]

    xs = [p[0] for p in recent_history]
    ys = [p[1] for p in recent_history]

    movement = math.sqrt(
        (max(xs) - min(xs)) ** 2 +
        (max(ys) - min(ys)) ** 2
    )

    if movement < movement_threshold:
        stationary_frames[track_id] += 1
    else:
        stationary_frames[track_id] = 0

    duration = stationary_frames[track_id] / fps

    violation = duration >= threshold_seconds

    return violation, round(duration, 2)