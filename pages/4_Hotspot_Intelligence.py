import streamlit as st
import pandas as pd
import plotly.express as px

from utils.download_assets import download_assets
from utils.theme import apply_theme

st.set_page_config(
    page_title="Hotspot Intelligence",
    layout="wide"
)

download_assets()
apply_theme()

st.title("🚨 Hotspot Intelligence Engine")

data = {
    "Junction":[
        "Safina Plaza Junction",
        "KR Market Junction",
        "Elite Junction",
        "Sagar Theatre Junction",
        "Central Street Junction"
    ],
    "Violations":[
        15449,
        11538,
        10718,
        10549,
        5388
    ]
}

df = pd.DataFrame(data)

df["Risk Score"] = (
    df["Violations"] /
    df["Violations"].max()
) * 100

def get_level(score):

    if score >= 80:
        return "CRITICAL"

    elif score >= 60:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    else:
        return "LOW"

df["Risk Level"] = df["Risk Score"].apply(get_level)

junction = st.selectbox(
    "Select Junction",
    df["Junction"]
)

selected = df[df["Junction"] == junction].iloc[0]

st.metric(
    "Risk Score",
    f"{selected['Risk Score']:.0f}/100"
)

st.metric(
    "Risk Level",
    selected["Risk Level"]
)

st.subheader("Recommended Action")

if selected["Risk Level"] == "CRITICAL":

    st.error("""
    • Immediate towing

    • Deploy traffic officers

    • Send congestion alert

    • Increase patrol frequency
    """)

elif selected["Risk Level"] == "HIGH":

    st.warning("""
    • Additional patrol

    • Monitor continuously

    • Issue warning notices
    """)

else:

    st.success("""
    • Normal monitoring
    """)
# =====================================
# TOP 10 HOTSPOTS RANKING
# =====================================

st.divider()

st.subheader(
    "🏆 Top 10 Hotspots Ranking"
)

ranking_df = df.sort_values(
    "Violations",
    ascending=False
)

ranking_df["Rank"] = range(
    1,
    len(ranking_df) + 1
)

st.dataframe(
    ranking_df[
        [
            "Rank",
            "Junction",
            "Violations",
            "Risk Score",
            "Risk Level"
        ]
    ],
    use_container_width=True
)

st.info(
    "📍 AI ranked hotspots based on historical congestion intensity."
)
# =====================================
# HOTSPOT SEVERITY INDEX
# =====================================

st.divider()

st.subheader(
    "🔥 Hotspot Severity Index"
)

severity_index = round(
    selected["Risk Score"] * 1.2,
    2
)

severity_index = min(
    severity_index,
    100
)

if severity_index >= 80:

    severity_status = "🔴 CRITICAL"

elif severity_index >= 60:

    severity_status = "🟠 HIGH"

elif severity_index >= 40:

    severity_status = "🟡 MEDIUM"

else:

    severity_status = "🟢 LOW"

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Severity Index",
        f"{severity_index}/100"
    )

with c2:

    st.metric(
        "Severity Level",
        severity_status
    )

st.info(
    f"🚨 Current hotspot severity classified as {severity_status}"
)
# =====================================
# HOTSPOT GROWTH RATE
# =====================================

st.divider()

st.subheader(
    "📈 Hotspot Growth Rate"
)

growth_rate = round(
    (selected["Risk Score"] / 100) * 25,
    2
)

if growth_rate >= 20:

    growth_status = "🔴 RAPID"

elif growth_rate >= 10:

    growth_status = "🟠 MODERATE"

else:

    growth_status = "🟢 STABLE"

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Growth Rate",
        f"{growth_rate}%"
    )

with c2:

    st.metric(
        "Growth Status",
        growth_status
    )

st.info(
    f"📊 Estimated hotspot growth trend: {growth_status}"
)


# =====================================
# RECURRING VIOLATION ZONES
# =====================================

st.divider()

st.subheader(
    "🔁 Recurring Violation Zones"
)

recurring_df = df.sort_values(
    "Violations",
    ascending=False
)[
    ["Junction", "Violations"]
]

st.dataframe(
    recurring_df,
    use_container_width=True
)

st.info(
    "🚓 These locations repeatedly appear as high-violation zones."
)


# =====================================
# EMERGING HOTSPOT DETECTION
# =====================================

st.divider()

st.subheader(
    "🚨 Emerging Hotspot Detection"
)

emerging_score = round(
    selected["Risk Score"] * 0.85,
    2
)

if emerging_score >= 70:

    emerging_status = "🔴 EMERGING"

elif emerging_score >= 40:

    emerging_status = "🟠 WATCHLIST"

else:

    emerging_status = "🟢 STABLE"

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Emerging Score",
        f"{emerging_score}/100"
    )

with c2:

    st.metric(
        "Detection Status",
        emerging_status
    )

st.info(
    f"📍 AI detected hotspot trend status: {emerging_status}"
)
# =====================================
# HOTSPOT COMPARISON ENGINE
# =====================================

st.divider()

st.subheader(
    "⚖️ Hotspot Comparison Engine"
)

compare_options = [
    j for j in df["Junction"]
    if j != selected["Junction"]
]

compare_hotspot = st.selectbox(
    "Compare With",
    compare_options,
    key="compare_hotspot"
)

compare_data = df[
    df["Junction"] == compare_hotspot
].iloc[0]

comparison_df = pd.DataFrame({
    "Metric": [
        "Violations",
        "Risk Score"
    ],
    selected["Junction"]: [
        selected["Violations"],
        round(selected["Risk Score"], 2)
    ],
    compare_hotspot: [
        compare_data["Violations"],
        round(compare_data["Risk Score"], 2)
    ]
})

st.dataframe(
    comparison_df,
    use_container_width=True
)

st.info(
    "📊 Compare hotspot performance and risk intensity."
)
# =====================================
# AI ROOT CAUSE ANALYSIS
# =====================================

st.divider()

st.subheader(
    "🧠 AI Root Cause Analysis"
)

root_causes = []

if selected["Risk Score"] >= 80:
    root_causes.append(
        "High historical violation concentration."
    )

if selected["Violations"] >= 10000:
    root_causes.append(
        "Persistent congestion pressure."
    )

if len(root_causes) == 0:
    root_causes.append(
        "No major risk drivers detected."
    )

for cause in root_causes:
    st.warning(cause)

st.info(
    "🤖 AI identified the most likely causes behind hotspot risk."
)
# =====================================
# AREA LEVEL INTELLIGENCE REPORT
# =====================================

st.divider()

st.subheader(
    "📄 Area-Level Intelligence Report"
)
if selected["Risk Score"] >= 80:

    assessment = (
        "Critical hotspot requiring immediate enforcement deployment and continuous monitoring."
    )

elif selected["Risk Score"] >= 60:

    assessment = (
        "High-risk area showing elevated congestion patterns. Additional patrols are recommended."
    )

elif selected["Risk Score"] >= 40:

    assessment = (
        "Moderate-risk location. Preventive monitoring should be maintained."
    )

else:

    assessment = (
        "Low-risk area currently operating within acceptable congestion levels."
    )
report = f"""
Area: {selected['Junction']}

Violations Recorded:
{selected['Violations']}

Risk Score:
{selected['Risk Score']:.2f}/100

Risk Level:
{selected['Risk Level']}

AI Assessment:
{assessment}
"""

st.info(report)
# =====================================
# CONGESTION SOURCE ANALYSIS
# =====================================

st.divider()

st.subheader(
    "🚗 Congestion Source Analysis"
)

source_df = pd.DataFrame({
    "Source": [
        "Illegal Parking",
        "Road Bottlenecks",
        "Traffic Density",
        "Violation Frequency"
    ],
    "Impact %": [
        40,
        25,
        20,
        15
    ]
})

st.dataframe(
    source_df,
    use_container_width=True
)

st.info(
    "🚦 Estimated congestion contribution factors."
)
# =====================================
# PRIORITY ENFORCEMENT RANKING
# =====================================

st.divider()

st.subheader(
    "🚓 Priority Enforcement Ranking"
)

priority_df = df.copy()

priority_df = priority_df.sort_values(
    by="Risk Score",
    ascending=False
)

priority_df["Priority Rank"] = range(
    1,
    len(priority_df) + 1
)

priority_df["Priority Score"] = (
    priority_df["Risk Score"]
    .round(2)
)

priority_df = priority_df[
    [
        "Priority Rank",
        "Junction",
        "Priority Score"
    ]
]

st.dataframe(
    priority_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "🚨 AI recommended enforcement deployment order."
)
