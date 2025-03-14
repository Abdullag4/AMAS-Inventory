import streamlit as st
from receive_items.receive_items import receive_items
from receive_items.received_po import received_po_tab

def main_receive_page():
    st.title("📦 Receive Items Management")

    tabs = st.tabs(["Manual Receive", "Received PO"])

    with tabs[0]:
        receive_items()

    with tabs[1]:
        received_po_tab()
