import streamlit as st
from po.autopo import auto_po_tab
from po.trackpo import track_po_tab
from po.manualpo import manual_po_tab

def po_main_page():
    st.title("📦 Purchase Order Management")

    tab1, tab2, tab3 = st.tabs(["Auto PO", "Tracking PO", "Manual PO"])

    with tab1:
        auto_po_tab()
    with tab2:
        track_po_tab()
    with tab3:
        manual_po_tab()
