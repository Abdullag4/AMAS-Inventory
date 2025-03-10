import streamlit as st
from PO.manualpo import manual_po_tab
from PO.trackpo import track_po_tab

def po_page():
    st.title("🛒 Purchase Order Management")

    tabs = st.tabs(["Manual PO", "Tracking PO"])  # ✅ Only Manual PO active now for clarity

    with tabs[0]:
        manual_po_tab()
