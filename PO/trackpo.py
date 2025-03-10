import streamlit as st
from PO.po_handler import POHandler

po_handler = POHandler()

def track_po_tab():
    """Tab for tracking purchase orders."""
    st.header("🚚 Track Purchase Orders")

    # ✅ Fetch all purchase orders
    po_details = po_handler.get_all_purchase_orders()

    if po_details.empty:
        st.info("ℹ️ No purchase orders found.")
        return

    # ✅ Convert column names to lowercase (fixes KeyError)
    po_details.columns = po_details.columns.str.lower()

    # ✅ Convert item images for display
    if "itempicture" in po_details.columns:
        po_details["itempicture"] = po_details["itempicture"].apply(
            lambda img: st.image(img, width=50) if img else "No Image"
        )

    # ✅ Display purchase orders in a table
    st.write("📋 **Purchase Orders Overview**")
    st.dataframe(po_details.drop(columns=["itempicture"]), use_container_width=True)

    # ✅ Expandable section for order details
    for idx, row in po_details.iterrows():
        with st.expander(f"📦 Order {row['poid']} - {row['suppliername']} ({row['status']})"):
            st.write(f"**Order Date:** {row['orderdate']}")
            st.write(f"**Expected Delivery:** {row['expecteddelivery']}")
            st.write(f"**Supplier Response Time:** {row['respondedat']}")
            st.write(f"**Status:** {row['status']}")
            st.write(f"**Item:** {row['itemnameenglish']} ({row['quantity']} units)")
            if row["itempicture"]:
                st.image(row["itempicture"], width=100)

    st.success("✅ Purchase Order Tracking Loaded Successfully!")
