import streamlit as st


def apply_theme():
    """
    Inject CSS to ensure:
    - Main area: light theme, but with darker/more vibrant green and blue colors.
    - Sidebar: solid black background with bright white text on everything.
    """
    st.markdown(
        """
        <style>

        /* ═══════════════════════════════════════════
           SIDEBAR — full black background
        ═══════════════════════════════════════════ */
        section[data-testid="stSidebar"] {
            background-color: #000000 !important;
        }

        /* All sidebar text → white */
        section[data-testid="stSidebar"] *,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div,
        section[data-testid="stSidebar"] small {
            color: #ffffff !important;
        }

        /* Navigation page links in sidebar */
        [data-testid="stSidebarNavItems"] a,
        [data-testid="stSidebarNavItems"] span,
        [data-testid="stSidebarNavItems"] li,
        [data-testid="stSidebarNavItems"] *,
        nav[data-testid="stSidebarNav"] a,
        nav[data-testid="stSidebarNav"] span,
        nav[data-testid="stSidebarNav"] * {
            color: #ffffff !important;
        }

        /* Active nav item highlight */
        [data-testid="stSidebarNavItems"] a[aria-current="page"],
        nav[data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #1a1a1a !important;
            border-radius: 6px !important;
            color: #90caf9 !important;
        }

        /* Sidebar links hover */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebarNavItems"] a:hover {
            color: #90caf9 !important;
            background-color: #1a1a1a !important;
            border-radius: 6px !important;
        }

        /* Sidebar metric values */
        section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stMetricDelta"] {
            color: #4caf50 !important; /* Brighter green for positive delta */
        }
        section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
            color: #cccccc !important;
        }

        /* Sidebar caption */
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] caption {
            color: #aaaaaa !important;
        }

        /* Sidebar divider */
        section[data-testid="stSidebar"] hr {
            border-color: #333333 !important;
        }

        /* Sidebar selectbox */
        section[data-testid="stSidebar"] .stSelectbox label {
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] .stSelectbox > div > div {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 1px solid #555555 !important;
        }
        /* ====================================
   MAIN PAGE SELECTBOX (LIGHT THEME)
==================================== */

/* Closed selectbox */
.stSelectbox > div > div {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #cccccc !important;
}

/* Dropdown popup container */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* Dropdown list */
div[role="listbox"] {
    background-color: #ffffff !important;
    border: 1px solid #cccccc !important;
}

/* Dropdown options */
div[role="option"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* Hover option */
div[role="option"]:hover {
    background-color: #e8f0fe !important;
    color: #000000 !important;
}

/* Selected option */
div[aria-selected="true"] {
    background-color: #dbeafe !important;
    color: #000000 !important;
}

        /* Sidebar success / info / warning / error notification text */
        section[data-testid="stSidebar"] [data-testid="stNotification"] p {
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] [data-testid="stNotification"] {
            background-color: #222222 !important;
            border: 1px solid #444444 !important;
        }


        /* ═══════════════════════════════════════════
           MAIN AREA — Solid Darker Colors (Not Faded)
        ═══════════════════════════════════════════ */
        /* Main page background */
.main .block-container {
    background-color: #ffffff !important;
}
/* Input widgets */
input,
textarea,
select {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* All normal text */
p, span, div, label {
    color: #0d1b2a;
}

        /* Success boxes → Solid Dark Green */
        [data-testid="stNotification"][kind="success"],
        div.stSuccess,
        .element-container div[data-testid="stNotification"].st-success {
            background-color: #1b5e20 !important; /* Dark Green */
            border-left: 5px solid #003300 !important;
        }
        [data-testid="stNotification"][kind="success"] p,
        div.stSuccess p,
        [data-testid="stNotification"][kind="success"] span,
        [data-testid="stNotification"][kind="success"] div {
            color: #ffffff !important;
            font-weight: 500 !important;
        }

        /* Info boxes → Solid Dark Blue */
        [data-testid="stNotification"][kind="info"],
        div.stInfo {
            background-color: #0d47a1 !important; /* Dark Blue */
            border-left: 5px solid #002171 !important;
        }
        [data-testid="stNotification"][kind="info"] p,
        div.stInfo p,
        [data-testid="stNotification"][kind="info"] span,
        [data-testid="stNotification"][kind="info"] div {
            color: #ffffff !important;
            font-weight: 500 !important;
        }

        /* Warning boxes → Solid Dark Orange/Amber */
        [data-testid="stNotification"][kind="warning"],
        div.stWarning {
            background-color: #e65100 !important; /* Dark Orange */
            border-left: 5px solid #ac1900 !important;
        }
        [data-testid="stNotification"][kind="warning"] p,
        div.stWarning p,
        [data-testid="stNotification"][kind="warning"] span,
        [data-testid="stNotification"][kind="warning"] div {
            color: #ffffff !important;
            font-weight: 500 !important;
        }

        /* Error boxes → Solid Dark Red */
        [data-testid="stNotification"][kind="error"],
        div.stError {
            background-color: #b71c1c !important; /* Dark Red */
            border-left: 5px solid #7f0000 !important;
        }
        [data-testid="stNotification"][kind="error"] p,
        div.stError p,
        [data-testid="stNotification"][kind="error"] span,
        [data-testid="stNotification"][kind="error"] div {
            color: #ffffff !important;
            font-weight: 500 !important;
        }

        /* Metric value — darker, bolder */
        [data-testid="stMetricValue"] {
            color: #0d1b2a !important;
            font-weight: 800 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #2c3e50 !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricDelta"] {
            font-weight: 700 !important;
        }

        /* Page titles and headers — deep navy */
        h1, h2, h3 {
            color: #0d1b2a !important;
        }

        /* Divider line — visible but subtle */
        hr {
            border-color: #bbbbbb !important;
        }

        /* Dataframe header — darker */
        thead tr th {
            background-color: #d0dbe8 !important;
            color: #0d1b2a !important;
            font-weight: 700 !important;
        }

        /* Force main content area to light theme */
.stApp,
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewBlockContainer"],
section.main {
    background-color: #ffffff !important;
    color: #0d1b2a !important;
    opacity: 1 !important;
    filter: none !important;
    transition: none !important;
}
        
        /* Hide the "Running..." overlay in the top right */
        div[data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
