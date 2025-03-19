import streamlit as st
from PO.po_handler import POHandler
from io import BytesIO
import pandas as pd

po_handler = POHandler()

def track_po_tab():
    st.header("🚚 Track Purchase Orders")

    po_details = po_handler.get_all_purchase_orders()

    if po_details.empty:
        st.info("ℹ️ No purchase orders found.")
        return

    summary_df = po_details[["poid", "suppliername", "status", "expecteddelivery"]].drop_duplicates().reset_index(drop=True)
    summary_df.columns = ["PO ID", "Supplier", "Status", "Expected Delivery"]

    st.subheader("📋 **Purchase Orders Summary**")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("🔍 **Detailed Order Information**")
    selected_poid = st.selectbox("🔽 Select a Purchase Order", options=summary_df["PO ID"].tolist())

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

    if order_info['status'] == 'Declined' and pd.notnull(order_info['suppliernote']):
        st.error(f"Supplier Decline Reason: {order_info['suppliernote']}")

    st.write("---")

    st.write("#### 📌 **Items in this Order:**")
    for idx, item in selected_order_details.iterrows():
        cols = st.columns([1, 3, 2, 2, 2, 3])

        if item['itempicture']:
            image_data = BytesIO(item['itempicture'])
            cols[0].image(image_data, width=60)
        else:
            cols[0].write("No Image")

        cols[1].write(f"**{item['itemnameenglish']}**")
        cols[2].write(f"Ordered: {item['orderedquantity']}")

        if item['proposalstatus'] != 'Pending':
            cols[3].write(f"Supplier Proposed: {item['supproposedquantity']} units at ${item['supproposedprice']}")
            cols[4].write(f"New Delivery: {item['supproposeddelivery'].strftime('%Y-%m-%d')}")
            cols[5].write(f"Supplier Note: {item['supitemnote']}")

            decision = cols[5].selectbox(
                "Decision", ["Pending", "Accepted", "Partially Accepted", "Declined"],
                key=f"{item['itemid']}_decision"
            )

            if cols[5].button("Update Decision", key=f"{item['itemid']}_btn"):
                po_handler.update_proposal_status(selected_poid, item['itemid'], decision)
                st.success(f"✅ Proposal for '{item['itemnameenglish']}' updated to '{decision}'.")
                st.rerun()

        else:
            cols[3].write("No proposal from supplier yet.")
            cols[4].write("-")
            cols[5].write("-")

    if order_info['status'] != 'Received':
        st.write("---")
        if st.button("📦 Mark as Delivered & Received"):
            po_handler.update_po_status_to_received(selected_poid)
            st.success(f"✅ Order #{selected_poid} marked as Delivered & Received.")
            st.rerun()
    else:
        st.success("✅ Order already marked as Received.")
