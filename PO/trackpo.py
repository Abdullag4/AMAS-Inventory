import streamlit as st
import pandas as pd
from PO.po_handler import POHandler

po_handler = POHandler()

def track_po_tab():
    """Tab for tracking purchase orders."""
    st.header("📋 Purchase Order Tracking")

    # ✅ Fetch all purchase orders
    po_details = po_handler.get_all_purchase_orders()

    if po_details.empty:
        st.info("ℹ️ No purchase orders found.")
        return

    # ✅ Summary Table for Quick Overview
    st.subheader("📊 Summary of Purchase Orders")
    summary_df = po_details[["poid", "suppliername", "status", "expecteddelivery"]].drop_duplicates()
    summary_df.columns = ["Order Number", "Supplier", "Status", "Expected Delivery"]

    # ✅ Display Summary Table
    st.dataframe(summary_df, use_container_width=True)

    # ✅ Expandable Section for Full Order Details
    st.subheader("🚚 Track Purchase Orders")
    
    for po_id in summary_df["Order Number"]:
        order_details = po_details[po_details["poid"] == po_id]
        supplier_name = order_details["suppliername"].iloc[0]
        status = order_details["status"].iloc[0]
        expected_delivery = order_details["expecteddelivery"].iloc[0]

        with st.expander(f"📦 Order {po_id} - {supplier_name} ({status})"):
            st.write(f"**Order Date:** {order_details['orderdate'].iloc[0]}")
            st.write(f"**Expected Delivery:** {expected_delivery}")
            st.write(f"**Status:** {status}")
            st.write(f"**Supplier Response Time:** {order_details['respondedat'].iloc[0] if pd.notna(order_details['respondedat'].iloc[0]) else 'Not Responded'}")

            # ✅ Display all items in this PO
            st.write("### 📦 Ordered Items")
            order_items = order_details[["itemnameenglish", "quantity", "estimatedprice", "itempicture"]]

            for idx, row in order_items.iterrows():
                cols = st.columns([1, 2, 2, 2])
                if row["itempicture"]:
                    cols[0].image(row["itempicture"], width=50)
                else:
                    cols[0].write("No Image")
                cols[1].write(f"**{row['itemnameenglish']}**")
                cols[2].write(f"📦 Quantity: {row['quantity']}")
                cols[3].write(f"💰 Estimated Price: {row['estimatedprice'] if row['estimatedprice'] else 'Not Provided'}")

    st.success("✅ Purchase Order Tracking Loaded Successfully!")
