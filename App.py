import streamlit as st
from utils.download_assets import download_assets

download_assets()
from utils.theme import apply_theme

st.set_page_config(
    page_title="SmartPark AI",
    page_icon="🚦",
    layout="wide"
)

apply_theme()

# =====================================
# SIDEBAR BRANDING
# =====================================

with st.sidebar:

    st.markdown("""
    # 🚦 SmartPark AI
    """)

    st.caption(
        "Urban Traffic Intelligence Platform"
    )

    st.success(
        "🟢 System Status: Active"
    )

    st.metric(
    "System Health",
    "100%",
    "Operational"
)

    st.info(
        "🤖 AI monitoring city-wide traffic and parking operations"
    )

    st.divider()

   

# =====================================
# HOME PAGE
# =====================================

st.markdown("""
# 🚦 SmartPark AI

### Intelligent Traffic Monitoring & Enforcement Platform

Transforming traffic violations into actionable intelligence using AI-powered analytics, forecasting, enforcement planning, and command center operations.
""")



st.success(
    "Powered by Bengaluru Police Parking Violation Dataset"
)
st.info(
    """
    🚀 SmartPark AI combines congestion prediction,
    hotspot intelligence, enforcement planning,
    AI forecasting and live traffic analytics
    into a unified traffic intelligence platform.
    """
)

st.markdown("---")

st.write(
    """
    SmartPark AI is an AI-powered urban traffic intelligence platform
    that identifies congestion hotspots, predicts future traffic risks,
    optimizes enforcement deployment, analyzes live traffic conditions,
    and supports city-wide traffic management decisions through
    advanced analytics and forecasting.
    """
)

c1, c2, c3, c4 = st.columns(4)


with c1:
    st.metric(
        "Modules",
        "8"
    )

with c2:
    st.metric(
        "Analytics Features",
        "75+"
    )

with c3:
    st.metric(
        "Predictions",
        "Real-Time"
    )

with c4:
    st.metric(
        "Coverage",
        "Bengaluru"
    )
    

st.subheader(
    "🚀 Platform Modules"
)
st.markdown("---")

c1, c2 = st.columns(2)

with c1:

    st.info("""
    🎯 Predict traffic congestion before it occurs.
    """)

with c2:

    st.success("""
    🚔 Optimize enforcement deployment using AI.
    """)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.success(
        "🔥 Hotspot Intelligence"
    )

with c2:
    st.warning(
        "⚠ Risk Predictor"
    )

with c3:
    st.info(
        "🎯 Command Center"
    )

with c4:
    st.error(
        "🎥 Video Analytics"
    )
   
st.markdown("---")

st.caption(
    "SmartPark AI • Bengaluru Traffic Intelligence Platform • Version 1.0"
)