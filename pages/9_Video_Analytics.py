import streamlit as st
# ── cv2 headless-safe import (fixes libxcb.so.1 error on Railway/Linux) ──
import os as _os
_os.environ.setdefault("DISPLAY", "")
_os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    import cv2
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "opencv-python-headless", "--quiet"])
    import cv2
import tempfile
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.download_assets import download_assets
from utils.theme import apply_theme
from utils.yolo_detector import (
    detect_vehicles,
    track_vehicles
)

from utils.parking_detector import (
    update_vehicle,
    check_illegal_parking
)

from utils.congestion_engine import calculate_congestion

st.set_page_config(
    page_title="Traffic Vision AI",
    layout="wide"
)

download_assets()
apply_theme()


# =====================================================
# PAGE CONFIG
# =====================================================



# =====================================================
# HEADER
# =====================================================

st.title("🎥 SmartPark AI Vision Analytics")

st.markdown("""
Upload a traffic image or video.

✅ Detect Vehicles

✅ Count Cars, Buses, Trucks & Motorcycles

✅ Analyze Road Occupancy

✅ Analyze Traffic Density

✅ Estimate Congestion

✅ Generate AI Recommendations
""")

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "Upload Traffic Image or Video",
    type=[
        "jpg", "jpeg", "png", "webp",
        "bmp", "tiff",
        "mp4", "mov", "avi",
        "wmv", "webm", "mkv",
        "mpeg", "mpg", "m4v"
    ]
)

# =====================================================
# PROCESS FILE
# =====================================================

if uploaded_file is not None:

    filename = uploaded_file.name.lower()

    image_ext = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tiff"
    )

    video_ext = (
        ".mp4",
        ".mov",
        ".avi",
        ".wmv",
        ".webm",
        ".mkv",
        ".mpeg",
        ".mpg",
        ".m4v"
    )

    # =================================================
    # IMAGE ANALYSIS
    # =================================================

    if filename.endswith(image_ext):

        file_bytes = np.asarray(
            bytearray(uploaded_file.read()),
            dtype=np.uint8
        )

        image = cv2.imdecode(
            file_bytes,
            cv2.IMREAD_COLOR
        )

        (
            annotated,
            total_count,
            counts,
            detected_boxes
        ) = detect_vehicles(image)
        for vehicle in detected_boxes:

            x1, y1, x2, y2 = vehicle["bbox"]

            label = vehicle["label"]

            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                3
            )

            cv2.putText(
                annotated,
                label.upper(),
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        (
            density_score,
            occupancy_percent,
            congestion_score
        ) = calculate_congestion(
            image,
            detected_boxes
        )

        st.subheader("🚗 Detected Vehicles")

        st.image(
            cv2.cvtColor(
                annotated,
                cv2.COLOR_BGR2RGB
            ),
            use_container_width=True
        )

    # =================================================
    # VIDEO ANALYSIS
    # =================================================

    elif filename.endswith(video_ext):

        temp_file = tempfile.NamedTemporaryFile(
            delete=False
        )

        temp_file.write(
            uploaded_file.read()
        )

        video_path = temp_file.name

        cap = cv2.VideoCapture(video_path)

        frame_count = 0

        total_count = 0

        all_boxes = []

        counts = {
            "car": 0,
            "bus": 0,
            "truck": 0,
            "motorcycle": 0
        }

        preview = st.empty()

        progress = st.progress(0)

        total_frames = int(
            cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        last_frame = None

        illegal_vehicle_ids = set()

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            frame_count += 1

            if frame_count % 30 != 0:
                continue

            annotated, tracked_vehicles = track_vehicles(frame)

            frame_total = len(tracked_vehicles)

            frame_boxes = []

            frame_counts = {
                "car": 0,
                "bus": 0,
                "truck": 0,
                "motorcycle": 0
            }

            for vehicle in tracked_vehicles:

                track_id = vehicle["track_id"]

                label = vehicle["label"]

                center = vehicle["center"]

                update_vehicle(
                    track_id,
                    center
                )

                violation, duration = check_illegal_parking(
                    track_id,
                    fps=30,
                    threshold_seconds=5
                )

                if label in frame_counts:
                    frame_counts[label] += 1

                frame_boxes.append(
                    vehicle["bbox"]
                )
                x1, y1, x2, y2 = vehicle["bbox"]

                # Draw GREEN box for every detected vehicle
                cv2.rectangle(
                    annotated,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                annotated,
                f"{label} #{track_id}",
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
                

                if violation:

                    illegal_vehicle_ids.add(
                        track_id
                    )

                    x1, y1, x2, y2 = vehicle["bbox"]

                    cv2.rectangle(
                        annotated,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
                        3
                    )

                    cv2.putText(
                        annotated,
                        f"ILLEGAL {duration:.1f}s",
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

            last_frame = frame

            total_count += frame_total

            all_boxes.extend(
                frame_boxes
            )

            for k in counts:

                counts[k] += frame_counts[k]

            preview.image(
                cv2.cvtColor(
                    annotated,
                    cv2.COLOR_BGR2RGB
                ),
                use_container_width=True
            )

            if total_frames > 0:

                progress.progress(
                    min(
                        frame_count /
                        total_frames,
                        1.0
                    )
                )

            cap.release()

        illegal_vehicle_count = len(
            illegal_vehicle_ids
        )

        st.session_state[
            "illegal_vehicles"
        ] = illegal_vehicle_count

        if last_frame is not None:

            (
                density_score,
                occupancy_percent,
                congestion_score
            ) = calculate_congestion(
                last_frame,
                all_boxes
            )

        else:

            density_score = 0
            occupancy_percent = 0
            congestion_score = 0

    

    # =================================================
    # RISK LEVEL
    # =================================================

    if congestion_score >= 80:

        risk_level = "🔴 CRITICAL"
        severity = "SEVERE TRAFFIC"

    elif congestion_score >= 60:

        risk_level = "🟠 HIGH"
        severity = "HEAVY TRAFFIC"

    elif congestion_score >= 40:

        risk_level = "🟡 MEDIUM"
        severity = "MODERATE TRAFFIC"

    else:

        risk_level = "🟢 LOW"
        severity = "LIGHT TRAFFIC"

    # =================================================
    # KPI METRICS
    # =================================================

    st.divider()

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Vehicles Detected",
            total_count
        )

    with c2:
        st.metric(
            "Congestion Score",
            f"{congestion_score}/100"
        )

    with c3:
        st.metric(
            "Risk Level",
            risk_level
        )

    with c4:
        st.metric(
            "Road Occupancy",
            f"{occupancy_percent}%"
        )

    with c5:
        st.metric(
            "Traffic Density",
            f"{density_score}%"
        )
    st.info(
        f"🚦 Traffic Severity: **{severity}**"
    )

    # =================================================
    # CONGESTION GAUGE
    # =================================================

    st.subheader("🚦 Congestion Gauge")

    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=congestion_score,
            title={
                "text": "Traffic Congestion"
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                },
                "bar": {
                    "color": "white"
                },
                "steps": [
                    {
                        "range": [0, 40],
                        "color": "green"
                    },
                    {
                        "range": [40, 60],
                        "color": "yellow"
                    },
                    {
                        "range": [60, 80],
                        "color": "orange"
                    },
                    {
                        "range": [80, 100],
                        "color": "red"
                    }
                ]
            }
        )
    )

    gauge_fig.update_layout(
        height=350
    )

    st.plotly_chart(
        gauge_fig,
        use_container_width=True
    )
        # =================================================
    # TRAFFIC HEALTH SCORE
    # =================================================

    st.subheader("📈 Traffic Health Score")

    health_score = max(
        0,
        100 - congestion_score
    )

    if health_score >= 80:

        health_status = "🟢 Excellent"

    elif health_score >= 60:

        health_status = "🟡 Good"

    elif health_score >= 40:

        health_status = "🟠 Moderate"

    else:

        health_status = "🔴 Poor"

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Traffic Health Score",
            f"{health_score}/100"
        )

    with col2:

        st.metric(
            "Traffic Condition",
            health_status
        )

    st.divider()
        # =================================================
    # TRAFFIC MANAGEMENT PRIORITY
    # =================================================

    st.subheader(
        "🏆 Traffic Management Priority"
    )

    if congestion_score >= 80:

        st.error("""
🔴 CRITICAL PRIORITY

Immediate intervention required

• Deploy emergency traffic team

• Activate diversion routes

• Continuous monitoring required
""")

    elif congestion_score >= 60:

        st.warning("""
🟠 HIGH PRIORITY

Deploy 5 traffic officers

• Tow support recommended

• Monitor continuously
""")

    elif congestion_score >= 40:

        st.info("""
🟡 MEDIUM PRIORITY

Deploy 2 traffic officers

• Monitor traffic flow

• Optimize signals
""")

    else:

        st.success("""
🟢 LOW PRIORITY

Routine monitoring sufficient

• Normal traffic conditions
""")

    st.divider()
        # =================================================
    # TRAFFIC TREND INDICATOR
    # =================================================

    st.subheader(
        "📈 Traffic Trend Indicator"
    )

    if congestion_score >= 70:

        trend_icon = "📉"
        trend_status = "Worsening"

        st.error("""
📉 WORSENING

Traffic congestion is increasing.

Immediate monitoring recommended.
""")

    elif congestion_score >= 40:

        trend_icon = "📊"
        trend_status = "Stable"

        st.warning("""
📊 STABLE

Traffic conditions are steady.

Continue monitoring.
""")

    else:

        trend_icon = "📈"
        trend_status = "Improving"

        st.success("""
📈 IMPROVING

Traffic conditions are improving.

Normal flow detected.
""")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Trend Status",
            trend_status
        )

    with col2:

        st.metric(
            "Trend Indicator",
            trend_icon
        )

    st.divider()
        # =================================================
    # PEAK HOUR ANALYSIS
    # =================================================

    st.subheader(
        "🚦 Peak Hour Analysis"
    )

    if total_count >= 100:

        peak_status = "🔴 PEAK HOUR"

        st.error("""
🔴 PEAK HOUR DETECTED

Traffic volume is extremely high.

Additional traffic control recommended.
""")

    elif total_count >= 50:

        peak_status = "🟡 MODERATE FLOW"

        st.warning("""
🟡 MODERATE TRAFFIC FLOW

Traffic volume is above average.

Monitor continuously.
""")

    else:

        peak_status = "🟢 NON-PEAK HOUR"

        st.success("""
🟢 NORMAL TRAFFIC FLOW

Traffic volume is within normal limits.
""")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Vehicles Observed",
            total_count
        )

    with c2:

        st.metric(
            "Peak Status",
            peak_status
        )

    st.divider()
        # =================================================
    # INCIDENT PROBABILITY DETECTION
    # =================================================

    st.subheader(
        "🚨 Incident Probability Detection"
    )

    incident_score = int(
        (
            congestion_score +
            density_score +
            occupancy_percent
        ) / 3
    )

    if incident_score >= 70:

        incident_level = "🔴 HIGH"

        st.error("""
🔴 HIGH INCIDENT RISK

Traffic conditions indicate a high
probability of accidents.

Immediate intervention recommended.
""")

    elif incident_score >= 40:

        incident_level = "🟡 MEDIUM"

        st.warning("""
🟡 MEDIUM INCIDENT RISK

Traffic conditions require
continuous monitoring.
""")

    else:

        incident_level = "🟢 LOW"

        st.success("""
🟢 LOW INCIDENT RISK

Traffic conditions are stable.

Accident probability is low.
""")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Incident Risk",
            incident_level
        )

    with c2:

        st.metric(
            "Probability",
            f"{incident_score}%"
        )

    st.divider()
        # =================================================
    # EMERGENCY RESPONSE RECOMMENDATION
    # =================================================

    st.subheader(
        "🚑 Emergency Response System"
    )

    emergency_score = int(
        (
            congestion_score +
            incident_score
        ) / 2
    )

    if emergency_score >= 80:

        police = 8
        tow = 3
        ambulance = 2
        priority = "🔴 CRITICAL"

        st.error("""
🔴 CRITICAL EMERGENCY

Immediate response required.

Deploy maximum resources.
""")

    elif emergency_score >= 60:

        police = 6
        tow = 2
        ambulance = 1
        priority = "🟠 HIGH"

        st.warning("""
🟠 HIGH PRIORITY

Heavy traffic conditions.

Deploy additional emergency units.
""")

    elif emergency_score >= 40:

        police = 4
        tow = 1
        ambulance = 1
        priority = "🟡 MODERATE"

        st.info("""
🟡 MODERATE PRIORITY

Monitor traffic continuously.

Prepare emergency resources.
""")

    else:

        police = 2
        tow = 0
        ambulance = 0
        priority = "🟢 NORMAL"

        st.success("""
🟢 NORMAL CONDITIONS

Routine monitoring sufficient.
""")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "👮 Traffic Police",
            police
        )

    with c2:
        st.metric(
            "🚛 Tow Trucks",
            tow
        )

    with c3:
        st.metric(
            "🚑 Ambulances",
            ambulance
        )

    with c4:
        st.metric(
            "Priority",
            priority
        )

    st.divider()
        # =================================================
    # DYNAMIC TRAFFIC SIGNAL TIMING
    # =================================================

    st.subheader(
        "🚦 Smart Traffic Signal Timing"
    )

    signal_score = int(
        (
            congestion_score +
            incident_score +
            emergency_score
        ) / 3
    )

    if signal_score >= 80:

        green_time = 120
        cycle_time = 240
        mode = "🔴 CRITICAL"

        st.error("""
🔴 CRITICAL TRAFFIC

Maximum green signal required.

Activate traffic optimization.
""")

    elif signal_score >= 60:

        green_time = 90
        cycle_time = 180
        mode = "🟠 HIGH"

        st.warning("""
🟠 HIGH TRAFFIC

Increase green signal duration.

Reduce vehicle waiting time.
""")

    elif signal_score >= 40:

        green_time = 60
        cycle_time = 120
        mode = "🟡 MODERATE"

        st.info("""
🟡 MODERATE TRAFFIC

Normal adaptive signal timing.

Continue monitoring.
""")

    else:

        green_time = 30
        cycle_time = 60
        mode = "🟢 NORMAL"

        st.success("""
🟢 NORMAL TRAFFIC

Standard signal timing sufficient.
""")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "🚦 Green Time",
            f"{green_time} sec"
        )

    with c2:
        st.metric(
            "🔄 Cycle Time",
            f"{cycle_time} sec"
        )

    with c3:
        st.metric(
            "Traffic Mode",
            mode
        )

    st.divider()
        # =================================================
    # SMART ROUTE DIVERSION
    # =================================================

    st.subheader(
        "🛣 Smart Route Diversion"
    )

    diversion_score = int(
        (
            congestion_score +
            incident_score +
            emergency_score +
            signal_score
        ) / 4
    )

    if diversion_score >= 80:

        diversion_percent = 50
        alternate_routes = 3
        status = "🔴 ACTIVE"
        support = "REQUIRED"

        st.error("""
🔴 DIVERSION REQUIRED

Severe congestion detected.

Activate all alternate routes.
""")

    elif diversion_score >= 60:

        diversion_percent = 35
        alternate_routes = 2
        status = "🟠 ACTIVE"
        support = "REQUIRED"

        st.warning("""
🟠 DIVERSION RECOMMENDED

Heavy congestion detected.

Use alternate traffic routes.
""")

    elif diversion_score >= 40:

        diversion_percent = 20
        alternate_routes = 1
        status = "🟡 PARTIAL"
        support = "OPTIONAL"

        st.info("""
🟡 PARTIAL DIVERSION

Moderate traffic.

Prepare alternate routes.
""")

    else:

        diversion_percent = 0
        alternate_routes = 0
        status = "🟢 NORMAL"
        support = "NOT REQUIRED"

        st.success("""
🟢 NORMAL TRAFFIC

No diversion required.
""")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🚗 Diversion Rate",
            f"{diversion_percent}%"
        )

    with c2:
        st.metric(
            "🛣 Alternate Routes",
            alternate_routes
        )

    with c3:
        st.metric(
            "🚦 Diversion Status",
            status
        )

    with c4:
        st.metric(
            "👮 Police Support",
            support
        )

    st.divider()
        # =================================================
    # SMART PARKING AVAILABILITY
    # =================================================

    st.subheader(
        "🅿️ Smart Parking Availability"
    )

    parking_score = int(
        (
            total_count +
            congestion_score +
            density_score +
            diversion_score
        ) / 4
    )

    if parking_score >= 80:

        available_slots = 10
        occupancy = 95
        parking_status = "🔴 FULL"
        overflow = "HIGH"

        st.error("""
🔴 PARKING FULL

Parking demand extremely high.

Redirect vehicles to alternate parking zones.
""")

    elif parking_score >= 60:

        available_slots = 25
        occupancy = 80
        parking_status = "🟠 LIMITED"
        overflow = "MEDIUM"

        st.warning("""
🟠 LIMITED PARKING

Parking demand increasing.

Consider alternate parking locations.
""")

    elif parking_score >= 40:

        available_slots = 50
        occupancy = 60
        parking_status = "🟡 AVAILABLE"
        overflow = "LOW"

        st.info("""
🟡 PARKING AVAILABLE

Parking capacity sufficient.

Continue monitoring.
""")

    else:

        available_slots = 80
        occupancy = 30
        parking_status = "🟢 FREE"
        overflow = "NONE"

        st.success("""
🟢 PARKING AVAILABLE

Parking capacity is healthy.
""")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🅿️ Available Slots",
            available_slots
        )

    with c2:
        st.metric(
            "🚗 Occupancy",
            f"{occupancy}%"
        )

    with c3:
        st.metric(
            "📍 Parking Status",
            parking_status
        )

    with c4:
        st.metric(
            "⚠️ Overflow Risk",
            overflow
        )

    st.divider()

    st.divider()
        # =================================================
    # SMART TRAFFIC ALERTS
    # =================================================

    st.subheader("🚨 Smart Traffic Alerts")

    alerts = []

    if congestion_score >= 80:
        alerts.append(
            "🚨 CRITICAL TRAFFIC ALERT - Immediate intervention required"
        )

    elif congestion_score >= 60:
        alerts.append(
            "⚠ HIGH CONGESTION ALERT - Traffic flow severely impacted"
        )

    if occupancy_percent >= 40:
        alerts.append(
            f"⚠ Road Occupancy High ({occupancy_percent:.1f}%)"
        )

    if density_score >= 70:
        alerts.append(
            f"⚠ Traffic Density Critical ({density_score:.1f}%)"
        )

    if counts["truck"] >= 5:
        alerts.append(
            f"🚚 High Truck Presence Detected ({counts['truck']} trucks)"
        )

    if counts["bus"] >= 3:
        alerts.append(
            f"🚌 Heavy Bus Activity Detected ({counts['bus']} buses)"
        )

    if len(alerts) == 0:

        st.success(
            "✅ No active traffic alerts. Traffic conditions are normal."
        )

    else:

        for alert in alerts:

            st.warning(alert)

    st.divider()
    # =================================================
    # VEHICLE BREAKDOWN
    # =================================================

    st.subheader("🚗 Vehicle Breakdown")

    vehicle_df = pd.DataFrame({

        "Vehicle": [
            "Cars",
            "Buses",
            "Trucks",
            "Motorcycles"
        ],

        "Count": [
            counts["car"],
            counts["bus"],
            counts["truck"],
            counts["motorcycle"]
        ]
    })

    st.dataframe(
        vehicle_df,
        use_container_width=True
    )
    # =================================================
    # VEHICLE DISTRIBUTION
    # =================================================

    st.subheader("📊 Vehicle Distribution")

    chart_df = vehicle_df.copy()

    chart_df = chart_df[
        chart_df["Count"] > 0
    ]

    if not chart_df.empty:

        fig = px.bar(
            chart_df,
            x="Vehicle",
            y="Count",
            text="Count",
            title="Detected Vehicles",
            color="Vehicle",
            color_discrete_map={
                "Cars": "#3498db",
                "Buses": "#f39c12",
                "Trucks": "#e74c3c",
                "Motorcycles": "#2ecc71"
            }
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            height=450,
            showlegend=False,
            xaxis_title="Vehicle Type",
            yaxis_title="Count"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =================================================
    # AI RECOMMENDATIONS
    # =================================================

    st.subheader("🤖 AI Recommendations")

    if congestion_score >= 80:

        st.error("""
• Severe traffic congestion detected

• Deploy 7 traffic officers

• Deploy 3 tow trucks

• Activate diversion routes

• Continuous monitoring required
""")

    elif congestion_score >= 60:

        st.warning("""
• High congestion detected

• Deploy 5 traffic officers

• Deploy 2 tow trucks

• Increase enforcement patrol

• Monitor bottlenecks continuously
""")

    elif congestion_score >= 40:

        st.info("""
• Moderate congestion

• Deploy 3 traffic officers

• Continue monitoring

• Optimize signal timing
""")

    else:

        st.success("""
• Traffic flow normal

• Standard monitoring sufficient

• Routine patrol recommended
""")
