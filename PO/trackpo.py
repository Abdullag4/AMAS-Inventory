import streamlit as st
import pandas as pd
from PO.po_handler import POHandler

po_handler = POHandler()

def track_po_tab():
    """Displays and tracks purchase orders with filtering and status updates."""
    st.header("🚚 Track Purchase Orders")

    # ✅ Fetch all purchase orders
    po_details = po_handler.get_all_purchase_orders()

    if po_details.empty:
        st.info("ℹ️ No purchase orders found.")
        return

    # ✅ Filter by status
    status_filter = st.selectbox("📌 Filter by Status", 
                                 ["All", "Pending", "Accepted", "Shipping", "Received", "Declined"])
    
    if status_filter != "All":
        po_details = po_details[po_details["status"] == status_filter]

    # ✅ Show purchase orders in a table
    st.write("📋 **Purchase Orders Overview**")
    st.dataframe(po_details[["poid", "suppliername", "orderdate", "expecteddelivery", "status"]],
                 use_container_width=True)

    # ✅ Select a specific PO to track
    selected_poid = st.selectbox("🔍 Select Purchase Order to Track", 
                                 po_details["poid"].tolist())

    if selected_poid:
        # ✅ Fetch details for the selected PO
        selected_po = po_details[po_details["poid"] == selected_poid].iloc[0]

        # ✅ Display PO details
        st.subheader(f"📦 Purchase Order #{selected_poid}")
        st.write(f"**Supplier:** {selected_po['suppliername']}")
        st.write(f"**Order Date:** {selected_po['orderdate']}")
        st.write(f"**Expected Delivery:** {selected_po['expecteddelivery']}")
        st.write(f"**Status:** `{selected_po['status']}`")

        # ✅ Fetch items related to the selected PO
        po_items = po_handler.get_po_items(selected_poid)

        if not po_items.empty:
            st.write("📦 **Ordered Items**")

            for _, row in po_items.iterrows():
                cols = st.columns([1, 3, 1, 2, 1])
                
                # ✅ Display item picture if available
                if row["itempicture"]:
                    cols[0].image(row["itempicture"], width=60)
                else:
                    cols[0].write("No Image")

                # ✅ Display item details
                cols[1].write(f"**{row['itemnameenglish']}**")
                cols[2].write(f"📦 Ordered: `{row['quantityordered']}`")
                cols[3].write(f"💰 Estimated Price: `{row['estimatedprice']}`")
                cols[4].write(f"🆔 Item ID: `{row['itemid']}`")

        else:
            st.warning("⚠️ No items found for this purchase order.")

        # ✅ Allow status updates
        new_status = st.selectbox("🔄 Update Purchase Order Status", 
                                  ["Pending", "Accepted", "Shipping", "Received", "Declined"], 
                                  index=["Pending", "Accepted", "Shipping", "Received", "Declined"].index(selected_po["status"]))

        if st.button("✅ Update Status"):
            po_handler.update_po_status(selected_poid, new_status)
            st.success(f"✅ Purchase Order #{selected_poid} updated to `{new_status}`.")
            st.experimental_rerun()
