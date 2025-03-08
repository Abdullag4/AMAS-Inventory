import streamlit as st
from PO.autopo import auto_po_tab
from PO.trackpo import track_po_tab
from PO.manualpo import manual_po_tab

def po_page():
    st.title("🛒 Purchase Order Management")

    tabs = st.tabs(["Auto PO", "Track PO", "Manual PO"])

    with tabs[0]:
        auto_po_tab()
    with tabs[1]:
        track_po_tab()
    with tabs[2]:
        manual_po_tab()
