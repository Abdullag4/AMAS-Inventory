import streamlit as st
from PO.manualpo import manual_po_tab
from PO.trackpo import track_po_tab  # ✅ Import PO Tracking tab

def po_page():
    """Main page for Purchase Order management with multiple tabs."""
    st.title("🛒 Purchase Order Management")

    # ✅ Enable both Manual PO and Tracking PO tabs
    tabs = st.tabs(["Manual PO", "Track PO"])

    with tabs[0]:  
        manual_po_tab()  # ✅ Handles Manual PO Creation

    with tabs[1]:  
        track_po_tab()  # ✅ Handles Tracking of POs
