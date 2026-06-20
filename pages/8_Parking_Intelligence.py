# -*- coding: utf-8 -*-
"""
parking_intelligence.py
=======================
SmartPark AI – Production-Ready Parking Intelligence Dashboard
Integrates: yolo_detector.py · parking_detector.py · yolov8x.pt
"""

# ─────────────────────────────────────────────────────────────
# STDLIB / THIRD-PARTY IMPORTS
# ─────────────────────────────────────────────────────────────
import sys
import os
import math
import tempfile
import importlib
from collections import defaultdict

import cv2
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from PIL import Image

# ─────────────────────────────────────────────────────────────
# PATH BOOTSTRAP
# ─────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

_UTILS_DIR = os.path.join(_SCRIPT_DIR, "utils")
if os.path.isdir(_UTILS_DIR) and _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

# ─────────────────────────────────────────────────────────────
# IMPORT EXISTING MODULES
# ─────────────────────────────────────────────────────────────
def _import_module(primary: str, fallback: str):
    for name in (primary, fallback):
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError:
            continue
    raise ImportError(f"Cannot find '{primary}' or '{fallback}'.")

yolo_mod    = _import_module("utils.yolo_detector",    "yolo_detector")
parking_mod = _import_module("utils.parking_detector", "parking_detector")

detect_vehicles       = yolo_mod.detect_vehicles
track_vehicles        = yolo_mod.track_vehicles
update_vehicle        = parking_mod.update_vehicle
check_illegal_parking = parking_mod.check_illegal_parking

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartPark AI – Parking Intelligence",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# LIGHT THEME CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Light background ── */
.stApp {
    background: #f0f4f8;
    color: #1e293b;
}

/* ── Hide default chrome ── */
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebar"] {
    display: block !important;
}
.block-container { padding: 1.5rem 2rem; max-width: 1600px; }

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.12);
}
.hero-title {
    font-size: 2rem; font-weight: 800;
    color: #ffffff;
    margin: 0; line-height: 1.2;
}
.hero-sub {
    font-size: 0.92rem; color: rgba(255,255,255,0.65);
    margin-top: 0.4rem;
}

/* ── Section headers ── */
.section-header {
    font-size: 1.05rem; font-weight: 700;
    color: #1e293b;
    border-left: 4px solid #475569;
    padding-left: 0.75rem;
    margin: 1.4rem 0 0.7rem;
    letter-spacing: 0.3px;
}

/* ── Metric cards ── */
.metric-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.1rem 1rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    text-align: center;
    transition: transform 0.18s, box-shadow 0.18s;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}
.metric-value {
    font-size: 1.9rem; font-weight: 800; color: #0f172a;
}
.metric-value-danger {
    font-size: 1.9rem; font-weight: 800; color: #dc2626;
}
.metric-label {
    font-size: 0.75rem; color: #64748b;
    text-transform: uppercase; letter-spacing: 0.8px;
    margin-top: 0.2rem;
}

/* ── Resource card ── */
.resource-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    display: flex; align-items: center; gap: 1rem;
}
.resource-icon { font-size: 1.8rem; }
.resource-count { font-size: 1.6rem; font-weight: 700; color: #0f172a; }
.resource-name  { font-size: 0.8rem; color: #64748b; }

/* ── Action cards ── */
.action-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    border-left: 4px solid #475569;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    color: #1e293b;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.action-card.critical { border-left-color: #dc2626; background: #fff5f5; }
.action-card.high     { border-left-color: #ea580c; background: #fff7f0; }
.action-card.medium   { border-left-color: #d97706; background: #fffbeb; }
.action-card.low      { border-left-color: #16a34a; background: #f0fdf4; }

/* ── Upload zone (custom HTML card) ── */
.upload-zone {
    background: #ffffff;
    border: 2px dashed #cbd5e1;
    border-radius: 14px;
    padding: 2.5rem; text-align: center;
}

/* ── Streamlit native file uploader – force light theme ── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border-radius: 14px !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #f8fafc !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 14px !important;
    color: #1e293b !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: #f1f5f9 !important;
    border-color: #94a3b8 !important;
}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] div,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] label {
    color: #475569 !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: #ff4b4b !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: #cc0000 !important;
}
/* ── Uploaded file chip: force RED bg + WHITE text everywhere ── */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileList"] > div,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileList"] > div > div,
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] section,
[data-testid="stFileUploaderFile"] article,
[data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploaderFile"] > div > div,
[data-baseweb="tag"] {
    background: #ff4b4b !important;
    background-color: #ff4b4b !important;
    border: 1px solid #ff4b4b !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}

[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFile"] p,
[data-testid="stFileUploaderFileList"] span,
[data-testid="stFileUploaderFileList"] small,
[data-testid="stFileUploaderFileList"] p {
    color: #ffffff !important;
    background: transparent !important;
    background-color: transparent !important;
}

[data-testid="stFileUploaderFile"] button,
[data-testid="stFileUploaderFile"] button *,
[data-testid="stFileUploaderFileList"] button,
[data-testid="stFileUploaderFileList"] button * {
    background: transparent !important;
    background-color: transparent !important;
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
    border: none !important;
    box-shadow: none !important;
}


/* ── Divider ── */
.sp-divider {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 1.2rem 0;
}

/* ── Violation row ── */
.violation-row {
    background: #fff5f5;
    border: 1px solid #fca5a5;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.4rem;
    font-size: 0.87rem;
    color: #1e293b;
}

/* ── Sign row ── */
.sign-row {
    background: #fefce8;
    border: 1px solid #fcd34d;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.4rem;
    font-size: 0.87rem;
    color: #1e293b;
}

/* ── Progress info ── */
.progress-info {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #475569;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "results_ready"   : False,
        "annotated_frame" : None,
        "last_counts"     : {"car":0,"bus":0,"truck":0,"motorcycle":0},
        "last_total"      : 0,
        "last_illegal"    : 0,
        "last_occupancy"  : 0.0,
        "last_congestion" : 0.0,
        "last_severity"   : 0.0,
        "last_risk"       : 0.0,
        "sign_zones"      : [],
        "violations"      : [],
        "active_tracked"  : 0,
        "total_tracked"   : 0,
        "_resources"      : {},
        "_actions"        : [],
        "_density"        : 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ─────────────────────────────────────────────────────────────
# DETECTION SETTINGS
# ─────────────────────────────────────────────────────────────
PARKING_THRESHOLD_SEC  = 2      # seconds near sign / stationary → illegal (lowered for reliability)
MOVEMENT_THRESHOLD_PX  = 55     # px spread over 20 positions = still parked
SIGN_PROXIMITY_PX      = 400    # pixels around sign bbox to count as violation zone (wider net)
SIGN_DETECT_EVERY_N    = 40     # re-detect signs every N processed frames (fast heuristic)
PROCESS_EVERY_N_FRAMES = 2      # run YOLO on 1-in-2 raw frames (2× speed boost)
MIN_STATIONARY_FRAMES  = 3      # min processed frames before calling stationary (lowered)

# ─────────────────────────────────────────────────────────────
# OCR / SIGN DETECTION
# ─────────────────────────────────────────────────────────────
try:
    import easyocr
    _ocr_reader = easyocr.Reader(["en"], verbose=False)
    _HAS_OCR = True
except Exception:
    _HAS_OCR = False

_NO_PARKING_KW = [
    "no parking", "no parking area", "tow away zone",
    "parking prohibited", "no park", "tow away", "no stopping",
]

def _has_no_parking_text(text: str) -> bool:
    return any(kw in text.lower() for kw in _NO_PARKING_KW)


def _merge_zones(zones: list) -> list:
    """Merge overlapping bounding boxes into a single zone."""
    if not zones:
        return []
    changed = True
    while changed:
        changed = False
        merged, used = [], [False] * len(zones)
        for i, (ax1, ay1, ax2, ay2) in enumerate(zones):
            if used[i]:
                continue
            for j, (bx1, by1, bx2, by2) in enumerate(zones):
                if i == j or used[j]:
                    continue
                if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
                    ax1, ay1 = min(ax1, bx1), min(ay1, by1)
                    ax2, ay2 = max(ax2, bx2), max(ay2, by2)
                    used[j]  = True
                    changed  = True
            merged.append((ax1, ay1, ax2, ay2))
            used[i] = True
        zones = merged
    return zones


def detect_no_parking_signs(frame_bgr: np.ndarray, use_ocr: bool = False) -> list:
    """
    Fast NO PARKING zone detector.
    Primary  : red/blue/yellow color+shape heuristic (no OCR – very fast).
    Optional : OCR via easyocr when use_ocr=True (slow, for image mode only).
    Returns list of (x1,y1,x2,y2) zone boxes.
    """
    zones = []
    h, w  = frame_bgr.shape[:2]
    frame_area = h * w

    # Work on a half-size copy for speed
    small   = cv2.resize(frame_bgr, (w // 2, h // 2), interpolation=cv2.INTER_LINEAR)
    sh, sw  = small.shape[:2]
    hsv     = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    kern3   = np.ones((3, 3), np.uint8)
    kern5   = np.ones((5, 5), np.uint8)

    # ── Red mask (classic No Parking circle sign) ────────────────────
    m_r1 = cv2.inRange(hsv, (0,   100, 80), (12,  255, 255))
    m_r2 = cv2.inRange(hsv, (160, 100, 80), (180, 255, 255))
    red  = cv2.morphologyEx(cv2.bitwise_or(m_r1, m_r2), cv2.MORPH_CLOSE, kern5)

    # ── Yellow / amber mask (Indian advisory boards) ──────────────
    yellow = cv2.morphologyEx(
        cv2.inRange(hsv, (15, 80, 120), (38, 255, 255)), cv2.MORPH_CLOSE, kern5)

    # ── Blue mask (blue prohibition signs) ────────────────────
    blue = cv2.morphologyEx(
        cv2.inRange(hsv, (100, 80, 60), (140, 255, 255)), cv2.MORPH_CLOSE, kern5)

    for mask in (red, yellow, blue):
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kern3)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        small_area = sh * sw
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if not (small_area * 0.0004 < area < small_area * 0.20):
                continue
            bx, by, bw, bh = cv2.boundingRect(cnt)
            aspect = bw / (bh + 1e-6)
            # Check circularity for round signs
            perim = cv2.arcLength(cnt, True)
            circ  = (4 * math.pi * area / (perim * perim)) if perim > 0 else 0
            if circ < 0.25 and not (0.35 < aspect < 4.0):
                continue
            if bw < 12 or bh < 10:
                continue
            # Scale coords back to full resolution with a small padding
            pad  = 5
            rx1  = max(0, (bx - pad) * 2)
            ry1  = max(0, (by - pad) * 2)
            rx2  = min(w, (bx + bw + pad) * 2)
            ry2  = min(h, (by + bh + pad) * 2)
            zones.append((rx1, ry1, rx2, ry2))

    zones = _merge_zones(zones)
    zones = sorted(zones, key=lambda z: (z[2]-z[0])*(z[3]-z[1]), reverse=True)[:6]

    # ── OCR pass (image mode only) ───────────────────────────────
    if use_ocr and _HAS_OCR:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        try:
            for (pts, text, conf) in _ocr_reader.readtext(rgb):
                if conf < 0.30 or not _has_no_parking_text(text):
                    continue
                arr        = np.array(pts, dtype=np.int32)
                tx1, ty1   = arr.min(axis=0)
                tx2, ty2   = arr.max(axis=0)
                pad        = 10
                zones.append((
                    max(0, tx1-pad), max(0, ty1-pad),
                    min(w, tx2+pad), min(h, ty2+pad)
                ))
        except Exception:
            pass
        zones = _merge_zones(zones)

    return zones


# ─────────────────────────────────────────────────────────────
# GEOMETRY HELPERS
# ─────────────────────────────────────────────────────────────
def _vehicle_near_sign(vx1, vy1, vx2, vy2, sx1, sy1, sx2, sy2, prox: int) -> bool:
    """True if vehicle bbox overlaps or is within prox pixels of sign zone."""
    ex1, ey1 = sx1 - prox, sy1 - prox
    ex2, ey2 = sx2 + prox, sy2 + prox
    return not (vx2 < ex1 or vx1 > ex2 or vy2 < ey1 or vy1 > ey2)


def vehicle_near_any_sign(bbox: tuple, sign_zones: list, prox: int = SIGN_PROXIMITY_PX) -> bool:
    vx1, vy1, vx2, vy2 = bbox
    return any(_vehicle_near_sign(vx1, vy1, vx2, vy2, *sz, prox) for sz in sign_zones)


def _bbox_iou(a: tuple, b: tuple) -> float:
    """Compute Intersection-over-Union between two bounding boxes (x1,y1,x2,y2)."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1); iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2); iy2 = min(ay2, by2)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    if inter == 0:
        return 0.0
    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union  = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def deduplicate_vehicles(vehicles: list, iou_threshold: float = 0.45) -> list:
    """
    Remove duplicate tracked-vehicle entries caused by YOLO assigning two track IDs
    to the same physical vehicle.  When two detections overlap by more than
    iou_threshold, we keep the one with the smaller (earlier) track_id.
    """
    if not vehicles:
        return vehicles
    # Sort by track_id so we always keep the lower (earlier) ID
    sorted_vhs = sorted(vehicles, key=lambda v: v["track_id"])
    kept = []
    for vh in sorted_vhs:
        duplicate = False
        for kv in kept:
            if _bbox_iou(vh["bbox"], kv["bbox"]) >= iou_threshold:
                duplicate = True
                break
        if not duplicate:
            kept.append(vh)
    return kept


# ─────────────────────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────────────────────
def compute_occupancy(boxes: list, h: int, w: int) -> float:
    if h <= 0 or w <= 0:
        return 0.0
    area = sum((x2-x1)*(y2-y1) for x1,y1,x2,y2 in boxes)
    return min(round(area / (h*w) * 100, 2), 100.0)


def compute_density(n: int, h: int, w: int) -> float:
    if h <= 0 or w <= 0 or n == 0:
        return 0.0
    mp = (h*w) / 1_000_000
    return min(round((n / max(mp, 0.01)) * 5, 2), 100.0)


def compute_congestion(density: float, occupancy: float) -> float:
    return min(round(density*0.5 + occupancy*0.5, 2), 100.0)


def compute_severity(vehicles: int, illegal: int, occ: float, cong: float) -> float:
    return min(round(
        min(vehicles/30, 1.0)*25 +
        min(illegal/5,   1.0)*35 +
        (occ/100)*20 +
        (cong/100)*20, 2), 100.0)


def compute_risk(illegal: int, cong: float, occ: float, density: float) -> float:
    return min(round(
        min(illegal/5, 1.0)*40 +
        (cong/100)*25 +
        (occ/100)*20 +
        (density/100)*15, 2), 100.0)


def _lvl(score, ths, labels):
    for t, l in zip(ths, labels):
        if score <= t:
            return l
    return labels[-1]

occ_level  = lambda v: _lvl(v, [30,60],       ["Low","Medium","High"])
cong_level = lambda v: _lvl(v, [33,66],       ["Low","Medium","High"])
sev_level  = lambda v: _lvl(v, [25,50,75],    ["Low","Moderate","High","Critical"])
risk_level = lambda v: _lvl(v, [33,66],       ["Low","Medium","High"])


# ─────────────────────────────────────────────────────────────
# RESOURCE PLANNER
# ─────────────────────────────────────────────────────────────
def plan_resources(risk: float, illegal: int, cong: float) -> dict:
    officers  = 1 + math.ceil(illegal/2) + math.ceil(risk/33)
    patrol    = max(1, math.ceil(officers/3)) if (illegal > 0 or cong > 30) else 0
    tow       = math.ceil(illegal/2) if illegal > 0 else 0
    return {"officers": officers, "patrol_vehicles": patrol, "tow_trucks": tow}


# ─────────────────────────────────────────────────────────────
# ACTION ENGINE
# ─────────────────────────────────────────────────────────────
def generate_actions(risk: float, severity: float, illegal: int, cong: float) -> list:
    acts = []
    if illegal >= 5:
        acts.append(("critical", "🚨 Critical: Multiple Violations – Dispatch Tow Trucks Immediately"))
    elif illegal >= 3:
        acts.append(("high", "🔴 Deploy Patrol Vehicle – Multiple Active Violations"))
    elif illegal == 2:
        acts.append(("high", "🔴 Dispatch Tow Truck – 2 Vehicles Illegally Parked"))
    elif illegal == 1:
        acts.append(("medium", "🟠 Issue Warning Notice – 1 Vehicle Illegally Parked"))
    if cong >= 75:
        acts.append(("critical", "🚨 Critical Congestion – Initiate Traffic Control Protocol"))
    elif cong >= 50:
        acts.append(("high", "🔴 Deploy Officer for Traffic Management"))
    elif cong >= 30:
        acts.append(("medium", "🟠 Monitor Congestion – Consider Patrol Deployment"))
    if risk >= 80:
        acts.append(("critical", "🚨 HIGH RISK – Request Immediate Enforcement Response"))
    elif risk >= 60:
        acts.append(("high", "🔴 Elevated Risk – Increase Patrol Frequency"))
    elif risk >= 40:
        acts.append(("medium", "🟠 Moderate Risk – Schedule Enforcement Check"))
    if severity >= 75:
        acts.append(("critical", "🚨 Critical Severity – Escalate to Traffic Command Center"))
    elif severity >= 50:
        acts.append(("high", "🔴 High Severity – Assign Additional Officers"))
    if not acts:
        acts.append(("low", "✅ Situation Normal – Continue Standard Monitoring"))
    # deduplicate
    seen, out = set(), []
    for item in acts:
        if item[1] not in seen:
            seen.add(item[1]); out.append(item)
    return out


# ─────────────────────────────────────────────────────────────
# ANNOTATION HELPERS
# ─────────────────────────────────────────────────────────────
_RED    = (0, 0, 220)
_GREEN  = (0, 200, 0)
_ORANGE = (0, 140, 255)

def draw_illegal(frame, bbox, tid, label, duration):
    x1, y1, x2, y2 = bbox
    cv2.rectangle(frame, (x1,y1), (x2,y2), _RED, 3)
    tag = f"ILLEGAL #{tid} | {label} | {duration:.1f}s"
    (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, max(y1-th-8, 0)), (x1+tw+6, y1), _RED, -1)
    cv2.putText(frame, tag, (x1+3, max(y1-4, th)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    return frame


def draw_sign_zones(frame, sign_zones):
    if sign_zones:
        # Encircle the entire frame with a single NO PARKING ZONE label
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (0, 0), (w, h), _ORANGE, 6)
        label = "NO PARKING ZONE DETECTED"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        cv2.rectangle(frame, (10, 10), (10+tw+20, 20+th+10), _ORANGE, -1)
        cv2.putText(frame, label, (20, 20+th),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 2)
    return frame


# ─────────────────────────────────────────────────────────────
# IMAGE PIPELINE
# ─────────────────────────────────────────────────────────────
def process_image(img_bgr: np.ndarray) -> dict:
    h, w = img_bgr.shape[:2]

    annotated, total_count, counts, boxes = detect_vehicles(img_bgr)
    sign_zones = detect_no_parking_signs(img_bgr, use_ocr=True)   # OCR OK for single image
    annotated  = draw_sign_zones(annotated, sign_zones)

    # ── Illegal detection for images: any vehicle bbox near a sign zone ──
    # First, deduplicate boxes to prevent flagging the same physical vehicle twice
    # (YOLO can output two overlapping detections for one car).
    unique_boxes = []
    for bbox in boxes:
        duplicate = False
        for ub in unique_boxes:
            if _bbox_iou(tuple(bbox), tuple(ub)) >= 0.45:
                duplicate = True
                break
        if not duplicate:
            unique_boxes.append(bbox)
    boxes = unique_boxes

    violations  = []
    illegal_boxes = set()
    if sign_zones:
        for idx, bbox in enumerate(boxes):
            if vehicle_near_any_sign(bbox, sign_zones, SIGN_PROXIMITY_PX):
                illegal_boxes.add(idx)
                x1, y1, x2, y2 = bbox
                tid = idx + 1
                # Draw red illegal box (overrides the green box already drawn)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), _RED, 3)
                tag = f"ILLEGAL #{tid} | near NO PARKING"
                (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(annotated, (x1, max(y1-th-8, 0)), (x1+tw+6, y1), _RED, -1)
                cv2.putText(annotated, tag, (x1+3, max(y1-4, th)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                violations.append({
                    "track_id": tid,
                    "label"   : "vehicle",
                    "duration": 0.0,
                    "bbox"    : bbox,
                })

    illegal_n = len(illegal_boxes)
    occ   = compute_occupancy(boxes, h, w)
    dens  = compute_density(total_count, h, w)
    cong  = compute_congestion(dens, occ)
    sev   = compute_severity(total_count, illegal_n, occ, cong)
    risk  = compute_risk(illegal_n, cong, occ, dens)
    res   = plan_resources(risk, illegal_n, cong)
    acts  = generate_actions(risk, sev, illegal_n, cong)

    return dict(
        annotated=annotated, total_count=total_count, counts=counts,
        sign_zones=sign_zones, occupancy=occ, density=dens,
        congestion=cong, illegal_count=illegal_n, violations=violations,
        severity=sev, risk=risk, resources=res, actions=acts,
        active_tracked=total_count, total_tracked=total_count,
    )


def _is_stationary(tid: int, eff_fps: float) -> tuple:
    """
    Simple window-based stationary check (no camera compensation).
    Compares max positional spread over last 20 processed positions.
    Uses effective fps (fps / PROCESS_EVERY_N_FRAMES) for correct duration.
    """
    history = parking_mod.vehicle_positions.get(tid)
    if not history or len(history) < MIN_STATIONARY_FRAMES:
        return False, 0.0

    window  = min(20, len(history))
    recent  = history[-window:]
    xs      = [p[0] for p in recent]
    ys      = [p[1] for p in recent]
    spread  = math.sqrt((max(xs) - min(xs))**2 + (max(ys) - min(ys))**2)

    if spread < MOVEMENT_THRESHOLD_PX:
        parking_mod.stationary_frames[tid] = \
            parking_mod.stationary_frames.get(tid, 0) + 1
    else:
        parking_mod.stationary_frames[tid] = 0

    duration  = parking_mod.stationary_frames.get(tid, 0) / eff_fps
    violation = duration >= PARKING_THRESHOLD_SEC
    return violation, round(duration, 2)


def process_video(video_path: str, progress_bar) -> dict:
    """
    Fast video pipeline:
      - Processes 1-in-PROCESS_EVERY_N_FRAMES raw frames (speed).
      - Sign detection via fast color+shape heuristic (no OCR).
      - Dual violation logic:
          1. Time-in-zone: vehicle inside a NO PARKING zone ≥ threshold → illegal.
          2. Stationary fallback: no sign detected but vehicle hasn’t moved ≥ threshold → illegal.
    """
    parking_mod.vehicle_positions.clear()
    parking_mod.stationary_frames.clear()

    all_track_ids   : set  = set()
    illegal_ids     : set  = set()
    violations_list : list = []
    sign_zones      : list = []
    zone_entry      : dict = {}   # {tid: processed_idx when entered zone}

    # ── Final-frame snapshot (metrics always match the displayed frame) ──
    last_annotated           = None
    last_tracked   : list   = []
    last_frame_counts        = {"car": 0, "bus": 0, "truck": 0, "motorcycle": 0}
    last_frame_boxes : list = []
    last_occ                 = 0.0
    last_cong                = 0.0
    last_dens                = 0.0
    last_illegal_in_frame : set  = set()   # illegal IDs visible in final frame
    last_violations_in_frame : list = []   # violation records for final frame

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("❌ Cannot open video file.")
        return {}

    fps          = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 1)
    h            = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w            = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_idx    = 0
    proc_idx     = 0
    eff_fps      = fps / PROCESS_EVERY_N_FRAMES   # real frames/sec we actually analyze

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        # ── Frame skip ───────────────────────────────────────────────
        if frame_idx % PROCESS_EVERY_N_FRAMES != 1:
            progress_bar.progress(
                min(frame_idx / total_frames, 1.0),
                text=f"⏳ Frame {frame_idx}/{total_frames}",
            )
            continue
        proc_idx += 1

        # ── Sign detection (fast heuristic, every N processed frames) ──
        if proc_idx % SIGN_DETECT_EVERY_N == 1:
            sign_zones = detect_no_parking_signs(frame, use_ocr=False)

        # ── Pre-resize for YOLO (imgsz=320 needs a small input) ──────
        ph, pw = frame.shape[:2]
        if pw > 640:
            sc         = 640 / pw
            proc_frame = cv2.resize(frame, (640, int(ph * sc)), cv2.INTER_LINEAR)
            sx, sy     = pw / 640, ph / int(ph * sc)
        else:
            proc_frame = frame
            sx, sy     = 1.0, 1.0

        # ── YOLO track ────────────────────────────────────────────
        try:
            tracked_frame, tracked_vehicles = track_vehicles(proc_frame)
            if sx != 1.0:
                scaled = []
                for vh in tracked_vehicles:
                    x1,y1,x2,y2 = vh["bbox"]
                    cx,cy        = vh["center"]
                    scaled.append({**vh,
                        "bbox"  : (int(x1*sx),int(y1*sy),int(x2*sx),int(y2*sy)),
                        "center": (int(cx*sx),int(cy*sy)),
                    })
                tracked_vehicles = scaled
                tracked_frame    = frame.copy()
                for vh in tracked_vehicles:
                    x1,y1,x2,y2 = vh["bbox"]
                    cv2.rectangle(tracked_frame,(x1,y1),(x2,y2),(0,220,0),3)
                    cv2.putText(tracked_frame, f"{vh['label']} #{vh['track_id']}",
                                (x1,max(y1-10,20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.65,(0,220,0),2)
        except Exception:
            tracked_frame    = frame.copy()
            tracked_vehicles = []

        # ── Deduplicate: remove overlapping detections of the same physical vehicle ──
        # YOLO sometimes assigns two track IDs to one car; IoU-NMS collapses them
        # to a single entry (keeping the smaller/earlier track_id) so that one
        # vehicle can only produce one illegal flag and one bounding box.
        tracked_vehicles = deduplicate_vehicles(tracked_vehicles, iou_threshold=0.45)

        # Update position history
        for vh in tracked_vehicles:
            update_vehicle(vh["track_id"], vh["center"])

        # Draw sign zones on full-res frame
        tracked_frame = draw_sign_zones(tracked_frame, sign_zones)

        # ── Per-vehicle violation logic ─────────────────────────────
        frame_counts = {"car":0,"bus":0,"truck":0,"motorcycle":0}
        frame_boxes  = []

        for vh in tracked_vehicles:
            tid   = vh["track_id"]
            bbox  = vh["bbox"]
            label = vh["label"]

            all_track_ids.add(tid)
            if label in frame_counts:
                frame_counts[label] += 1
            frame_boxes.append(bbox)

            near_sign = vehicle_near_any_sign(bbox, sign_zones, SIGN_PROXIMITY_PX) \
                        if sign_zones else False

            # ── Method 1: Time-in-zone (primary – most reliable) ─────
            if near_sign:
                if tid not in zone_entry:
                    zone_entry[tid] = proc_idx
                duration     = (proc_idx - zone_entry[tid]) / eff_fps
                is_violation = duration >= PARKING_THRESHOLD_SEC
            else:
                zone_entry.pop(tid, None)
                # ── Method 2: Position-stationary fallback ──────────
                is_violation, duration = _is_stationary(tid, eff_fps)

            duration = round(duration, 2)

            if is_violation and tid not in illegal_ids:
                illegal_ids.add(tid)
                violations_list.append({
                    "track_id": tid,
                    "label"   : label,
                    "duration": duration,
                    "bbox"    : bbox,
                })

            if tid in illegal_ids:
                tracked_frame = draw_illegal(tracked_frame, bbox, tid, label, duration)

        # ── Compute per-frame analytics ──────────────────────────────
        occ  = compute_occupancy(frame_boxes, h, w)
        dens = compute_density(sum(frame_counts.values()), h, w)
        cong = compute_congestion(dens, occ)

        # ── Snapshot this frame as the "current" state ────────────────
        # Only vehicles present in this frame that are in illegal_ids
        frame_tids              = {vh["track_id"] for vh in tracked_vehicles}
        last_frame_counts       = dict(frame_counts)          # per-class count this frame
        last_frame_boxes        = list(frame_boxes)           # bboxes this frame
        last_occ                = occ
        last_cong               = cong
        last_dens               = dens
        last_illegal_in_frame   = illegal_ids & frame_tids    # illegal & visible now
        # Keep only violation records whose vehicle is still in this frame
        last_violations_in_frame = [
            v for v in violations_list
            if v["track_id"] in last_illegal_in_frame
        ]

        last_annotated = tracked_frame
        last_tracked   = tracked_vehicles

        progress_bar.progress(
            min(frame_idx / total_frames, 1.0),
            text=f"⏳ Frame {frame_idx}/{total_frames}",
        )

    cap.release()
    progress_bar.progress(1.0, text="✅ Done")

    # ── Final-frame override: any vehicle currently near a sign is ALWAYS illegal ──
    # This guarantees the annotated image and dashboard are in perfect sync.
    # Even if the time threshold wasn't met (short video / brief appearance),
    # a vehicle visibly next to a NO PARKING sign must be flagged.
    if sign_zones and last_tracked and last_annotated is not None:
        # Deduplicate the last frame's tracked vehicles too, so the override
        # cannot introduce a second box for an already-flagged vehicle.
        last_tracked = deduplicate_vehicles(last_tracked, iou_threshold=0.45)

        # Track which IDs have already been drawn as illegal during the loop
        already_drawn_illegal = set(illegal_ids)  # snapshot before override

        for vh in last_tracked:
            tid  = vh["track_id"]
            bbox = vh["bbox"]
            lbl  = vh["label"]
            if vehicle_near_any_sign(bbox, sign_zones, SIGN_PROXIMITY_PX):
                if tid not in illegal_ids:
                    # Brand-new violation — add to ids, list, and draw once
                    illegal_ids.add(tid)
                    violations_list.append({
                        "track_id": tid,
                        "label"   : lbl,
                        "duration": 0.0,
                        "bbox"    : bbox,
                    })
                    last_annotated = draw_illegal(last_annotated, bbox, tid, lbl, 0.0)
                # If tid was already in illegal_ids AND was NOT drawn during the
                # final processed frame's loop (edge case: tracking lost then
                # re-appeared), redraw it exactly once.
                elif tid not in already_drawn_illegal:
                    last_annotated = draw_illegal(last_annotated, bbox, tid, lbl, 0.0)
                # else: already drawn during the loop — do NOT draw again.

        # Rebuild final-frame snapshots after the override
        frame_tids             = {vh["track_id"] for vh in last_tracked}
        last_illegal_in_frame  = illegal_ids & frame_tids
        last_violations_in_frame = [
            v for v in violations_list
            if v["track_id"] in last_illegal_in_frame
        ]

    # ── All metrics derived from the FINAL processed frame only ─────
    # This ensures the dashboard matches exactly what is shown in the
    # annotated output image (no historical accumulation artefacts).
    final_total    = sum(last_frame_counts.values())
    final_illegal  = len(last_illegal_in_frame)
    final_occ      = round(last_occ,  2)
    final_cong     = round(last_cong, 2)
    final_dens     = round(last_dens, 2)

    sev  = compute_severity(final_total, final_illegal, final_occ, final_cong)
    risk = compute_risk(final_illegal, final_cong, final_occ, final_dens)
    res  = plan_resources(risk, final_illegal, final_cong)
    acts = generate_actions(risk, sev, final_illegal, final_cong)

    return dict(
        annotated      = last_annotated,
        total_count    = final_total,
        counts         = last_frame_counts,
        sign_zones     = sign_zones,
        occupancy      = final_occ,
        density        = final_dens,
        congestion     = final_cong,
        illegal_count  = final_illegal,
        violations     = last_violations_in_frame,
        severity       = sev,
        risk           = risk,
        resources      = res,
        actions        = acts,
        active_tracked = len(last_tracked),
        total_tracked  = len(all_track_ids),
        fps            = fps,
        frame_count    = frame_idx,
    )


# ─────────────────────────────────────────────────────────────
# PLOTLY CHARTS
# ─────────────────────────────────────────────────────────────
_LIGHT_LAYOUT = dict(
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor ="rgba(255,255,255,0)",
    font=dict(family="Inter", color="#1e293b"),
    margin=dict(l=20, r=20, t=40, b=20),
)


def _gauge(title, value, max_val, stops):
    bar_color = stops[-1][1]
    for th, col in stops:
        if value <= th:
            bar_color = col; break
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={"text": title, "font": {"size": 13, "color": "#64748b"}},
        number={"font": {"size": 26, "color": "#0f172a"}},
        gauge={
            "axis"    : {"range":[0, max_val], "tickcolor":"#94a3b8",
                         "tickfont":{"color":"#94a3b8","size":9}},
            "bar"     : {"color": bar_color, "thickness": 0.28},
            "bgcolor" : "rgba(0,0,0,0.03)",
            "borderwidth": 0,
            "steps"   : [
                {"range":[0,          max_val*.33], "color":"rgba(22,163,74,.1)"},
                {"range":[max_val*.33,max_val*.66], "color":"rgba(217,119,6,.1)"},
                {"range":[max_val*.66,max_val],     "color":"rgba(220,38,38,.1)"},
            ],
            "threshold": {"line":{"color":bar_color,"width":3},"value":value},
        }
    ))
    fig.update_layout(**_LIGHT_LAYOUT, height=200)
    return fig


def vehicle_distribution_chart(counts):
    labels = [k.capitalize() for k,v in counts.items() if v > 0]
    values = [v for v in counts.values() if v > 0]
    if not values:
        labels, values = ["No Vehicles"], [1]
    colors = ["#3b82f6","#0891b2","#16a34a","#d97706"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors[:len(labels)], line=dict(color="#f8fafc",width=2)),
        textinfo="label+percent",
        textfont=dict(color="#1e293b", size=12),
    ))
    fig.update_layout(
        **_LIGHT_LAYOUT, showlegend=False, height=240,
        title={"text":"Vehicle Distribution","font":{"color":"#64748b","size":13}},
    )
    return fig


def score_bar_chart(density, occ, cong, sev, risk):
    cats   = ["Density","Occupancy %","Congestion","Severity","Risk"]
    vals   = [density, occ, cong, sev, risk]
    colors = ["#3b82f6","#0891b2","#d97706","#ea580c","#dc2626"]
    fig = go.Figure(go.Bar(
        x=cats, y=vals,
        marker_color=colors,
        text=[f"{v:.1f}" for v in vals],
        textposition="outside",
        textfont=dict(color="#1e293b", size=12),
    ))
    fig.update_layout(
        **_LIGHT_LAYOUT, height=280, showlegend=False,
        yaxis=dict(range=[0,110], gridcolor="rgba(0,0,0,0.05)"),
        title={"text":"Score Breakdown (0–100)","font":{"color":"#64748b","size":13}},
    )
    return fig


# ─────────────────────────────────────────────────────────────
# HTML CARD HELPERS
# ─────────────────────────────────────────────────────────────
def _metric(label, value, danger=False):
    cls = "metric-value-danger" if danger else "metric-value"
    return (f'<div class="metric-card">'
            f'<div class="{cls}">{value}</div>'
            f'<div class="metric-label">{label}</div>'
            f'</div>')


def _resource(icon, count, name):
    return (f'<div class="resource-card">'
            f'<div class="resource-icon">{icon}</div>'
            f'<div><div class="resource-count">{count}</div>'
            f'<div class="resource-name">{name}</div></div>'
            f'</div>')


# ─────────────────────────────────────────────────────────────
# ════════════════ MAIN UI ════════════════
# ─────────────────────────────────────────────────────────────

# ── Hero banner ──────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🚦 SmartPark AI — Parking Intelligence Dashboard</div>
    <div class="hero-sub">
        Real-time vehicle detection · Illegal parking enforcement · Congestion &amp; risk analytics
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SECTION 1 – UPLOAD
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📂 Upload Panel</div>', unsafe_allow_html=True)

_IMAGE_EXTS = {"jpg","jpeg","png","bmp","tiff","tif","webp","gif","jfif","heic","heif"}
_VIDEO_EXTS = {"mp4","avi","mov","mkv","wmv","flv","webm","mpeg","mpg","m4v","3gp","ts","mts","m2ts"}
_ALL_EXTS   = list(_IMAGE_EXTS | _VIDEO_EXTS)

uploaded_file = st.file_uploader(
    "Upload any image or video",
    type=_ALL_EXTS,
    label_visibility="collapsed",
    help="Images: JPG · PNG · BMP · WEBP · HEIC  |  Videos: MP4 · AVI · MOV · MKV · WMV · WEBM · MPEG and more",
)

if uploaded_file is not None:
    _ext      = uploaded_file.name.lower().rsplit(".",1)[-1] if "." in uploaded_file.name else ""
    file_type = "video" if _ext in _VIDEO_EXTS else "image"
else:
    file_type = "image"

if uploaded_file is None:
    st.markdown("""
    <div class="upload-zone">
        <div style="font-size:2.2rem;">📤</div>
        <div style="font-size:1rem; color:#475569; margin-top:0.5rem; font-weight:600;">
            Upload any image or video to begin analysis
        </div>
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:0.3rem;">
            🖼️ JPG · PNG · BMP · TIFF · WEBP · GIF · HEIC
            &nbsp;|&nbsp;
            🎬 MP4 · AVI · MOV · MKV · WMV · FLV · WEBM · MPEG
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────
# RUN ANALYSIS BUTTON
# ─────────────────────────────────────────────────────────────
st.markdown('<hr class="sp-divider">', unsafe_allow_html=True)
run_col, info_col = st.columns([1, 5])
with run_col:
    run_btn = st.button("🔍 Run Analysis", type="primary", use_container_width=True)
with info_col:
    if file_type == "video":
        st.markdown(
            '<div class="progress-info">🎬 Video detected – '
            'signs will be re-detected every 10 frames to follow camera movement. '
            'Only ONE annotated result will be shown below.</div>',
            unsafe_allow_html=True
        )

if run_btn:
    st.session_state["results_ready"] = False

    # ── IMAGE ──────────────────────────────────────────────
    if file_type == "image":
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        img_bgr    = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        with st.spinner("🔍 Running YOLO detection & analytics…"):
            results = process_image(img_bgr)

    # ── VIDEO ──────────────────────────────────────────────
    else:
        suffix_map = {
            "video/mp4":".mp4","video/avi":".avi","video/quicktime":".mov",
            "video/x-msvideo":".avi","video/x-matroska":".mkv",
            "video/x-ms-wmv":".wmv","video/x-flv":".flv",
            "video/webm":".webm","video/mpeg":".mpeg",
            "video/mp2t":".ts","video/3gpp":".3gp",
        }
        _orig_ext = uploaded_file.name.rsplit(".",1)[-1] if "." in uploaded_file.name else "mp4"
        suffix    = suffix_map.get(uploaded_file.type, f".{_orig_ext}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Progress bar only – no live preview duplication
        st.markdown('<div class="section-header">⏳ Processing Video</div>',
                    unsafe_allow_html=True)
        progress_ph = st.progress(0, text="Initialising…")

        results = process_video(tmp_path, progress_ph)
        os.unlink(tmp_path)

    if results:
        st.session_state.update({
            "results_ready"   : True,
            "annotated_frame" : results.get("annotated"),
            "last_counts"     : results["counts"],
            "last_total"      : results["total_count"],
            "last_illegal"    : results["illegal_count"],
            "last_occupancy"  : results["occupancy"],
            "last_congestion" : results["congestion"],
            "last_severity"   : results["severity"],
            "last_risk"       : results["risk"],
            "sign_zones"      : results["sign_zones"],
            "violations"      : results["violations"],
            "active_tracked"  : results["active_tracked"],
            "total_tracked"   : results["total_tracked"],
            "_resources"      : results["resources"],
            "_actions"        : results["actions"],
            "_density"        : results.get("density", 0),
        })

# ─────────────────────────────────────────────────────────────
# DISPLAY RESULTS
# ─────────────────────────────────────────────────────────────
if not st.session_state["results_ready"]:
    st.stop()

ann_frame    = st.session_state["annotated_frame"]
counts       = st.session_state["last_counts"]
total_veh    = st.session_state["last_total"]
illegal_n    = st.session_state["last_illegal"]
occupancy    = st.session_state["last_occupancy"]
congestion   = st.session_state["last_congestion"]
severity     = st.session_state["last_severity"]
risk         = st.session_state["last_risk"]
sign_zones   = st.session_state["sign_zones"]
violations   = st.session_state["violations"]
act_tracked  = st.session_state["active_tracked"]
tot_tracked  = st.session_state["total_tracked"]
resources    = st.session_state["_resources"]
actions      = st.session_state["_actions"]
density      = st.session_state["_density"]

# ─────────────────────────────────────────────────────────────
# SECTION 2 – ANNOTATED DETECTION VIEWER  (single output)
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🖼️ Annotated Detection Result</div>',
            unsafe_allow_html=True)

if ann_frame is not None:
    rgb_out = cv2.cvtColor(ann_frame, cv2.COLOR_BGR2RGB)
    st.image(rgb_out, use_container_width=True,
             caption="SmartPark AI – Final Annotated Frame")
else:
    st.info("No annotated output available.")

# Legend
st.markdown("""
<div style="display:flex; gap:1.5rem; margin:0.4rem 0 0.8rem; flex-wrap:wrap; font-size:0.83rem;">
    <span style="color:#00c800; font-weight:600;">■ Vehicle Detected</span>
    <span style="color:#dc2626; font-weight:600;">■ Illegal Parking</span>
    <span style="color:#ea580c; font-weight:600;">■ NO PARKING Zone</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="sp-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SECTION 3 – METRICS DASHBOARD
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Metrics Dashboard</div>', unsafe_allow_html=True)

r1 = st.columns(6)
with r1[0]: st.markdown(_metric("Total Vehicles", total_veh), unsafe_allow_html=True)
with r1[1]: st.markdown(_metric("Cars",  counts.get("car",0)), unsafe_allow_html=True)
with r1[2]: st.markdown(_metric("Buses", counts.get("bus",0)), unsafe_allow_html=True)
with r1[3]: st.markdown(_metric("Trucks",counts.get("truck",0)), unsafe_allow_html=True)
with r1[4]: st.markdown(_metric("Motorcycles",counts.get("motorcycle",0)), unsafe_allow_html=True)
with r1[5]: st.markdown(_metric("Illegal Vehicles", illegal_n, danger=illegal_n>0),
                        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

r2 = st.columns(6)
with r2[0]: st.markdown(_metric("Active Tracked",  act_tracked), unsafe_allow_html=True)
with r2[1]: st.markdown(_metric("Total Tracked",   tot_tracked), unsafe_allow_html=True)
with r2[2]: st.markdown(_metric(f"Occupancy ({occ_level(occupancy)})",
                                f"{occupancy:.1f}%"), unsafe_allow_html=True)
with r2[3]: st.markdown(_metric(f"Congestion ({cong_level(congestion)})",
                                f"{congestion:.1f}"), unsafe_allow_html=True)
with r2[4]: st.markdown(_metric(f"Severity ({sev_level(severity)})",
                                f"{severity:.1f}"), unsafe_allow_html=True)
with r2[5]: st.markdown(_metric(f"Risk ({risk_level(risk)})",
                                f"{risk:.1f}", danger=risk>60), unsafe_allow_html=True)

st.markdown('<hr class="sp-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# VIOLATIONS TABLE
# ─────────────────────────────────────────────────────────────
if violations:
    st.markdown('<div class="section-header">🚨 Illegal Parking Violations</div>',
                unsafe_allow_html=True)
    for v in violations:
        st.markdown(
            f'<div class="violation-row">'
            f'🚗 <b>Vehicle #{v["track_id"]}</b> ({v["label"].capitalize()}) '
            f'— Stationary <b>{v["duration"]:.1f}s</b> near NO PARKING sign'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<hr class="sp-divider">', unsafe_allow_html=True)

if sign_zones:
    st.markdown('<div class="section-header">🪧 NO PARKING Signs Detected</div>',
                unsafe_allow_html=True)
    for i, (sx1,sy1,sx2,sy2) in enumerate(sign_zones, 1):
        st.markdown(
            f'<div class="sign-row">'
            f'🪧 <b>Sign Zone #{i}</b> — ({sx1},{sy1}) → ({sx2},{sy2})'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<hr class="sp-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SECTION 4 – RESOURCE PLANNER
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🗂️ Enforcement Resource Planner</div>',
            unsafe_allow_html=True)
rc = st.columns(3)
with rc[0]: st.markdown(_resource("👮", resources.get("officers",1),    "Officers Recommended"), unsafe_allow_html=True)
with rc[1]: st.markdown(_resource("🚔", resources.get("patrol_vehicles",0),"Patrol Vehicles"),    unsafe_allow_html=True)
with rc[2]: st.markdown(_resource("🚛", resources.get("tow_trucks",0),  "Tow Trucks"),           unsafe_allow_html=True)

st.markdown('<hr class="sp-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SECTION 5 – ACTION RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">⚡ Action Recommendations</div>',
            unsafe_allow_html=True)
for priority, text in actions:
    st.markdown(f'<div class="action-card {priority}">{text}</div>',
                unsafe_allow_html=True)

st.markdown('<hr class="sp-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SECTION 6 – ANALYTICS CHARTS
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Analytics Charts</div>',
            unsafe_allow_html=True)

chart_l, chart_r = st.columns([1, 2])
with chart_l:
    st.plotly_chart(vehicle_distribution_chart(counts),
                    use_container_width=True, config={"displayModeBar":False})
with chart_r:
    gc = st.columns(3)
    with gc[0]:
        st.plotly_chart(_gauge("Congestion", congestion, 100,
                               [(33,"#16a34a"),(66,"#d97706"),(100,"#dc2626")]),
                        use_container_width=True, config={"displayModeBar":False})
    with gc[1]:
        st.plotly_chart(_gauge("Severity", severity, 100,
                               [(25,"#16a34a"),(50,"#d97706"),(75,"#ea580c"),(100,"#dc2626")]),
                        use_container_width=True, config={"displayModeBar":False})
    with gc[2]:
        st.plotly_chart(_gauge("Risk", risk, 100,
                               [(33,"#16a34a"),(66,"#d97706"),(100,"#dc2626")]),
                        use_container_width=True, config={"displayModeBar":False})

st.plotly_chart(score_bar_chart(density, occupancy, congestion, severity, risk),
                use_container_width=True, config={"displayModeBar":False})

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<hr class="sp-divider">
<div style="text-align:center; color:#94a3b8; font-size:0.76rem; padding:0.4rem 0 1rem;">
    CyberStorm &copy; 2026 &nbsp;·&nbsp; Powered by YOLOv8 &amp; Streamlit
    &nbsp;·&nbsp; All analytics derived from real detections
</div>
""", unsafe_allow_html=True)
