import streamlit as st
from PO.po_handler import POHandler
import base64
from io import BytesIO

po_handler = POHandler()

def track_po_tab():
    """Tab for tracking purchase orders."""
    st.header("🚚 Track Purchase Orders")

    # ✅ Fetch all purchase orders
    po_details = po_handler.get_all_purchase_orders()

    if po_details.empty:
        st.info("ℹ️ No purchase orders found.")
        return

    # ✅ Convert images to displayable format
    def image_to_display(img_data):
        if img_data and isinstance(img_data, (bytes, memoryview)):  # ✅ Check if valid binary data
            img_bytes = BytesIO(img_data).getvalue()  # ✅ Convert to bytes
            encoded = base64.b64encode(img_bytes).decode()  # ✅ Encode as Base64
            return f'<img src="data:image/png;base64,{encoded}" width="60">'
        return "No Image"

    # ✅ Apply image processing for display
    if "itempicture" in po_details.columns:
        po_details["itempicture"] = po_details["itempicture"].apply(image_to_display)

    # ✅ Display purchase orders in a table
    st.write("📋 **Purchase Orders Overview**")
    st.dataframe(po_details.drop(columns=["itempicture"]), use_container_width=True)

    # ✅ Expandable section for order details
    for idx, row in po_details.iterrows():
        with st.expander(f"📦 Order {row['poid']} - {row['suppliername']} ({row['status']})"):
            st.write(f"**Order Date:** {row['orderdate']}")
            st.write(f"**Expected Delivery:** {row['expecteddelivery']}")
            st.write(f"**Supplier Response Time:** {row['respondedat'] or 'Pending'}")
            st.write(f"**Status:** {row['status']}")
            st.write(f"**Item:** {row['itemnameenglish']} ({row['quantity']} units)")

            # ✅ Display item image if available
            if row["itempicture"] != "No Image":
                st.markdown(row["itempicture"], unsafe_allow_html=True)
