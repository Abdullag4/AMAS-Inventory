# trackpo.py
import streamlit as st
from PO.po_handler import POHandler
from io import BytesIO
import pandas as pd

# Import the new Proposed PO logic
from PO.proposedpo import proposed_po_tab

po_handler = POHandler()

def track_po_tab():
    """Tab for tracking purchase orders."""
    st.header("🚚 Track Purchase Orders")

    tabs = st.tabs(["📋 Active Orders", "📌 Proposed Adjustments"])

    with tabs[0]:
        # 1) Show active orders (i.e., everything NOT 'Proposed')
        po_details = po_handler.get_all_purchase_orders()
        active_po_df = po_details[po_details["proposedstatus"] != "Proposed"]

        if active_po_df.empty:
            st.info("ℹ️ No active purchase orders found.")
            return

        summary_df = active_po_df[["poid", "suppliername", "status", "expecteddelivery"]].drop_duplicates()
        summary_df.columns = ["PO ID", "Supplier", "Status", "Expected Delivery"]
        st.subheader("📋 **Active Purchase Orders Summary**")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.subheader("🔍 **Detailed Order Information**")
        selected_poid = st.selectbox(
            "🔽 Select a Purchase Order to view details",
            options=summary_df["PO ID"].tolist()
        )

        selected_order_details = active_po_df[active_po_df["poid"] == selected_poid]
        if selected_order_details.empty:
            st.warning("⚠️ No details found for the selected order.")
            return

        order_info = selected_order_details.iloc[0]
        st.write(f"### 📦 Order #{order_info['poid']} – {order_info['suppliername']}")

        col1, col2, col3 = st.columns(3)
        if pd.notnull(order_info['orderdate']):
            col1.metric("🗓️ Order Date", order_info['orderdate'].strftime("%Y-%m-%d"))
        else:
            col1.metric("🗓️ Order Date", "N/A")

        if pd.notnull(order_info['expecteddelivery']):
            col2.metric("📅 Expected Delivery", order_info['expecteddelivery'].strftime("%Y-%m-%d"))
        else:
            col2.metric("📅 Expected Delivery", "N/A")

        col3.metric("🚦 Status", order_info['status'])

        if pd.notnull(order_info['respondedat']):
            st.write(f"**Supplier Response Time:** {order_info['respondedat'].strftime('%Y-%m-%d %H:%M:%S')}")

        st.write("---")
        st.write("#### 📌 **Items in this Order:**")

        for idx, item in selected_order_details.iterrows():
            row_cols = st.columns([1, 4, 2, 2, 2])

            if item['itempicture']:
                image_data = BytesIO(item['itempicture'])
                row_cols[0].image(image_data, width=60)
            else:
                row_cols[0].write("No Image")

            row_cols[1].write(f"**{item['itemnameenglish']}**")
            row_cols[2].write(f"Ordered: {item['orderedquantity']}")
            row_cols[3].write(f"Received: {item['receivedquantity']}")

            if pd.notnull(item['estimatedprice']):
                row_cols[4].write(f"Price: ${item['estimatedprice']:.2f}")
            else:
                row_cols[4].write("Price: N/A")

        if order_info['status'] != 'Received':
            st.write("---")
            if st.button("📦 Mark as Delivered & Received"):
                po_handler.update_po_status_to_received(selected_poid)
                st.success(f"✅ Order #{selected_poid} marked as Delivered & Received.")
                st.rerun()
        else:
            st.success("✅ This order has already been marked as Received.")

    with tabs[1]:
        # 2) Proposed Adjustments Tab
        proposed_po_tab(po_handler)
