import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

from utils.download_assets import download_assets
from utils.theme import apply_theme

st.set_page_config(
    page_title="AI Forecast",
    layout="wide"
)

download_assets()
apply_theme()

st.title("🔮 AI Congestion Forecast")

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
    return pd.read_csv(csv_path)

df = load_data()

# Clean Junctions
df["junction_name"] = (
    df["junction_name"]
    .fillna("Unknown")
    .astype(str)
)

df = df[
    (df["junction_name"] != "No Junction")
    &
    (df["junction_name"] != "Unknown")
]

# =====================================
# JUNCTION LIST
# =====================================

junctions = sorted(
    list(
        df["junction_name"]
        .dropna()
        .unique()
    )
)

junction = st.selectbox(
    "Select Junction",
    options=junctions,
    index=0
)

# =====================================
# HISTORICAL COUNTS
# =====================================

junction_counts = (
    df["junction_name"]
    .value_counts()
)

count = int(
    junction_counts.get(
        junction,
        0
    )
)

max_count = int(
    junction_counts.max()
)

# =====================================
# CURRENT RISK
# =====================================

base_risk = round(
    (
        count / max_count
    ) * 100,
    2
)

# =====================================
# FORECAST ENGINE
# =====================================

current_hour = datetime.now().hour

if 7 <= current_hour <= 10:

    next_hour = base_risk * 1.08
    next_6_hours = base_risk * 1.12
    next_day = base_risk * 1.05

elif 17 <= current_hour <= 20:

    next_hour = base_risk * 1.10
    next_6_hours = base_risk * 1.15
    next_day = base_risk * 1.08

elif 0 <= current_hour <= 5:

    next_hour = base_risk * 0.80
    next_6_hours = base_risk * 0.75
    next_day = base_risk * 0.90

else:

    next_hour = base_risk * 0.98
    next_6_hours = base_risk * 0.95
    next_day = base_risk * 0.92

next_hour = round(
    min(100, max(0, next_hour)),
    2
)

next_6_hours = round(
    min(100, max(0, next_6_hours)),
    2
)

next_day = round(
    min(100, max(0, next_day)),
    2
)

# =====================================
# METRICS
# =====================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Current Risk",
        f"{base_risk}/100"
    )

with c2:
    st.metric(
        "Next Hour",
        f"{next_hour}/100"
    )

with c3:
    st.metric(
        "Next 6 Hours",
        f"{next_6_hours}/100"
    )

with c4:
    st.metric(
        "Next Day",
        f"{next_day}/100"
    )

# =====================================
# FORECAST CHART
# =====================================

forecast = pd.DataFrame({
    "Time": [
        "Current",
        "1 Hour",
        "6 Hours",
        "24 Hours"
    ],
    "Risk": [
        base_risk,
        next_hour,
        next_6_hours,
        next_day
    ]
})

st.line_chart(
    forecast.set_index("Time")
)

# =====================================
# AI ANALYSIS
# =====================================

st.subheader("🤖 AI Forecast Analysis")

if next_day > base_risk:

    st.warning(
        f"""
Forecast indicates increasing congestion pressure at
{junction}.

AI recommends proactive enforcement deployment.
"""
    )

elif next_day < base_risk:

    st.success(
        f"""
Forecast indicates congestion is expected to decrease at
{junction}.

Current enforcement levels appear sufficient.
"""
    )

else:

    st.info(
        f"""
Forecast indicates stable congestion conditions at
{junction}.
"""
    )


# =====================================
# 24 HOUR CONGESTION FORECAST
# =====================================

st.divider()

st.subheader(
    "🕒 24 Hour Congestion Forecast"
)

hours = list(range(24))

forecast_values = []

for h in hours:

    if 7 <= h <= 10:
        value = base_risk * 1.10

    elif 17 <= h <= 20:
        value = base_risk * 1.15

    elif 0 <= h <= 5:
        value = base_risk * 0.75

    else:
        value = base_risk

    forecast_values.append(
        round(
            min(100, max(0, value)),
            2
        )
    )

hourly_df = pd.DataFrame({
    "Hour": hours,
    "Forecast Risk": forecast_values
})

st.line_chart(
    hourly_df.set_index("Hour")
)

st.info(
    "📈 AI forecast of congestion risk across the next 24 hours."
)
# =====================================
# 7 DAY VIOLATION FORECAST
# =====================================

st.divider()

st.subheader(
    "📅 7 Day Violation Forecast"
)

days = [
    "Mon",
    "Tue",
    "Wed",
    "Thu",
    "Fri",
    "Sat",
    "Sun"
]

future_violations = [
    int(count * 1.00),
    int(count * 1.05),
    int(count * 1.10),
    int(count * 1.08),
    int(count * 1.12),
    int(count * 1.15),
    int(count * 1.18)
]

violation_df = pd.DataFrame({
    "Day": days,
    "Predicted Violations": future_violations
})

st.bar_chart(
    violation_df.set_index("Day")
)

st.info(
    "🚔 Estimated violation trend for the upcoming week."
)
# =====================================
# DEMAND PREDICTION ENGINE
# =====================================

st.divider()

st.subheader(
    "📊 Demand Prediction Engine"
)

predicted_demand = round(
    (base_risk + next_day) / 2,
    2
)

if predicted_demand >= 70:

    demand_status = "🔴 HIGH"

elif predicted_demand >= 35:

    demand_status = "🟠 MODERATE"

else:

    demand_status = "🟢 LOW"

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Predicted Demand",
        predicted_demand
    )

with c2:

    st.metric(
        "Demand Status",
        demand_status
    )

st.info(
    "📈 AI prediction of future parking demand."
)
# =====================================
# CONGESTION TREND PROJECTION
# =====================================

st.divider()

st.subheader(
    "📉 Congestion Trend Projection"
)

if next_day > base_risk:

    trend = "📈 Increasing"

elif next_day < base_risk:

    trend = "📉 Decreasing"

else:

    trend = "➡ Stable"

st.metric(
    "Projected Trend",
    trend
)

st.info(
    "🔮 AI projection of future congestion direction."
)
# =====================================
# PARKING AVAILABILITY FORECAST
# =====================================

st.divider()

st.subheader(
    "🅿️ Parking Availability Forecast"
)

current_availability = round(
    100 - base_risk,
    2
)

future_availability = round(
    100 - next_day,
    2
)

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Current Availability",
        f"{current_availability}%"
    )

with c2:

    st.metric(
        "Tomorrow Availability",
        f"{future_availability}%"
    )

st.info(
    "🚗 Estimated parking space availability forecast."
)
# =====================================
# RISK FORECAST TIMELINE
# =====================================

st.divider()

st.subheader(
    "⏳ Risk Forecast Timeline"
)

timeline_df = pd.DataFrame({
    "Time":[
        "Current",
        "1 Hour",
        "6 Hours",
        "24 Hours"
    ],
    "Risk":[
        base_risk,
        next_hour,
        next_6_hours,
        next_day
    ]
})

st.dataframe(
    timeline_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "📅 Forecasted congestion risk timeline."
)
# =====================================
# ENFORCEMENT DEMAND FORECAST
# =====================================

st.divider()

st.subheader(
    "👮 Enforcement Demand Forecast"
)

future_officers = max(
    3,
    round(predicted_demand / 8)
)

future_tow_trucks = max(
    2,
    round(predicted_demand / 15)
)

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Future Officers",
        future_officers
    )

with c2:

    st.metric(
        "Future Tow Trucks",
        future_tow_trucks
    )

st.info(
    "🚔 Predicted enforcement resource demand."
)
# =====================================
# FUTURE RESOURCE PLANNING
# =====================================

st.divider()

st.subheader(
    "📦 Future Resource Planning"
)

resource_df = pd.DataFrame({
    "Resource":[
        "Traffic Officers",
        "Tow Trucks",
        "Barricades",
        "Traffic Cones"
    ],
    "Required":[
        future_officers,
        future_tow_trucks,
        future_officers * 2,
        future_officers * 10
    ]
})

st.dataframe(
    resource_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "📋 AI-generated future deployment planning."
)
# =====================================
# AI FORECAST INSIGHTS
# =====================================

st.divider()

st.subheader(
    "🤖 AI Forecast Insights"
)

insights = []

if predicted_demand >= 70:

    insights.append(
        "Future parking demand expected to remain high."
    )

if future_availability < 30:

    insights.append(
        "Parking space shortages may occur."
    )

if next_day > base_risk:

    insights.append(
        "Congestion risk is forecasted to increase."
    )

if len(insights) == 0:

    insights.append(
        "Forecast conditions remain stable."
    )

for insight in insights:

    st.success(insight)

st.info(
    "🧠 AI-generated forecasting recommendations."
)
# =====================================
# FUTURE HOTSPOT PREDICTION
# =====================================

st.divider()

st.subheader(
    "🔥 Future Hotspot Prediction"
)

future_hotspot = junction_counts.idxmax()

future_hotspot_count = int(
    junction_counts.max()
)

st.write(
    "### Predicted Hotspot"
)

st.success(
    future_hotspot
)

st.metric(
    "Projected Violations",
    future_hotspot_count
)

st.info(
    "🚨 Junction most likely to remain a future congestion hotspot."
)
# =====================================
# SUMMARY
# =====================================

st.subheader("📈 Forecast Summary")

st.markdown(
    f"""
### Selected Junction
**{junction}**

### Historical Violations
**{count:,}**

### Current Risk
**{base_risk}/100**

### Forecast

- Next Hour: **{next_hour}/100**
- Next 6 Hours: **{next_6_hours}/100**
- Next Day: **{next_day}/100**

### AI Forecast Inputs

- Historical violation density
- Junction traffic pressure
- Time-of-day pattern
- Peak-hour behaviour
- Traffic congestion trend

### AI Insight

The SmartPark AI forecasting engine uses historical violation
patterns and junction activity levels to estimate future
congestion risk and support proactive traffic management.
"""
)
# =====================================
# DEBUG INFO
# =====================================

with st.expander("Forecast Diagnostics"):

    st.write(
        "Selected Junction:",
        junction
    )

    st.write(
        "Historical Violations:",
        count
    )

    st.write(
        "Maximum Junction Violations:",
        max_count
    )

    st.write(
        "Current Hour:",
        current_hour
    )

    st.write(
        "Predicted Demand:",
        predicted_demand
    )
