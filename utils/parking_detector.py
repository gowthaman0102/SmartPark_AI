from collections import defaultdict
import math
import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Global tracking state.
#
# IMPORTANT: these dictionaries persist for the lifetime of the Python
# process. Streamlit keeps the same process alive across reruns and across
# different users' sessions, so if we never clear this state, track IDs left
# over from a PREVIOUS video (or a previous user's video) leak into the
# CURRENT video's analysis. That causes vehicles to be wrongly flagged
# "already stationary for X seconds" on the very first frame of a brand new
# clip. Call reset_tracking() before processing every new video.
# ---------------------------------------------------------------------------
vehicle_positions = defaultdict(list)
stationary_frames = defaultdict(int)


def reset_tracking():
    """
    Clear all tracking state. MUST be called immediately before processing
    a new video (or a new upload of the same video) so stale data from a
    previous run cannot cause false positives/negatives.
    """
    vehicle_positions.clear()
    stationary_frames.clear()


def update_vehicle(track_id, center):
    """
    Record the latest observed (x, y) center point for a tracked vehicle.
    """
    vehicle_positions[track_id].append(center)

    if len(vehicle_positions[track_id]) > 300:
        vehicle_positions[track_id].pop(0)


def point_in_zone(point, zone_points):
    """
    Returns True if `point` (x, y) in pixel coordinates lies inside the
    polygon defined by `zone_points` (list of (x, y) pixel coordinates).
    """
    if not zone_points or len(zone_points) < 3:
        return False

    polygon = np.array(zone_points, dtype=np.int32)

    result = cv2.pointPolygonTest(
        polygon,
        (float(point[0]), float(point[1])),
        False
    )

    return result >= 0


def check_illegal_parking(
    track_id,
    center=None,
    zone_points=None,
    fps=1.0,
    threshold_seconds=5,
    zone_threshold_seconds=2,
    movement_threshold=50
):
    """
    Determine whether a tracked vehicle counts as an illegal-parking
    violation.

    Parameters
    ----------
    track_id : int
        The persistent tracking ID assigned by the YOLO tracker.
    center : (x, y) or None
        The vehicle's current pixel position. Required if you want
        zone-based checking; safe to omit for pure duration-based checking.
    zone_points : list[(x, y)] or None
        Pixel-coordinate polygon describing a "no parking" zone for this
        video. If the vehicle's center falls inside this polygon, the
        much shorter `zone_threshold_seconds` is used instead of the
        general `threshold_seconds`. Pass None to disable zone checking
        and always use `threshold_seconds`.
    fps : float
        The EFFECTIVE sampling rate, in processed-frames-per-second — i.e.
        how many times per real second `update_vehicle()` is being called
        for this track. This is NOT the raw video capture fps unless you
        are processing every single frame. If you only run detection on
        every Nth frame, pass (raw_fps / N) here, otherwise stationary
        duration will be calculated incorrectly.
    threshold_seconds : float
        Seconds a vehicle must stay stationary outside any zone (or when
        no zone is defined) before it's flagged illegal.
    zone_threshold_seconds : float
        Seconds a vehicle must stay stationary INSIDE a no-parking zone
        before it's flagged illegal. Kept short since stopping in a
        marked restricted zone at all is the violation.
    movement_threshold : float
        Max pixel displacement across the recent history window for a
        vehicle to still be considered "stationary".

    Returns
    -------
    (violation: bool, duration_seconds: float, in_zone: bool)
    """

    history = vehicle_positions[track_id]

    if len(history) < 5:
        return False, 0, False

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

    duration = stationary_frames[track_id] / fps if fps > 0 else 0

    in_zone = False
    if zone_points and center is not None:
        in_zone = point_in_zone(center, zone_points)

    active_threshold = zone_threshold_seconds if in_zone else threshold_seconds

    violation = duration >= active_threshold

    return violation, round(duration, 2), in_zone
