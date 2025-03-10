import streamlit as st
from PO.po_handler import POHandler
import base64
from io import BytesIO

po_handler = POHandler()

def track_po_tab():
    """Tab for tracking purchase orders with dropdown selection."""
    st.header("🚚 Track Purchase Orders")

    # ✅ Fetch all purchase orders
    po_details = po_handler.get_all_purchase_orders()

    if po_details.empty:
        st.info("ℹ️ No purchase orders found.")
        return

    # ✅ Create a dropdown for PO selection
    po_options = {f"PO-{row['poid']} - {row['suppliername']} ({row['status']})": row['poid'] for _, row in po_details.iterrows()}
    selected_po = st.selectbox("📜 Select a Purchase Order", list(po_options.keys()))

    # ✅ Get the selected PO details
    selected_po_id = po_options[selected_po]
    selected_po_details = po_details[po_details["poid"] == selected_po_id]

    # ✅ Function to convert images for display
    def image_to_display(img_data):
        if img_data and isinstance(img_data, (bytes, memoryview)):  # ✅ Ensure valid binary data
            img_bytes = BytesIO(img_data).getvalue()  # ✅ Convert to bytes
            encoded = base64.b64encode(img_bytes).decode()  # ✅ Encode as Base64
            return f'<img src="data:image/png;base64,{encoded}" width="60">'
        return "No Image"

    # ✅ Apply image processing for display
    if "itempicture" in selected_po_details.columns:
        selected_po_details["itempicture"] = selected_po_details["itempicture"].apply(image_to_display)

    # ✅ Display selected PO details
    with st.expander(f"📦 Order {selected_po_details.iloc[0]['poid']} - {selected_po_details.iloc[0]['suppliername']} ({selected_po_details.iloc[0]['status']})"):
        st.write(f"**Order Date:** {selected_po_details.iloc[0]['orderdate']}")
        st.write(f"**Expected Delivery:** {selected_po_details.iloc[0]['expecteddelivery']}")
        st.write(f"**Supplier Response Time:** {selected_po_details.iloc[0]['respondedat'] or 'Pending'}")
        st.write(f"**Status:** {selected_po_details.iloc[0]['status']}")

        # ✅ Display ordered items
        st.write("### 📦 Ordered Items:")
        for idx, row in selected_po_details.iterrows():
            cols = st.columns([1, 3, 1, 1])
            cols[0].markdown(row["itempicture"], unsafe_allow_html=True) if row["itempicture"] != "No Image" else cols[0].write("No Image")
            cols[1].write(f"**{row['itemnameenglish']}**")
            cols[2].write(f"Qty: {row['quantity']}")
            cols[3].write(f"Est. Price: {row['estimatedprice'] if row['estimatedprice'] else 'N/A'}")

    st.success("✅ Purchase Order Tracking Loaded Successfully!")
