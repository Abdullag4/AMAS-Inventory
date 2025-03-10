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

    # ✅ Convert item images for display
    if "itempicture" in po_details.columns:
        po_details["itempicture"] = po_details["itempicture"].apply(
            lambda img: f'<img src="data:image/png;base64,{img}" width="50">' if img else "No Image"
        )

    # ✅ Display purchase orders in a table
    st.write("📋 **Purchase Orders Overview**")
    st.dataframe(po_details.drop(columns=["itempicture"]), use_container_width=True)

    # ✅ Expandable section for order details
    for idx, row in po_details.iterrows():
        with st.expander(f"📦 Order {row['POID']} - {row['SupplierName']} ({row['Status']})"):
            st.write(f"**Order Date:** {row['OrderDate']}")
            st.write(f"**Expected Delivery:** {row['ExpectedDelivery']}")
            st.write(f"**Status:** {row['Status']}")
            st.write(f"**Item:** {row['ItemNameEnglish']} ({row['Quantity']} units)")
            if row["itempicture"]:
                st.image(row["itempicture"], width=100)
