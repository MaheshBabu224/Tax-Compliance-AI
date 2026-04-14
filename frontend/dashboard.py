"""
Tax Compliance AI Dashboard - Streamlit Frontend
"""
import sys
import os
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import logging

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/dashboard.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import configuration
from config import DATA_CONFIG, CITY_COORDINATES, DEFAULT_COORDINATES

logger.info("Dashboard application started")

# ===== PAGE CONFIG =====
st.set_page_config(page_title="SatyaTax", layout="wide")

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    """Load tax profiles data"""
    try:
        df = pd.read_csv(DATA_CONFIG["output_file"])
        logger.info(f"Loaded {len(df)} tax profiles")
        return df
    except FileNotFoundError:
        logger.error(f"Data file not found: {DATA_CONFIG['output_file']}")
        return None

df = load_data()

if df is None or df.empty:
    st.error("❌ Dataset not loaded properly. Please run: python generate_dataset.py")
    st.stop()

logger.info(f"Dashboard loaded with {len(df)} records")

# ===== CSS STYLING ================
st.markdown(
    """
<style>
/* FORCE STREAMLIT ROOT DARK */
[data-testid="stAppViewContainer"] {
    background: #0a001a !important;
}

/* FIX HEADER AREA */
header {
    background: transparent !important;
}

/* REMOVE WHITE FROM TABS */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
}

.stTabs [data-baseweb="tab"] {
    color: white !important;
}

/* FIX SELECTBOX / INPUTS */
div[data-baseweb="select"] > div {
    background-color: #1a002f !important;
    color: white !important;
}

/* FIX TABLES */
[data-testid="stDataFrame"] {
    background-color: transparent !important;
}

/* FIX EXPANDER */
.streamlit-expanderHeader {
    background-color: #1a002f !important;
    color: white !important;
}

/* FIX PLOTLY FULL DARK */
.js-plotly-plot .plotly, 
.js-plotly-plot .plot-container,
.js-plotly-plot svg {
    background-color: transparent !important;
}

/* MAIN APP BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #2d0b4e, #0a001a) !important;
    color: white;
}

/* REMOVE WHITE CONTAINERS */
section.main > div {
    background-color: transparent !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #1a002f !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* FIX PLOTS */
.js-plotly-plot, .plot-container {
    background-color: transparent !important;
}

/* FIX BLOCKS */
.block-container {
    background-color: transparent !important;
}

/* CARDS */
.card {
    padding:20px;
    border-radius:12px;
    text-align:center;
    color:white;
    font-weight: bold;
}

/* COLORS */
.low { background:#22c55e; }
.medium { background:#f59e0b; }
.high { background:#f97316; }
.critical { background:#ef4444; }

/* INFO BOX */
.info-box {
    padding: 15px;
    border-radius: 8px;
    background: rgba(255,255,255,0.08);
    border-left: 4px solid #22c55e;
}

</style>
""",
    unsafe_allow_html=True,
)

# ===== SIDEBAR =====
st.sidebar.title("🏛️ SatyaTax")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Search", "Map", "Analytics", "About"],
)

with st.sidebar.expander("ℹ️ About Dataset"):
    st.write(f"""
    - **Total Records:** {len(df):,}
    - **Risk Levels:** {df['RiskLevel'].nunique()}
    - **Cities:** {df['City'].nunique()}
    - **Anomalies:** {len(df[df['Anomaly'] == 'Anomaly']):,}
    """)

# ===== DASHBOARD PAGE =====
if menu == "Dashboard":
    st.title("📊 SatyaTax Dashboard")
    logger.info("Dashboard page accessed")

    col1, col2, col3, col4 = st.columns(4)

    low = len(df[df["RiskLevel"] == "Low"])
    med = len(df[df["RiskLevel"] == "Medium"])
    high = len(df[df["RiskLevel"] == "High"])
    crit = len(df[df["RiskLevel"] == "Critical"])

    col1.markdown(
        f"<div class='card low'><h3>Low</h3><h1>{low}</h1></div>",
        unsafe_allow_html=True,
    )
    col2.markdown(
        f"<div class='card medium'><h3>Medium</h3><h1>{med}</h1></div>",
        unsafe_allow_html=True,
    )
    col3.markdown(
        f"<div class='card high'><h3>High</h3><h1>{high}</h1></div>",
        unsafe_allow_html=True,
    )
    col4.markdown(
        f"<div class='card critical'><h3>Critical</h3><h1>{crit}</h1></div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    risk_counts = df["RiskLevel"].value_counts().reset_index()
    risk_counts.columns = ["RiskLevel", "Count"]

    fig1 = px.pie(
        risk_counts,
        names="RiskLevel",
        values="Count",
        color="RiskLevel",
        color_discrete_map={
            "Low": "green",
            "Medium": "orange",
            "High": "darkorange",
            "Critical": "red",
        },
    )
    fig1.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    sample = df.sample(min(50, len(df)))

    fig3 = px.histogram(
        df,
        x="RiskScore",
        nbins=30,
        color_discrete_sequence=["red"],
    )
    fig3.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    city_data = df.groupby("City")["RiskScore"].mean().reset_index()
    fig4 = px.bar(
        city_data,
        x="City",
        y="RiskScore",
        color="RiskScore",
        color_continuous_scale="Reds",
    )
    fig4.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Risk Distribution")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Risk Score Distribution")
        st.plotly_chart(fig3, use_container_width=True)

    with right_col:
        st.subheader("Average Risk by City")
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Insights")

    highest_city = city_data.sort_values(by="RiskScore", ascending=False).iloc[0]["City"]

    st.info(
        f"""
    - {crit} taxpayers are in **Critical Risk**
    - {high} taxpayers are in **High Risk**
    - Highest risk city: **{highest_city}**
    """
    )

# ===== SEARCH PAGE =====
elif menu == "Search":
    st.title("🔍 Search Taxpayer")
    logger.info("Search page accessed")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        name = st.selectbox("Select Taxpayer", [""] + sorted(df["Name"].unique()))
    
    with col2:
        city_filter = st.selectbox("Filter by City", ["All"] + sorted(df["City"].unique()))
    
    if name:
        p = df[df["Name"] == name].iloc[0]
        logger.info(f"Taxpayer searched: {name}")

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Location", p["City"])
        with col2:
            st.metric("Risk Score", p["RiskScore"])
        with col3:
            st.metric("Status", p["RiskLevel"])

        st.progress(p["RiskScore"] / 100)
        
        st.markdown("### Anomaly Detection")
        anomaly_status = "🚨 Detected" if p["Anomaly"] == "Anomaly" else "✅ Normal"
        st.write(f"**Anomaly Status:** {anomaly_status}")

        st.markdown("### AI Analysis")
        st.info(p["AI_Reason"])
        
        st.markdown("### Income Details")
        income_col1, income_col2, income_col3 = st.columns(3)
        income_col1.metric("Tax Evaded", f"₹{p['TaxEvaded']:,}")
        income_col2.metric("Person ID", p["PersonID"])
        income_col3.metric("Status", "Under Review" if p["RiskLevel"] in ["High", "Critical"] else "Low Risk")


# ===== MAP PAGE =====
elif menu == "Map":
    st.title("🗺️ Live Geographic Map")
    logger.info("Map page accessed")

    coords = CITY_COORDINATES

    df["lat"] = df["City"].map(lambda x: coords.get(x, DEFAULT_COORDINATES)[0])
    df["lon"] = df["City"].map(lambda x: coords.get(x, DEFAULT_COORDINATES)[1])

    st.map(df[["lat", "lon"]], zoom=4)


# ===== ANALYTICS PAGE =====
elif menu == "Analytics":
    st.title("📈 Advanced Analytics")
    logger.info("Analytics page accessed")
    
    tab1, tab2, tab3 = st.tabs(["Risk by City", "Top Risky", "Income Analysis"])
    
    with tab1:
        st.subheader("Average Risk Score by City")
        city_risk = df.groupby("City")["RiskScore"].mean().sort_values(ascending=False)
        fig = px.bar(
            x=city_risk.index,
            y=city_risk.values,
            color=city_risk.values,
            color_continuous_scale="Reds",
            labels={"x": "City", "y": "Average Risk Score"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Top 15 Risky Individuals")
        top_risky = df.nlargest(15, "RiskScore")[
            ["Name", "City", "RiskScore", "RiskLevel", "TaxEvaded", "Anomaly"]
        ]
        st.dataframe(top_risky, use_container_width=True)
    
    with tab3:
        st.subheader("Risk Level Distribution")
        risk_counts = df["RiskLevel"].value_counts().reset_index()
        risk_counts.columns = ["RiskLevel", "Count"]
        fig = px.pie(
            risk_counts,
            names="RiskLevel",
            values="Count",
            color="RiskLevel",
            color_discrete_map={
                "Low": "green",
                "Medium": "orange",
                "High": "darkorange",
                "Critical": "red",
            },
        )
        st.plotly_chart(fig, use_container_width=True)


# ===== ABOUT PAGE =====
elif menu == "About":
    st.title("ℹ️ About SatyaTax")
    logger.info("About page accessed")

    st.markdown("""
    ## SatyaTax: AI-Based Tax Compliance System
    
    An intelligent system designed to detect and monitor tax compliance anomalies using advanced machine learning algorithms.
    
    ### Features
    - 🤖 **ML Anomaly Detection** - Isolation Forest algorithm for detecting suspicious patterns
    - 📊 **Risk Scoring** - Calculated based on income discrepancies
    - 🗺️ **Geographic Analysis** - City-level risk assessment
    - 🔍 **Individual Search** - Detailed taxpayer profiles
    - 📈 **Advanced Analytics** - Comprehensive data insights
    
    ### How It Works
    1. **Data Collection** - Synthetic tax compliance data generation
    2. **ML Analysis** - Anomaly detection using Isolation Forest
    3. **Risk Calculation** - Scoring based on declared vs estimated income
    4. **Visualization** - Interactive dashboards and reports
    
    ### Architecture
    - **Frontend** - Streamlit web application
    - **Backend** - Flask REST API
    - **ML Model** - Scikit-learn Isolation Forest
    - **Data** - CSV-based storage (SQLite for production)
    
    ### Version
    **SatyaTax v1.0.0**
    
    ### Support
    For issues or questions, please check the README.md file.
    """)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>© 2024 Tax Compliance AI System | All Rights Reserved</small>
    </div>
    """, unsafe_allow_html=True)
    st.write("AI-powered tax compliance system with analytics and visualization.")
