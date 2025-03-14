import streamlit as st
from reports.sup_performance import sup_performance_tab

def main_reports():
    """Main Reports Page."""
    st.title("📊 Reports Dashboard")

    tabs = st.tabs(["Supplier Performance"])  # ✅ Future tabs can be added later

    with tabs[0]:
        sup_performance_tab()
