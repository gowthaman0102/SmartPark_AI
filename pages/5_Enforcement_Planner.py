import streamlit as st
import pandas as pd
import plotly.express as px

from utils.download_assets import download_assets
from utils.theme import apply_theme

st.set_page_config(
    page_title="Enforcement Planner",
    layout="wide"
)

download_assets()
apply_theme()

st.title("🚔 AI Enforcement Planner")

junctions = {
    "Safina Plaza Junction":15449,
    "KR Market Junction":11538,
    "Elite Junction":10718,
    "Sagar Theatre Junction":10549,
    "Central Street Junction":5388
}

junction = st.selectbox(
    "Select Junction",
    list(junctions.keys())
)

violations = junctions[junction]

risk_score = round(
    (violations / max(junctions.values())) * 100
)

st.metric(
    "Risk Score",
    f"{risk_score}/100"
)

# Resource allocation

if risk_score >= 80:

    officers = 5
    tow_trucks = 3

    priority = "CRITICAL"

elif risk_score >= 60:

    officers = 3
    tow_trucks = 2
    priority = "HIGH"

else:

    officers = 1
    tow_trucks = 1
    priority = "LOW"

st.subheader("Recommended Deployment")

col1,col2,col3 = st.columns(3)

col1.metric(
    "Traffic Officers",
    officers
)

col2.metric(
    "Tow Trucks",
    tow_trucks
)

col3.metric(
    "Priority",
    priority
)

st.subheader("Expected Impact")

reduction = round(risk_score * 0.35)

st.success(
    f"Estimated Congestion Reduction: {reduction}%"
)

st.info(f"""
Recommended Actions

• Deploy {officers} traffic officers

• Deploy {tow_trucks} towing vehicles

• Increase enforcement patrols

• Issue parking violation alerts

• Monitor hotspot continuously
""")
# =====================================
# OFFICER DEPLOYMENT OPTIMIZER
# =====================================

st.divider()

st.subheader(
    "👮 Officer Deployment Optimizer"
)

required_officers = max(
    1,
    int(violations / 3000)
)

deployment_status = (
    "🔴 CRITICAL"
    if required_officers >= 5
    else "🟠 HIGH"
    if required_officers >= 3
    else "🟢 NORMAL"
)

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Required Officers",
        required_officers
    )

with c2:

    st.metric(
        "Deployment Status",
        deployment_status
    )

st.info(
    f"🚔 AI recommends deploying {required_officers} officers to maintain enforcement coverage."
)
# =====================================
# TOW TRUCK ALLOCATION ENGINE
# =====================================

st.divider()

st.subheader(
    "🚚 Tow Truck Allocation Engine"
)

required_tow_trucks = max(
    1,
    int(violations / 5000)
)

tow_status = (
    "🔴 HIGH DEMAND"
    if required_tow_trucks >= 3
    else "🟠 MODERATE"
    if required_tow_trucks >= 2
    else "🟢 LOW"
)

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Required Tow Trucks",
        required_tow_trucks
    )

with c2:

    st.metric(
        "Towing Demand",
        tow_status
    )

st.info(
    f"🚛 Recommended towing fleet allocation: {required_tow_trucks}"
)
# =====================================
# RESOURCE ALLOCATION VISUALIZATION
# =====================================

allocation_df = pd.DataFrame({
    "Resource": [
        "Officers",
        "Tow Trucks"
    ],
    "Count": [
        officers,
        tow_trucks
    ]
})

fig = px.bar(
    allocation_df,
    x="Resource",
    y="Count",
    title="Resource Allocation"
)

fig.update_layout(
    autosize=True,
    height=450,
    margin=dict(
        l=20,
        r=20,
        t=60,
        b=20
    )
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="resource_allocation_chart"
)

st.info(
    "📊 Visual comparison of enforcement resources allocated by AI."
)
# =====================================
# PATROL ROUTE OPTIMIZER
# =====================================

st.divider()

st.subheader(
    "🛣️ Patrol Route Optimizer"
)

route_length = round(
    (risk_score / 100) * 15,
    1
)

route_status = (
    "🔴 Intensive Patrol"
    if risk_score >= 80
    else "🟠 Standard Patrol"
    if risk_score >= 60
    else "🟢 Light Patrol"
)

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Route Length",
        f"{route_length} km"
    )

with c2:

    st.metric(
        "Patrol Mode",
        route_status
    )

st.info(
    f"🚓 Suggested patrol coverage radius: {route_length} km"
)

# =====================================
# RESOURCE REQUIREMENT ESTIMATOR
# =====================================

st.divider()

st.subheader(
    "📦 Resource Requirement Estimator"
)

cones = officers * 10
barricades = officers * 2

resource_df = pd.DataFrame({
    "Resource":[
        "Traffic Cones",
        "Barricades",
        "Officers",
        "Tow Trucks"
    ],
    "Required":[
        cones,
        barricades,
        officers,
        tow_trucks
    ]
})

st.dataframe(
    resource_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "📋 Estimated field resources required."
)

# =====================================
# SHIFT PLANNING ASSISTANT
# =====================================

st.divider()

st.subheader(
    "🕒 Shift Planning Assistant"
)

if risk_score >= 80:

    shift = "24/7 Coverage"

elif risk_score >= 60:

    shift = "Peak-Hour Coverage"

else:

    shift = "Regular Coverage"

st.success(
    f"Recommended Shift Strategy: {shift}"
)

# =====================================
# ZONE BASED DEPLOYMENT PLAN
# =====================================

st.divider()

st.subheader(
    "🗺️ Zone-Based Deployment Plan"
)

zone_df = pd.DataFrame({
    "Zone":[
        "North",
        "South",
        "East",
        "West"
    ],
    "Deployment":[
        officers,
        max(1, officers-1),
        officers,
        max(1, officers-2)
    ]
})

st.dataframe(
    zone_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "📍 Officer allocation across operational zones."
)

# =====================================
# ENFORCEMENT COST ESTIMATION
# =====================================

st.divider()

st.subheader(
    "💰 Enforcement Cost Estimation"
)

estimated_cost = (
    officers * 5000 +
    tow_trucks * 7000
)

st.metric(
    "Estimated Cost",
    f"₹{estimated_cost:,}"
)

st.info(
    "💵 Estimated daily enforcement expenditure."
)

# =====================================
# DAILY ACTION PLAN
# =====================================

st.divider()

st.subheader(
    "📅 Daily Action Plan"
)

st.info(f"""
1. Deploy {officers} officers

2. Deploy {tow_trucks} tow trucks

3. Monitor hotspot continuously

4. Enforce illegal parking rules

5. Generate end-of-day report
""")

# =====================================
# RESOURCE EFFICIENCY SCORE
# =====================================

st.divider()

st.subheader(
    "⚡ Resource Efficiency Score"
)

efficiency_score = round(
    reduction /
    officers,
    2
)

efficiency_score = max(
    efficiency_score,
    50
)

st.metric(
    "Efficiency Score",
    f"{efficiency_score}/100"
)

st.info(
    "📈 AI calculated expected deployment efficiency."
)

# =====================================
# AI ENFORCEMENT RECOMMENDATIONS
# =====================================

st.divider()

st.subheader(
    "🤖 AI Enforcement Recommendations"
)

recommendations = []

if risk_score >= 80:

    recommendations.append(
        "Deploy maximum enforcement resources."
    )

    recommendations.append(
        "Increase towing frequency."
    )

elif risk_score >= 60:

    recommendations.append(
        "Increase patrol visibility."
    )

    recommendations.append(
        "Monitor congestion growth."
    )

else:

    recommendations.append(
        "Maintain normal monitoring."
    )

for rec in recommendations:

    st.success(rec)

st.info(
    "🧠 AI-generated enforcement strategy recommendations."
)
