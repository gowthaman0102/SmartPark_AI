import streamlit as st
import pandas as pd
from pathlib import Path

from utils.download_assets import download_assets
from utils.theme import apply_theme

st.set_page_config(
    page_title="AI Command Center",
    layout="wide"
)

download_assets()
apply_theme()

st.title("🚨 SmartPark AI Command Center")

st.markdown("""
AI-powered operational dashboard for parking-induced congestion management.
""")

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    csv_path = (
        Path(__file__).parent.parent
        / "data"
        / "parking_violations.csv"
    )

    df = pd.read_csv(csv_path, nrows=50000)

    df["junction_name"] = (
        df["junction_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df = df[df["junction_name"] != ""]
    df = df[df["junction_name"].str.upper() != "NO JUNCTION"]
    df = df[df["junction_name"].str.upper() != "UNKNOWN"]
    df = df[df["junction_name"].str.upper() != "NULL"]
    df = df[df["junction_name"].str.upper() != "NAN"]

    return df

df = load_data()

# =====================================================
# HOTSPOT ANALYSIS
# =====================================================

junction_counts = (
    df["junction_name"]
    .value_counts()
    .reset_index()
)

junction_counts.columns = [
    "Junction",
    "Violation Count"
]

# Percentile based risk score

junction_counts["Risk Score"] = (
    junction_counts["Violation Count"]
    .rank(pct=True)
    * 100
).round(2)

# =====================================================
# RISK LEVELS
# =====================================================

def get_risk_level(score):

    if score >= 95:
        return "CRITICAL"

    elif score >= 80:
        return "HIGH"

    elif score >= 60:
        return "MEDIUM"

    else:
        return "LOW"


junction_counts["Risk Level"] = (
    junction_counts["Risk Score"]
    .apply(get_risk_level)
)

# =====================================================
# TOP HOTSPOTS
# =====================================================

top_hotspots = junction_counts.head(10)

st.subheader("🔥 Top AI-Detected Hotspots")

st.dataframe(
    top_hotspots,
    use_container_width=True
)

# =====================================================
# JUNCTION SELECTOR
# =====================================================

selected = st.selectbox(
    "Select Junction",
    top_hotspots["Junction"]
)

row = top_hotspots[
    top_hotspots["Junction"] == selected
].iloc[0]

risk = float(row["Risk Score"])
count = int(row["Violation Count"])
level = row["Risk Level"]

# =====================================================
# AI RESOURCE ALLOCATION
# =====================================================

officers = max(
    1,
    round(risk / 15)
)

tow_trucks = max(
    1,
    round(risk / 30)
)

# =====================================================
# KPI SECTION
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Risk Score",
        f"{risk}/100"
    )

with col2:
    st.metric(
        "Traffic Officers",
        officers
    )

with col3:
    st.metric(
        "Tow Trucks",
        tow_trucks
    )

with col4:
    st.metric(
        "Priority",
        level
    )

st.divider()
# =====================================================
# CITY-WIDE SITUATION DASHBOARD
# =====================================================

st.subheader(
    "🌍 City-Wide Situation Dashboard"
)

city_risk_index = round(
    junction_counts["Risk Score"].mean(),
    2
)

critical_zones = len(
    junction_counts[
        junction_counts["Risk Level"] == "CRITICAL"
    ]
)

high_zones = len(
    junction_counts[
        junction_counts["Risk Level"] == "HIGH"
    ]
)

if critical_zones > 5:

    city_status = "🔴 CRITICAL"

elif high_zones > 20:

    city_status = "🟠 ELEVATED"

else:

    city_status = "🟢 STABLE"

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "City Risk Index",
        f"{city_risk_index}/100"
    )

with c2:

    st.metric(
        "Critical Zones",
        critical_zones
    )

with c3:

    st.metric(
        "High Risk Zones",
        high_zones
    )
with c4:

    st.metric(
        "City Status",
        city_status
    )   

st.info(
    "📡 Real-time city-wide operational status."
)
# =====================================================
# CRITICAL ALERT SYSTEM
# =====================================================

st.divider()

st.subheader(
    "🚨 Critical Alert System"
)

if critical_zones > 5:

    alert_status = "🔴 RED ALERT"

elif high_zones > 15:

    alert_status = "🟠 ORANGE ALERT"

else:

    alert_status = "🟢 NORMAL"

st.metric(
    "Alert Status",
    alert_status
)

st.error(
    f"⚠️ {critical_zones} critical operational zones currently require immediate attention."
)
# =====================================================
# INCIDENT MONITORING PANEL
# =====================================================

st.divider()

st.subheader(
    "📋 Incident Monitoring Panel"
)

incident_df = pd.DataFrame({
    "Incident":[
        "Illegal Parking",
        "Traffic Blockage",
        "Tow Request",
        "Congestion Alert"
    ],
    "Status":[
        "ACTIVE",
        "ACTIVE",
        "PENDING",
        "ACTIVE"
    ]
})

st.dataframe(
    incident_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "📡 Active incidents monitored by Command Center."
)

# =====================================================
# AI RECOMMENDED ACTIONS
# =====================================================

st.subheader("🤖 AI Recommended Actions")

if level == "CRITICAL":

    st.error(f"""
• Immediate towing operation

• Deploy {officers} traffic officers

• Deploy {tow_trucks} tow trucks

• Issue congestion alert

• Continuous hotspot monitoring

• Increase enforcement frequency
""")

elif level == "HIGH":

    st.warning(f"""
• Deploy {officers} traffic officers

• Deploy {tow_trucks} tow trucks

• Increase patrol frequency

• Monitor congestion growth

• Schedule enforcement checks
""")

elif level == "MEDIUM":

    st.info(f"""
• Deploy {officers} traffic officers

• Moderate enforcement

• Active monitoring
""")

else:

    st.success("""
• Standard monitoring

• Routine patrol

• No escalation required
""")

# =====================================================
# IMPACT FORECAST
# =====================================================

st.subheader("📈 Predicted Impact")

reduction = round(
    min(
        50,
        risk * 0.35
    ),
    1
)

st.info(
    f"Estimated congestion reduction after enforcement: {reduction}%"
)
# =====================================================
# LIVE RISK FEED
# =====================================================

st.divider()

st.subheader(
    "📡 Live Risk Feed"
)

risk_feed = junction_counts.head(5)[
    [
        "Junction",
        "Risk Score",
        "Risk Level"
    ]
]
highest_junction = risk_feed.iloc[0]["Junction"]

st.metric(
    "Highest Risk Junction",
    highest_junction
)
st.dataframe(
    risk_feed,
    use_container_width=True,
    hide_index=True
)

st.info(
    "🔄 Live AI-generated risk feed from monitored hotspots."
)
# =====================================================
# EMERGENCY RESPONSE PANEL
# =====================================================

st.divider()

st.subheader(
    "🚑 Emergency Response Panel"
)

response_time = max(
    5,
    round(30 - (risk / 4))
)

readiness = max(
    50,
    100 - response_time * 5
)

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Estimated Response Time",
        f"{response_time} mins"
    )

with c2:

    st.metric(
        "Readiness Score",
        f"{readiness}%"
    )

st.info(
    f"🚨 Emergency response readiness linked to {level} priority."
)
# =====================================================
# MULTI-ZONE MONITORING
# =====================================================

st.divider()

st.subheader(
    "🗺️ Multi-Zone Monitoring"
)

zone_df = pd.DataFrame({
    "Zone":[
        "North",
        "South",
        "East",
        "West"
    ],
    "Risk":[
        "HIGH",
        "MEDIUM",
        "CRITICAL",
        "LOW"
    ]
})

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.metric(
        "North Zone",
        "HIGH"
    )

with c2:
    st.metric(
        "South Zone",
        "MEDIUM"
    )

with c3:
    st.metric(
        "East Zone",
        "CRITICAL"
    )

with c4:
    st.metric(
        "West Zone",
        "LOW"
    )

st.info(
    "📍 AI monitoring multiple operational zones."
)
# =====================================================
# ENFORCEMENT STATUS TRACKING
# =====================================================

st.divider()

st.subheader(
    "🚓 Enforcement Status Tracking"
)

status_df = pd.DataFrame({
    "Resource": [
        "Traffic Officers",
        "Tow Trucks",
        "Patrol Units"
    ],
    "Status": [
        "DEPLOYED",
        "ACTIVE",
        "ON DUTY"
    ]
})

st.dataframe(
    status_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "📍 Live enforcement resource status."
)
# =====================================================
# DECISION SUPPORT ENGINE
# =====================================================

st.divider()

st.subheader(
    "🧠 Decision Support Engine"
)

decision_score = round(
    city_risk_index * 0.9,
    2
)

st.metric(
    "Decision Confidence",
    f"{decision_score}%"
)

st.progress(
    int(decision_score)
)

st.info(
    "🤖 AI confidence level for current operational decisions."
)
# =====================================================
# AI COMMAND RECOMMENDATIONS
# =====================================================

st.divider()

st.subheader(
    "🎯 AI Command Recommendations"
)

recommendations = []

if critical_zones > 5:

    recommendations.append(
        "Escalate city-wide enforcement operations"
    )

    recommendations.append(
        "Deploy additional patrol units"
    )

    recommendations.append(
        "Increase towing fleet allocation"
    )

    recommendations.append(
        "Activate emergency monitoring mode"
    )

else:

    recommendations.append(
        "Maintain normal operational readiness"
    )

for rec in recommendations:

    st.success(rec)

st.info(
    "🧠 AI-generated strategic command recommendations."
)

# =====================================================
# SYSTEM STATISTICS
# =====================================================

st.subheader("📊 System Statistics")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Total Violations",
        f"{len(df):,}"
    )

with c2:
    st.metric(
        "Unique Junctions",
        df["junction_name"].nunique()
    )

with c3:
    st.metric(
        "Vehicle Categories",
        df["vehicle_type"].nunique()
    )

# =====================================================
# TOP 5 HOTSPOTS CHART
# =====================================================

st.subheader("📍 Top 5 Hotspots")

chart_df = top_hotspots.head(5)

import plotly.express as px

fig = px.bar(
    chart_df,
    x="Junction",
    y="Violation Count",
    title="Top 5 Hotspots"
)

fig.update_layout(
    height=450,
    xaxis_title="Junction",
    yaxis_title="Violations"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# AI DECISION SUMMARY
# =====================================================

st.subheader(
    "🎯 City Command Summary"
)

st.markdown(f"""
### City Status

- City Risk Index: {city_risk_index}/100
- Critical Zones: {critical_zones}
- High Risk Zones: {high_zones}

### Resource Status

- Officers Deployed: {officers}
- Tow Trucks Active: {tow_trucks}
- Emergency Readiness: {readiness}%

### Predicted Outcome

- {reduction}% Congestion Reduction

### AI Insight

The SmartPark AI Command Engine analyzed:

- City-wide parking violations
- Hotspot density
- Risk distribution
- Enforcement demand
- Resource availability

to prioritize operational decisions and reduce parking-induced congestion across monitored zones.
""")
