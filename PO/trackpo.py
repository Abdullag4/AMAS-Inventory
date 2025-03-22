import streamlit as st
from PO.po_handler import POHandler
from io import BytesIO
import pandas as pd

po_handler = POHandler()

def track_po_tab():
    """Tab for tracking purchase orders."""
    st.header("🚚 Track Purchase Orders")

    tabs = st.tabs(["📋 Active Orders", "📌 Proposed Adjustments"])
    
    # Active Orders Tab
    with tabs[0]:
        po_details = po_handler.get_all_purchase_orders()
        if po_details.empty:
            st.info("ℹ️ No purchase orders found.")
        else:
            display_order_details(po_details)

    # Proposed Adjustments Tab
    with tabs[1]:
        proposed_orders = po_handler.get_proposed_pos()
        if proposed_orders.empty:
            st.info("ℹ️ No proposed adjustments from suppliers.")
        else:
            handle_proposed_orders(proposed_orders)

def display_order_details(po_details):
    summary_df = po_details[["poid", "suppliername", "status", "expecteddelivery"]].drop_duplicates()
    summary_df.columns = ["PO ID", "Supplier", "Status", "Expected Delivery"]
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    selected_poid = st.selectbox(
        "🔽 Select a Purchase Order to view details",
        options=summary_df["PO ID"].tolist()
    )

    details = po_details[po_details["poid"] == selected_poid]
    order_info = details.iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("🗓️ Order Date", order_info['orderdate'].strftime("%Y-%m-%d"))
    col2.metric("📅 Expected Delivery", order_info['expecteddelivery'].strftime("%Y-%m-%d"))
    col3.metric("🚦 Status", order_info['status'])

    st.write("#### 📌 **Items:**")
    for idx, item in details.iterrows():
        cols = st.columns([1, 4, 2, 2, 2])
        if item['itempicture']:
            cols[0].image(BytesIO(item['itempicture']), width=60)
        cols[1].write(f"**{item['itemnameenglish']}**")
        cols[2].write(f"Ordered: {item['orderedquantity']}")
        cols[3].write(f"Received: {item['receivedquantity']}")
        cols[4].write(f"Price: ${item['estimatedprice']:.2f}" if item['estimatedprice'] else "Price: N/A")

    if order_info['status'] != 'Received':
        if st.button("📦 Mark as Delivered & Received"):
            po_handler.update_po_status_to_received(selected_poid)
            st.success(f"✅ Order #{selected_poid} marked as Delivered & Received.")
            st.rerun()
    else:
        st.success("✅ Order already received.")

def handle_proposed_orders(proposed_orders):
    for _, order in proposed_orders.iterrows():
        with st.expander(f"🔔 Proposed Adjustment – PO #{order['poid']} ({order['suppliername']})"):
            st.write(f"**Supplier Note:** {order['suppliernote']}")
            
            col1, col2 = st.columns(2)
            col1.metric("📅 Original Delivery", order['expecteddelivery'].strftime("%Y-%m-%d"))
            col2.metric("🆕 Proposed Delivery", order['supproposeddeliver'].strftime("%Y-%m-%d"))

            action_cols = st.columns(3)
            if action_cols[0].button(f"✅ Accept Proposal #{order['poid']}", key=f"accept_{order['poid']}"):
                po_handler.accept_proposed_po(order['poid'])
                st.success(f"✅ Proposal accepted and new PO created.")
                st.rerun()

            if action_cols[1].button(f"❌ Decline Proposal #{order['poid']}", key=f"decline_{order['poid']}"):
                po_handler.decline_proposed_po(order['poid'])
                st.warning("❌ Proposal declined.")
                st.rerun()

            action_cols[2].info("📝 To modify, edit manually as a new PO.")
