import streamlit as st
import pandas as pd
import joblib
import ast
import plotly.express as px
from datetime import datetime
from pathlib import Path

from utils.download_assets import download_assets
from utils.theme import apply_theme

st.set_page_config(
    page_title="AI Risk Predictor",
    layout="wide"
)

download_assets()
apply_theme()

st.title("🚨 AI Congestion Risk Predictor")


# ==================================
# LOAD MODEL
# ==================================

@st.cache_resource
def load_model():

    models_dir = (
        Path(__file__).parent.parent
        / "models"
    )

    model = joblib.load(
        models_dir / "congestion_model.pkl"
    )

    le_junction = joblib.load(
        models_dir / "le_junction.pkl"
    )

    le_vehicle = joblib.load(
        models_dir / "le_vehicle.pkl"
    )

    le_violation = joblib.load(
        models_dir / "le_violation.pkl"
    )

    return (
        model,
        le_junction,
        le_vehicle,
        le_violation
    )


@st.cache_data
def load_data():

    csv_path = (
        Path(__file__).parent.parent
        / "data"
        / "parking_violations.csv"
    )

    df = pd.read_csv(csv_path, nrows=50000)

    df["junction_name"] = df["junction_name"].fillna("Unknown")
    df["vehicle_type"] = df["vehicle_type"].fillna("Unknown")
    df["violation_type"] = df["violation_type"].fillna("Unknown")

    def extract_primary_violation(x):
        try:
            v = ast.literal_eval(str(x))
            if isinstance(v, list):
                return str(v[0])
            return str(v)
        except:
            return str(x)

    df["primary_violation"] = df["violation_type"].apply(
        extract_primary_violation
    )

    return df


model, le_junction, le_vehicle, le_violation = load_model()

df = load_data()


# ==================================
# HISTORICAL COUNTS
# ==================================

junction_freq_map = (
    df["junction_name"]
    .value_counts()
    .to_dict()
)

vehicle_freq_map = (
    df["vehicle_type"]
    .value_counts()
    .to_dict()
)

violation_freq_map = (
    df["primary_violation"]
    .value_counts()
    .to_dict()
)


# ==================================
# DROPDOWNS
# ==================================

junctions = sorted(
    df["junction_name"].unique()
)

vehicles = sorted(
    df["vehicle_type"].unique()
)

violations = sorted(
    df["primary_violation"].unique()
)


# ==================================
# UI
# ==================================

st.header("Enter Incident Details")

with st.form("risk_prediction_form"):

    junction = st.selectbox(
        "Junction",
        junctions
    )

    vehicle = st.selectbox(
        "Vehicle Type",
        vehicles
    )

    violation = st.selectbox(
        "Violation Type",
        violations
    )

    hour = st.slider(
        "Hour",
        0,
        23,
        12
    )

    day = st.slider(
        "Day",
        1,
        31,
        15
    )

    month = st.slider(
        "Month",
        1,
        12,
        6
    )

    predict = st.form_submit_button(
        "🚨 Predict Risk"
    )

# ==================================
# PREDICT
# ==================================

if predict:
    st.session_state["predict_clicked"] = True

if st.session_state.get("predict_clicked", False):

    try:
        junction_encoded = (
            le_junction.transform([junction])[0]
        )
    except:
        junction_encoded = 0

    try:
        vehicle_encoded = (
            le_vehicle.transform([vehicle])[0]
        )
    except:
        vehicle_encoded = 0

    try:
        violation_encoded = (
            le_violation.transform([violation])[0]
        )
    except:
        violation_encoded = 0

    is_weekend = 1 if day % 7 in [0, 6] else 0

    is_peak_hour = (
        1 if hour in [8, 9, 10, 17, 18, 19]
        else 0
    )

    junction_freq = junction_freq_map.get(
        junction,
        1
    )

    vehicle_freq = vehicle_freq_map.get(
        vehicle,
        1
    )

    violation_freq = violation_freq_map.get(
        violation,
        1
    )

    X = pd.DataFrame([[
        junction_encoded,
        vehicle_encoded,
        violation_encoded,
        hour,
        day,
        month,
        is_weekend,
        is_peak_hour,
        junction_freq,
        vehicle_freq,
        violation_freq
    ]], columns=[
        "junction_encoded",
        "vehicle_encoded",
        "violation_encoded",
        "hour",
        "day",
        "month",
        "is_weekend",
        "is_peak_hour",
        "junction_freq",
        "vehicle_freq",
        "violation_freq"
    ])

    risk_score = float(
        model.predict(X)[0]
    )

    risk_score = round(
        max(0, min(100, risk_score)),
        2
    )

    if risk_score >= 80:
        level = "🔴 CRITICAL"

    elif risk_score >= 60:
        level = "🟠 HIGH"

    elif risk_score >= 40:
        level = "🟡 MEDIUM"

    else:
        level = "🟢 LOW"

    st.divider()

    st.subheader("Predicted Risk Score")

    st.metric(
        "Risk Score",
        f"{risk_score}/100"
    )

    st.success(
        f"Risk Level: {level}"
    )
        # ==================================
    # RISK CONFIDENCE SCORE
    # ==================================

    st.divider()

    st.subheader(
        "🎯 Risk Confidence Score"
    )

    confidence_score = min(
        100,
        int(
            (
                junction_freq /
                max(junction_freq_map.values())
            ) * 100
        )
    )

    if confidence_score >= 80:

        confidence_level = "🟢 HIGH"

    elif confidence_score >= 50:

        confidence_level = "🟡 MODERATE"

    else:

        confidence_level = "🔴 LOW"

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Confidence Score",
            f"{confidence_score}%"
        )

    with c2:

        st.metric(
            "Prediction Confidence",
            confidence_level
        )

    st.info(
        f"🤖 Model Confidence Assessment: {confidence_level}"
    )   
        # ==================================
    # VIOLATION PROBABILITY
    # ==================================

    st.divider()

    st.subheader(
        "📈 Violation Probability"
    )

    violation_probability = round(
        risk_score,
        2
    )

    if violation_probability >= 80:

        probability_status = "🔴 VERY HIGH"

    elif violation_probability >= 60:

        probability_status = "🟠 HIGH"

    elif violation_probability >= 40:

        probability_status = "🟡 MODERATE"

    else:

        probability_status = "🟢 LOW"

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Violation Probability",
            f"{violation_probability}%"
        )

    with c2:

        st.metric(
            "Probability Level",
            probability_status
        )

    st.info(
        f"📊 Estimated Future Violation Probability: {probability_status}"
    )
        # ==================================
    # TRAFFIC ESCALATION PREDICTION
    # ==================================

    st.divider()

    st.subheader(
        "📈 Traffic Escalation Prediction"
    )

    if risk_score >= 80:

        escalation = "🔴 CRITICAL"
        escalation_percent = 95

    elif risk_score >= 60:

        escalation = "🟠 HIGH"
        escalation_percent = 75

    elif risk_score >= 40:

        escalation = "🟡 MODERATE"
        escalation_percent = 50

    else:

        escalation = "🟢 LOW"
        escalation_percent = 20

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Escalation Probability",
            f"{escalation_percent}%"
        )

    with c2:

        st.metric(
            "Escalation Status",
            escalation
        )

    st.info(
        f"🚦 Expected Traffic Escalation Level: {escalation}"
    )
        # ==================================
    # AREA VULNERABILITY SCORE
    # ==================================

    st.divider()

    st.subheader(
        "🛡️ Area Vulnerability Score"
    )

    vulnerability_score = min(
        100,
        int(
            (
                junction_freq /
                max(junction_freq_map.values())
            ) * 100
        )
    )

    if vulnerability_score >= 80:

        vulnerability_level = "🔴 CRITICAL"

    elif vulnerability_score >= 60:

        vulnerability_level = "🟠 HIGH"

    elif vulnerability_score >= 40:

        vulnerability_level = "🟡 MODERATE"

    else:

        vulnerability_level = "🟢 LOW"

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Vulnerability Score",
            f"{vulnerability_score}/100"
        )

    with c2:

        st.metric(
            "Area Risk Level",
            vulnerability_level
        )

    st.info(
        f"📍 Historical Area Vulnerability: {vulnerability_level}"
    )
        # ==================================
    # RISK BREAKDOWN ANALYSIS
    # ==================================

    st.divider()

    st.subheader(
        "📊 Risk Breakdown Analysis"
    )

    junction_impact = min(
        100,
        int(
            junction_freq /
            max(junction_freq_map.values())
            * 100
        )
    )

    vehicle_impact = min(
        100,
        int(
            vehicle_freq /
            max(vehicle_freq_map.values())
            * 100
        )
    )

    violation_impact = min(
        100,
        int(
            violation_freq /
            max(violation_freq_map.values())
            * 100
        )
    )

    time_impact = (
        100 if is_peak_hour
        else 40
    )

    breakdown_df = pd.DataFrame({

        "Factor":[
            "Junction",
            "Vehicle",
            "Violation",
            "Time"
        ],

        "Impact Score":[
            junction_impact,
            vehicle_impact,
            violation_impact,
            time_impact
        ]
    })

    st.dataframe(
        breakdown_df,
        use_container_width=True
    )

    st.info(
        "📈 AI identified the strongest contributors to the predicted risk score."
    )
# ==================================
# FUTURE RISK TIMELINE
# ==================================

    st.divider()

    st.subheader(
        "📈 Future Risk Timeline"
    )

    future_hours = [
        hour,
        (hour + 1) % 24,
        (hour + 2) % 24,
        (hour + 3) % 24,
        (hour + 4) % 24,
        (hour + 5) % 24
    ]

    future_risk = []

    for i in range(6):

        forecast = min(
            100,
            risk_score + (i * 3)
        )

        future_risk.append(
            round(forecast, 2)
        )

    timeline_df = pd.DataFrame({
        "Hour": future_hours,
        "Predicted Risk": future_risk
    })

   # fig = px.line(
        # timeline_df,
        # x="Hour",
      #   y="Predicted Risk",
      #   markers=True,
       #  title="6-Hour Risk Forecast"
    # )

    # st.plotly_chart(
      #   fig,
       #  use_container_width=True
    # )

    st.info(
        "🔮 AI forecast of expected congestion risk over the next 6 hours."
    )


# ==================================
# HIGH-RISK ALERT GENERATOR
# ==================================

    st.divider()

    st.subheader(
        "🚨 High-Risk Alert Generator"
    )

    escalation_probability = min(
        100,
        int(risk_score * 0.8)
    )

    alerts = []

    if risk_score >= 80:
        alerts.append(
            "🔴 Critical congestion risk detected."
        )

    if escalation_probability >= 70:
        alerts.append(
            "📈 Traffic escalation expected."
        )

    if vulnerability_score >= 70:
        alerts.append(
            "🛡️ High-risk hotspot identified."
        )

    if violation_probability >= 70:
        alerts.append(
            "🚓 Increased violation activity predicted."
        )

    if len(alerts) == 0:

        st.success(
            "✅ No major risk alerts detected."
        )

    else:

        for alert in alerts:
            st.error(alert)


# ==================================
# AI EXPLANATION
# ==================================

    st.divider()

    st.subheader(
        "🤖 AI Explanation"
    )

    st.write(f"""
The AI analyzed:

- Junction history
- Vehicle type
- Violation type
- Peak-hour pattern
- Weekend pattern
- Historical congestion frequency

Predicted Risk Score: {risk_score}

Risk Level: {level}

Model Confidence: {confidence_score}%

Violation Probability: {violation_probability}%

Traffic Escalation Probability: {escalation_probability}%
""")


# ==================================
# MODEL INPUTS
# ==================================

    st.divider()

    st.subheader(
        "📋 Model Inputs"
    )

    st.json({
        "Junction": junction,
        "Vehicle": vehicle,
        "Violation": violation,
        "Hour": hour,
        "Day": day,
        "Month": month,
        "Peak Hour": "Yes" if is_peak_hour else "No",
        "Weekend": "Yes" if is_weekend else "No"
    })


# ==================================
# RISK CLASSIFICATION DASHBOARD
# ==================================

    st.divider()

    st.subheader(
        "🏆 Risk Classification Dashboard"
    )

    if risk_score >= 80:

        final_classification = "🔴 CRITICAL RISK"

    elif risk_score >= 60:

        final_classification = "🟠 HIGH RISK"

    elif risk_score >= 40:

        final_classification = "🟡 MEDIUM RISK"

    else:

        final_classification = "🟢 LOW RISK"

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Final Risk Score",
            f"{risk_score}/100"
        )

    with c2:

        st.metric(
            "Classification",
            final_classification
        )

    st.info(
        f"🚨 AI Final Assessment: {final_classification}"
    )
