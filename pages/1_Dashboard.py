import streamlit as st
import pandas as pd
import plotly.express as px
import ast
from pathlib import Path

from utils.download_assets import download_assets
from utils.theme import apply_theme

st.set_page_config(
    page_title="SmartPark Dashboard",
    page_icon="📊",
    layout="wide"
)

download_assets()
apply_theme()

# =====================================
# LOAD DATA
# =====================================

@st.cache_data
def load_data():

    csv_path = (
        Path(__file__).parent.parent
        / "data"
        / "parking_violations.csv"
    )

    df = pd.read_csv(csv_path)

    def extract_primary_violation(x):
        try:
            parsed = ast.literal_eval(str(x))
            if isinstance(parsed, list):
                return str(parsed[0])
            return str(parsed)
        except:
            return str(x)

    df["primary_violation"] = (
        df["violation_type"]
        .fillna("Unknown")
        .apply(extract_primary_violation)
    )

    return df

df = load_data()

# =====================================
# TITLE
# =====================================

st.title("📊 SmartPark Dashboard")

st.info("""
### Key Insights

• 298,450 parking violations analyzed

• Safina Plaza and KR Market are major congestion hotspots

• Cars, Scooters and Passenger Autos contribute most violations

• Parking violations directly impact road capacity and congestion
""")

# =====================================
# KPI CARDS
# =====================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Violations",
        f"{len(df):,}"
    )

with col2:
    st.metric(
        "Police Stations",
        df["police_station"].nunique()
    )

with col3:
    st.metric(
        "Junctions",
        df["junction_name"].nunique()
    )

with col4:
    st.metric(
        "Vehicle Types",
        df["vehicle_type"].nunique()
    )

st.divider()
# =====================================
# CITY RISK INDEX
# =====================================

st.subheader("🛡️ City Risk Index")

risk_score = min(
    100,
    int(
        (
            len(df) / 300000
        ) * 100
    )
)

if risk_score >= 80:

    risk_status = "🔴 HIGH"

elif risk_score >= 60:

    risk_status = "🟠 MODERATE"

else:

    risk_status = "🟢 LOW"


c1, c2 = st.columns(2)

with c1:

    st.metric(
        "City Risk Index",
        f"{risk_score}/100"
    )

with c2:

    st.metric(
        "Risk Status",
        risk_status
    )

# =====================================
# AI CITY HEALTH SCORE
# =====================================

st.divider()

st.subheader(
    "🧠 AI City Health Score"
)

health_score = max(
    0,
    100 - risk_score
)

if health_score >= 80:

    health_status = "🟢 EXCELLENT"

elif health_score >= 60:

    health_status = "🟡 GOOD"

elif health_score >= 40:

    health_status = "🟠 FAIR"

else:

    health_status = "🔴 POOR"

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "City Health Score",
        f"{health_score}/100"
    )

with c2:

    st.metric(
        "Health Status",
        health_status
    )

st.info(
    f"🏙️ Overall Parking Ecosystem Health: **{health_status}**"
)
# =====================================
# VIOLATION SEVERITY INDEX
# =====================================

st.divider()

st.subheader("🔥 Violation Severity Index")

severity_map = {

    "WRONG PARKING": 90,

    "NO PARKING": 85,

    "PARKING IN A MAIN ROAD": 75,

    "PARKING ON FOOTPATH": 65,

    "DEFECTIVE NUMBER PLATE": 30

}

df["severity_score"] = df[
    "primary_violation"
].map(
    severity_map
).fillna(50)

avg_severity = int(
    df["severity_score"].mean()
)

if avg_severity >= 80:

    severity_status = "🔴 CRITICAL"

elif avg_severity >= 60:

    severity_status = "🟠 HIGH"

elif avg_severity >= 40:

    severity_status = "🟡 MODERATE"

else:

    severity_status = "🟢 LOW"

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Average Severity Score",
        f"{avg_severity}/100"
    )

with c2:

    st.metric(
        "Severity Level",
        severity_status
    )

st.info(
    f"🚨 Citywide Violation Severity Assessment: {severity_status}"
)
# =====================================
# ENFORCEMENT EFFICIENCY SCORE
# =====================================

st.divider()

st.subheader(
    "🚔 Enforcement Efficiency Score"
)

total_stations = df[
    "police_station"
].nunique()

total_junctions = df[
    "junction_name"
].nunique()

efficiency_score = min(
    100,
    int(
        (
            total_stations /
            max(total_junctions, 1)
        ) * 500
    )
)

if efficiency_score >= 80:

    enforcement_status = "🟢 EXCELLENT"

elif efficiency_score >= 60:

    enforcement_status = "🟡 GOOD"

elif efficiency_score >= 40:

    enforcement_status = "🟠 MODERATE"

else:

    enforcement_status = "🔴 POOR"

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Efficiency Score",
        f"{efficiency_score}/100"
    )

with c2:

    st.metric(
        "Enforcement Status",
        enforcement_status
    )

st.info(
    f"🚓 Enforcement Performance Assessment: {enforcement_status}"
)
# =====================================
# SMART CAPACITY UTILIZATION
# =====================================

st.divider()

st.subheader(
    "🚗 Smart Capacity Utilization"
)

capacity_score = min(
    100,
    int(
        avg_severity * 0.6
        +
        risk_score * 0.4
    )
)

utilization = capacity_score

if utilization >= 80:

    utilization_status = "🔴 OVERLOADED"

elif utilization >= 60:

    utilization_status = "🟠 HIGH"

elif utilization >= 40:

    utilization_status = "🟡 MODERATE"

else:

    utilization_status = "🟢 HEALTHY"

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Capacity Utilization",
        f"{utilization}%"
    )

with c2:

    st.metric(
        "Utilization Status",
        utilization_status
    )

st.info(
    f"🚗 Parking Infrastructure Status: {utilization_status}"
)
# =====================================
# AI EXECUTIVE SUMMARY
# =====================================

st.divider()

st.subheader(
    "🚨 AI Executive Summary"
)

top_violation = (
    df["primary_violation"]
    .value_counts()
    .idxmax()
)

top_hotspot = (
    df[
        df["junction_name"].fillna("") != "No Junction"
    ]["junction_name"]
    .value_counts()
    .idxmax()
)

summary_text = f"""
### SmartPark AI Assessment

• Total Violations Analyzed: {len(df):,}

• Highest Risk Violation:
{top_violation}

• Most Congested Hotspot:
{top_hotspot}

• City Health Score:
{health_score}/100

• Enforcement Efficiency:
{efficiency_score}/100

• Capacity Utilization:
{utilization}%

### Recommended Action

Increase enforcement around high-risk hotspots.

Deploy patrol units to major violation zones.

Optimize parking allocation in overloaded regions.

Continuous monitoring recommended.
"""

st.info(summary_text)
# =====================================
# TOP VIOLATIONS
# =====================================

st.subheader("🚫 Top Violation Types")

violations = (
    df["primary_violation"]
    .value_counts()
    .head(5)
    .reset_index()
)

violations.columns = [
    "Violation Type",
    "Count"
]

fig1 = px.bar(
    violations,
    x="Count",
    y="Violation Type",
    orientation="h",
    title="Top Violation Categories"
)

fig1.update_layout(
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.divider()

# =====================================
# HOTSPOTS
# =====================================

st.subheader("📍 Top Congestion Hotspots")

hotspots = (
    df[
        df["junction_name"].fillna("") != "No Junction"
    ]["junction_name"]
    .value_counts()
    .head(10)
    .reset_index()
)

hotspots.columns = [
    "Junction",
    "Violations"
]

fig2 = px.bar(
    hotspots,
    x="Violations",
    y="Junction",
    orientation="h",
    title="Top Parking Congestion Hotspots"
)

fig2.update_layout(
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.divider()

# =====================================
# POLICE STATIONS
# =====================================

st.subheader("👮 Top Police Stations")

stations = (
    df["police_station"]
    .fillna("Unknown")
    .value_counts()
    .head(10)
    .reset_index()
)

stations.columns = [
    "Police Station",
    "Violations"
]

fig3 = px.bar(
    stations,
    x="Violations",
    y="Police Station",
    orientation="h",
    title="Most Active Enforcement Areas"
)

fig3.update_layout(
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.divider()

# =====================================
# VEHICLE DISTRIBUTION
# =====================================

st.subheader("🚗 Vehicle Distribution")

vehicles = (
    df["vehicle_type"]
    .fillna("Unknown")
    .value_counts()
    .head(8)
    .reset_index()
)

vehicles.columns = [
    "Vehicle",
    "Count"
]

fig4 = px.pie(
    vehicles,
    names="Vehicle",
    values="Count",
    title="Vehicle Type Distribution"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.divider()

# =====================================
# DATASET SUMMARY
# =====================================

st.subheader("📈 Dataset Summary")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Unique Violations",
        df["primary_violation"].nunique()
    )

with c2:
    st.metric(
        "Unique Junctions",
        df["junction_name"].nunique()
    )

with c3:
    st.metric(
        "Unique Vehicle Types",
        df["vehicle_type"].nunique()
    )
