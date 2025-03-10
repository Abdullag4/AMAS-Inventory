import streamlit as st
from PO.po_handler import POHandler
from io import BytesIO
import pandas as pd

po_handler = POHandler()

def track_po_tab():
    """Tab for tracking purchase orders."""
    st.header("🚚 Track Purchase Orders")

    # ✅ Fetch all purchase orders
    po_details = po_handler.get_all_purchase_orders()

    if po_details.empty:
        st.info("ℹ️ No purchase orders found.")
        return

    # ✅ Prepare summary table
    summary_cols = ["poid", "suppliername", "status", "expecteddelivery"]
    summary_df = po_details[summary_cols].drop_duplicates().reset_index(drop=True)
    summary_df.columns = ["PO ID", "Supplier", "Status", "Expected Delivery"]

    st.subheader("📋 **Purchase Orders Summary**")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # ✅ Expandable section for detailed view per order
    st.subheader("🔍 **Detailed Order Information**")

    # Create dropdown based on PO ID
    selected_poid = st.selectbox(
        "🔽 Select a Purchase Order to view details",
        options=summary_df["PO ID"].tolist()
    )

    # Filter details for selected PO
    selected_order_details = po_details[po_details["poid"] == selected_poid]

    if selected_order_details.empty:
        st.warning("⚠️ No details found for the selected order.")
        return

    order_info = selected_order_details.iloc[0]
    st.write(f"### 📦 Order #{order_info['poid']} – {order_info['suppliername']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("🗓️ Order Date", order_info['orderdate'].strftime("%Y-%m-%d"))
    col2.metric("📅 Expected Delivery", order_info['expecteddelivery'].strftime("%Y-%m-%d"))
    col3.metric("🚦 Status", order_info['status'])

    if pd.notnull(order_info['respondedat']):
        st.write(f"**Supplier Response Time:** {order_info['respondedat'].strftime('%Y-%m-%d %H:%M:%S')}")

    st.write("---")

    st.write("#### 📌 **Items in this Order:**")
    for idx, item in selected_order_details.iterrows():
        cols = st.columns([1, 4, 2, 2])

        if item['itempicture']:
            image_data = BytesIO(item['itempicture'])
            cols[0].image(image_data, width=60)
        else:
            cols[0].write("No Image")

        cols[1].write(f"**{item['itemnameenglish']}**")
        cols[2].write(f"Qty: {item['quantity']}")
        if pd.notnull(item['estimatedprice']):
            cols[3].write(f"Price: ${item['estimatedprice']:.2f}")
        else:
            cols[3].write("Price: N/A")

    st.success("✅ Purchase Order details loaded successfully!")
