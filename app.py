import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize Application Page Configuration Configuration
st.set_page_config(
    page_title="NSE Market Intelligence Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.database import DatabaseManager
from src.scraper import NSEScraper
from src.analytics import AnalyticsEngine
from src.styles import apply_terminal_theme

# Apply CSS Override Injectors
apply_terminal_theme()

# Wire Up Singletons into Streamlit State Engines
if "db" not in st.session_state:
    st.session_state.db = DatabaseManager()
if "scraper" not in st.session_state:
    st.session_state.scraper = NSEScraper()
if "engine" not in st.session_state:
    st.session_state.engine = AnalyticsEngine(st.session_state.db)

db = st.session_state.db
scraper = st.session_state.scraper
engine = st.session_state.engine

# ==================== SIDEBAR CONTROLS & MANUAL TRIGGER INGESTORS ====================
st.sidebar.image("https://img.icons8.com/nolan/64/bullish.png", width=50)
st.sidebar.title("NSE Terminal Engine")
st.sidebar.markdown("---")

st.sidebar.subheader("Data Synchronization")
if st.sidebar.button("⚡ Run Daily Live Scraping Ingestion", use_container_width=True):
    with st.spinner("Executing secure handshake with NSE India..."):
        df_52w = scraper.fetch_52w_highs()
        df_active = scraper.fetch_most_active()
        
        if not df_52w.empty:
            db.save_52w_highs(df_52w)
        if not df_active.empty:
            db.save_most_active(df_active)
            
        st.sidebar.success(f"Ingested {len(df_52w)} breakout targets and {len(df_active)} volume leaders!")
        st.rerun()

# Date Selection Routing Matrix
with db.engine.connect() as _conn:
    available_dates_df = pd.read_sql("SELECT DISTINCT snapshot_date FROM daily_52week_high ORDER BY snapshot_date DESC;", _conn)

available_dates = available_dates_df["snapshot_date"].astype(str).tolist() if not available_dates_df.empty else [datetime.today().strftime('%Y-%m-%d')]
selected_date = st.sidebar.selectbox("🎯 Target Analytical Frame", options=available_dates, index=0)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Terminal Tip:** Click on any cell count or status frame value to pull historical sub-logs instantly inside structural overlay panes.")

# Header Matrix Banner
st.title("⚡ NSE India Market Intelligence Terminal")
st.caption(f"Continuous Analytics Framework Running | Quant Matrix Status: Active | Selected Trading Session: **{selected_date}**")

# ==================== MODAL DIALOG COMPONENT FOR POPUPS ====================
@st.dialog("📋 Structural Asset Historical Logs")
def show_symbol_modal(symbol):
    st.write(f"### Historical Breakout Run: **{symbol}**")
    st.markdown(f"[📊 Open Direct Interactive Chart on TradingView](https://www.tradingview.com/chart/?symbol=NSE:{symbol})")
    
    history_df = engine.get_symbol_occurrence_history(symbol)
    if not history_df.empty:
        st.metric("Total Historic Technical Breakout Days", len(history_df))
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No secondary instances documented inside the active analytics window matrix.")

# ==================== STREAMLIT MULTI-TAB VIEW LAYER ROUTING ====================
tab1, tab2, tab3 = st.tabs([
    "📈 NSE 52-Week High Breakouts", 
    "🗃️ Historical Engine Analytics", 
    "🔥 Volume Velocity & Overlaps"
])

# -------------------- TAB 1: 52-WEEK HIGH SCANNER --------------------
with tab1:
    st.subheader("Daily 52-Week High Breakout Registry")
    df_tab1 = engine.get_tab1_dataset(selected_date)
    
    if df_tab1.empty:
        st.warning("No data ingested for this date segment. Fire the scraper engine on the left sidebar.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Technical Breakouts", len(df_tab1))
        col2.metric("New Structural Entrants", len(df_tab1[df_tab1["Status"] == "NEW"]))
        col3.metric("Systemic Recurring Assets", len(df_tab1[df_tab1["Status"] == "RETURNING"]))
        
        # Inlining UI controls inside Interactive Data Editor Structure
        df_tab1["TradingView URL"] = df_tab1["Symbol"].apply(lambda x: f"https://www.tradingview.com/chart/?symbol=NSE:{x}")
        
        search_term = st.text_input("🔍 Filter Asset Registry Matrix", placeholder="Type Symbol or Company Name...")
        if search_term:
            df_tab1 = df_tab1[df_tab1["Symbol"].str.contains(search_term, case=False) | df_tab1["Company Name"].str.contains(search_term, case=False)]

        edited_df = st.data_editor(
            df_tab1,
            column_config={
                "TradingView URL": st.column_config.LinkColumn("Chart Link", display_text="Open Chart ↗"),
                "Historical Appearances": st.column_config.NumberColumn("Total Documented Days (Click to Inspect)", help="Click to examine instances"),
            },
            hide_index=True,
            use_container_width=True,
            disabled=True
        )
        
        # Capturing Row/Cell Selection interactions dynamically to spawn Dialog Modal overlay
        selected_symbol = st.selectbox("🎯 Drill down specific asset history from list above:", [""] + df_tab1["Symbol"].tolist())
        if selected_symbol:
            show_symbol_modal(selected_symbol)

# -------------------- TAB 2: HISTORICAL SYMBOL ANALYTICS --------------------
with tab2:
    st.subheader("Aggregated Market Capture Profiles")
    df_tab2 = engine.get_tab2_dataset()
    
    if df_tab2.empty:
        st.info("Historical matrices will build dynamically as additional day profiles parse into memory.")
    else:
        st.markdown("This window runs continuous structural analytical calculations across all dates present in the master repository.")
        
        search_tab2 = st.text_input("🔍 Search Aggregated Index", placeholder="Filter by asset ticket...")
        if search_tab2:
            df_tab2 = df_tab2[df_tab2["Symbol"].str.contains(search_tab2, case=False)]
            
        st.dataframe(df_tab2, use_container_width=True, hide_index=True)

# -------------------- TAB 3: MOST ACTIVE EQUITIES + OVERLAPS --------------------
with tab3:
    st.subheader("Liquidity Concentration Matrix & Technical Confluences")
    df_tab3 = engine.get_tab3_dataset(selected_date)
    
    if df_tab3.empty:
        st.warning("Data empty. Populate systems via synchronization sequence.")
    else:
        overlap_count = len(df_tab3[df_tab3["52W High Match"] == "OVERLAP MATCH"])
        
        m1, m2 = st.columns(2)
        m1.metric("Volume Leaders Traced", len(df_tab3))
        m2.metric("Critical Breakout Confluences Found (Overlap Status)", overlap_count, delta_color="inverse")
        
        filter_overlap = st.checkbox("⚠️ Hide Isolated Flow Assets (Show Overlaps Only)")
        if filter_overlap:
            df_tab3 = df_tab3[df_tab3["52W High Match"] == "OVERLAP MATCH"]
            
        df_tab3["TradingView Chart"] = df_tab3["Symbol"].apply(lambda x: f"https://www.tradingview.com/chart/?symbol=NSE:{x}")
        
        st.data_editor(
            df_tab3,
            column_config={
                "TradingView Chart": st.column_config.LinkColumn("Quick Chart", display_text="View ↗"),
                "Volume (Shares)": st.column_config.NumberColumn(format="%d"),
                "Turnover (Cr)": st.column_config.NumberColumn(format="₹ %.2f"),
            },
            hide_index=True,
            use_container_width=True,
            disabled=True
        )