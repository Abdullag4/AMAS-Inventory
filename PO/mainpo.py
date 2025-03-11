import streamlit as st
from PO.manualpo import manual_po_tab
from PO.trackpo import track_po_tab
from PO.archivedpo import archived_po_tab  # ✅ Import new Archived PO tab

def po_page():
    st.title("🛒 Purchase Order Management")

    tabs = st.tabs(["Manual PO", "Track PO", "Archived PO"])  # ✅ Added Archived PO tab

    with tabs[0]:
        manual_po_tab()  # ✅ Handles Manual PO Creation

    with tabs[1]:
        track_po_tab()  # ✅ Handles Tracking of POs

    with tabs[2]:
        archived_po_tab()  # ✅ New Archived PO Tab
