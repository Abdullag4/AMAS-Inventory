import streamlit as st
from PO.po_handler import POHandler

po_handler = POHandler()

def archived_po_tab():
    """Tab for viewing archived (completed & rejected) purchase orders."""
    st.header("📁 Archived Purchase Orders")

    # ✅ Fetch Completed & Rejected Purchase Orders
    completed_orders, rejected_orders = po_handler.get_archived_purchase_orders()

    # ✅ Completed Orders Section
    st.subheader("✅ Completed Purchase Orders")
    if completed_orders.empty:
        st.info("ℹ️ No completed orders yet.")
    else:
        st.dataframe(completed_orders, use_container_width=True)

    # ✅ Rejected Orders Section
    st.subheader("❌ Rejected Purchase Orders")
    if rejected_orders.empty:
        st.info("ℹ️ No rejected orders yet.")
    else:
        st.dataframe(rejected_orders, use_container_width=True)
