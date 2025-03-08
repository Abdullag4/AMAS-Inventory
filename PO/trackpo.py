import streamlit as st
from PO.po_handler import POHandler

po_handler = POHandler()

def track_po_tab():
    st.header("🚚 Track Purchase Orders")
    po_details = po_handler.get_all_purchase_orders()

    if not po_details.empty:
        st.dataframe(po_details, use_container_width=True)
    else:
        st.info("No purchase orders to display.")
