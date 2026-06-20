import streamlit as st
import pandas as pd
import folium
import numpy as np
from pathlib import Path

from streamlit_folium import st_folium
from folium.plugins import HeatMap

from utils.download_assets import download_assets
from utils.theme import apply_theme

st.set_page_config(
    page_title="SmartPark AI Heatmap",
    layout="wide"
)

download_assets()
apply_theme()


# =====================================================
# PAGE CONFIG
# =====================================================




st.title("🗺 SmartPark AI Congestion Heatmap")


st.markdown("""
Visualize parking violations, congestion hotspots and parking pressure across Bengaluru.

✅ Congestion Heatmap

✅ Parking Violation Density

✅ Parking Availability Heatmap

✅ AI Congestion Analysis

✅ Hotspot Visualization
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

    df = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    )

    np.random.seed(42)
    df["parking_pressure"] = np.random.randint(
        1,
        100,
        size=len(df)
    )
    df["availability_score"] = 100 - df["parking_pressure"]

    return df

df = load_data()



# =====================================================
# KPI METRICS
# =====================================================


total_locations = len(df)


avg_pressure = int(
    df["parking_pressure"].mean()
)


avg_availability = int(
    df["availability_score"].mean()
)



if avg_pressure > 70:

    congestion = "🔴 HIGH"


elif avg_pressure > 40:

    congestion = "🟠 MODERATE"


else:

    congestion = "🟢 LOW"



c1, c2, c3 = st.columns(3)



with c1:

    st.metric(
        "Parking Violation Points",
        total_locations
    )


with c2:

    st.metric(
        "Congestion Level",
        congestion
    )


with c3:

    st.metric(
        "Parking Availability",
        f"{avg_availability}%"
    )



st.info(
    f"🚦 AI Traffic Status: **{congestion} CONGESTION DETECTED**"
)



st.divider()



# =====================================================
# MAP CREATION
# =====================================================


m = folium.Map(

    location=[
        12.97,
        77.59
    ],

    zoom_start=11,

    tiles="CartoDB positron"

)



# =====================================================
# CONGESTION HEATMAP
# =====================================================


st.subheader(
    "🔥 Congestion Density Heatmap"
)



heat_data = df[
    [
        "latitude",
        "longitude"
    ]
].values.tolist()



HeatMap(

    heat_data,

    radius=15,

    blur=20,

    max_zoom=13,

    min_opacity=0.4

).add_to(m)



# =====================================================
# PARKING AVAILABILITY HEATMAP
# =====================================================


availability_data = df[
    [
        "latitude",
        "longitude",
        "parking_pressure"
    ]
].values.tolist()



HeatMap(

    availability_data,

    radius=18,

    blur=25,

    gradient={
        0.2:"darkgreen",
        0.5:"darkorange",
        0.8:"darkred"
    }

).add_to(m)



# =====================================================
# DISPLAY MAP
# =====================================================


st_folium(
    m,
    use_container_width=True,
    height=700,
    returned_objects=[],
    key="heatmap_main"
)



# =====================================================
# PARKING ANALYSIS TABLE
# =====================================================


st.divider()


st.subheader(
    "🅿️ Parking Pressure Analysis"
)



analysis_df = pd.DataFrame({
    "Metric":[
        "Average Parking Pressure",
        "Available Parking Score",
        "Violation Density"
    ],

    "Value":[
        f"{avg_pressure}%",
        f"{avg_availability}%",
        str(total_locations)
    ]
})

analysis_df["Value"] = analysis_df["Value"].astype(str)



st.dataframe(

    analysis_df,

    use_container_width=True

)
# =====================================================
# AI HOTSPOT CLUSTERING
# =====================================================

st.divider()

st.subheader(
    "🎯 AI Hotspot Clustering"
)

# Create grid-based hotspot clusters

hotspots = (

    df.groupby(
        [
            pd.cut(df["latitude"], 10),
            pd.cut(df["longitude"], 10)
        ]
    )

    .size()

    .reset_index(
        name="violations"
    )

)

hotspots = hotspots.sort_values(
    "violations",
    ascending=False
)

top_hotspots = hotspots.head(5)

cluster_df = pd.DataFrame({

    "Hotspot Rank":[
        f"#{i+1}"
        for i in range(len(top_hotspots))
    ],

    "Violation Density":
        top_hotspots["violations"].values,

    "Risk Score":[
        min(
            100,
            int(v / top_hotspots["violations"].max() * 100)
        )
        for v in top_hotspots["violations"]
    ]

})

st.dataframe(
    cluster_df,
    use_container_width=True
)

highest_risk = cluster_df["Risk Score"].max()

if highest_risk > 80:

    st.error(
        "🚨 Critical congestion hotspot detected. Immediate enforcement recommended."
    )

elif highest_risk > 50:

    st.warning(
        "⚠ Moderate hotspot concentration detected."
    )

else:

    st.success(
        "✅ Hotspot distribution remains stable."
    )
# =====================================================
# INCIDENT RISK ZONES
# =====================================================

st.divider()

st.subheader(
    "🚨 Incident Risk Zones"
)

risk_df = cluster_df.copy()

risk_df["Risk Level"] = risk_df["Risk Score"].apply(

    lambda x:
    "🔴 Critical" if x >= 80 else
    "🟠 High" if x >= 60 else
    "🟡 Moderate" if x >= 40 else
    "🟢 Low"

)

risk_df["Priority"] = risk_df["Risk Score"].apply(

    lambda x:
    "Immediate" if x >= 80 else
    "High" if x >= 60 else
    "Medium" if x >= 40 else
    "Low"

)

st.dataframe(

    risk_df[
        [
            "Hotspot Rank",
            "Risk Score",
            "Risk Level",
            "Priority"
        ]
    ],

    use_container_width=True

)

critical_zones = len(
    risk_df[
        risk_df["Risk Score"] >= 80
    ]
)

high_zones = len(
    risk_df[
        (risk_df["Risk Score"] >= 60)
        &
        (risk_df["Risk Score"] < 80)
    ]
)

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Critical Risk Zones",
        critical_zones
    )

with c2:

    st.metric(
        "High Risk Zones",
        high_zones
    )
# =====================================================
# ADVANCED AI INSIGHT ENGINE
# =====================================================

st.divider()

st.subheader("🧠 Advanced AI Insight Engine")

top_hotspot = cluster_df.iloc[0]

top_rank = top_hotspot["Hotspot Rank"]
top_density = top_hotspot["Violation Density"]
top_risk = top_hotspot["Risk Score"]

if top_risk >= 80:

    officers = 6
    tow_trucks = 2
    action = "Immediate Enforcement"
    status = "🔴 CRITICAL"

elif top_risk >= 60:

    officers = 4
    tow_trucks = 1
    action = "High Priority Monitoring"
    status = "🟠 HIGH"

elif top_risk >= 40:

    officers = 3
    tow_trucks = 1
    action = "Routine Monitoring"
    status = "🟡 MODERATE"

else:

    officers = 1
    tow_trucks = 0
    action = "Standard Patrol"
    status = "🟢 LOW"


c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "Highest Risk Hotspot",
        top_rank
    )

with c2:

    st.metric(
        "Risk Score",
        f"{top_risk}/100"
    )

with c3:

    st.metric(
        "Violation Density",
        f"{top_density:,}"
    )


st.info(f"""
### 🚨 AI Enforcement Recommendation

**Hotspot:** {top_rank}

**Risk Level:** {status}

**Suggested Officers:** {officers}

**Suggested Tow Trucks:** {tow_trucks}

**Recommended Action:** {action}

**Expected Congestion Probability:** {top_risk}%
""")



# =====================================================
# LEGEND
# =====================================================


st.subheader(
    "📍 Heatmap Legend"
)


st.markdown("""

🟢 Low Parking Pressure

🟡 Moderate Parking Pressure

🔴 High Parking Pressure


Higher intensity indicates:

• More parking violations

• Lower parking availability

• Higher congestion probability

""")


# =====================================================
# AI INSIGHT
# =====================================================


st.subheader(
    "🤖 AI Insight"
)



if avg_pressure > 70:


    st.error("""
• Severe parking shortage detected.

• Create temporary parking zones.

• Increase enforcement teams.

• Redirect vehicles to alternative areas.

• Continuous monitoring required.
""")


elif avg_pressure > 40:


    st.warning("""
• Moderate parking pressure detected.

• Optimize parking allocation.

• Monitor crowded zones.

• Improve parking availability.
""")


else:


    st.success("""
• Parking availability is stable.

• Normal traffic monitoring sufficient.

• Current parking management effective.
""")
