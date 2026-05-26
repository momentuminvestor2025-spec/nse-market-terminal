import streamlit as st

def apply_terminal_theme():
    """Injects high-contrast dark CSS styled for structural market terminals."""
    st.markdown("""
        <style>
            /* Base Container Cleanups */
            .block-container { padding-top: 2rem; padding-bottom: 2rem; }
            
            /* Metric Card Enhancements */
            div[data-testid="stMetricValue"] {
                font-family: 'Courier New', Courier, monospace;
                font-weight: 700;
                color: #00FF66 !important;
            }
            
            /* Custom Status Badge Implementations */
            .badge-new {
                background-color: #00FF66; color: #000000;
                padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;
            }
            .badge-returning {
                background-color: #1E293B; color: #94A3B8;
                padding: 3px 8px; border-radius: 4px; font-weight: 500; font-size: 11px;
            }
            .badge-overlap {
                background-color: #EF4444; color: #FFFFFF;
                padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;
                animation: pulse 2s infinite;
            }
            
            /* Custom Hyperlinks */
            .tv-link {
                color: #38BDF8 !important; text-decoration: none; font-weight: 600;
            }
            .tv-link:hover { text-decoration: underline; }
        </style>
    """, unsafe_allow_html=True)