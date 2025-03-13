import streamlit as st
from PO.po_handler import POHandler

po_handler = POHandler()

def archived_po_tab():
    """Tab for viewing archived (completed & declined) purchase orders."""
    st.header("📦 Archived Purchase Orders")

    # ✅ Fetch archived purchase orders
    archived_orders = po_handler.get_archived_purchase_orders()

    if archived_orders.empty:
        st.info("ℹ️ No archived purchase orders found.")
        return

    # ✅ Group by POID to avoid redundancy
    archived_orders_grouped = archived_orders.groupby("poid")

    # ✅ Section for Completed POs
    st.subheader("✅ Completed Purchase Orders")
    for poid, group in archived_orders_grouped:
        order_info = group.iloc[0]  # ✅ Get first row for summary

        with st.expander(f"📦 PO #{poid} - {order_info['suppliername']} ({order_info['status']})"):
            st.write(f"**Order Date:** {order_info['orderdate']}")
            st.write(f"**Expected Delivery:** {order_info['expecteddelivery']}")
            
            # ✅ Handle missing ActualDelivery date
            actual_delivery = order_info.get("actualdelivery", "Not Available")
            st.write(f"**Delivered on:** {actual_delivery}")

            # ✅ List items inside this order
            for _, item in group.iterrows():
                cols = st.columns([1, 3, 2])

                if item["itempicture"]:
                    cols[0].image(item["itempicture"], width=60)
                else:
                    cols[0].write("No Image")

                cols[1].write(f"**{item['itemnameenglish']}**")
                cols[2].write(f"Ordered: {item['orderedquantity']}, Received: {item['receivedquantity']}")

    # ✅ Section for Declined POs
    st.subheader("❌ Declined Purchase Orders")
    declined_orders = archived_orders[archived_orders["status"] == "Declined"]
    
    if not declined_orders.empty:
        for poid, group in declined_orders.groupby("poid"):
            order_info = group.iloc[0]

            with st.expander(f"📦 PO #{poid} - {order_info['suppliername']} ({order_info['status']})"):
                st.write(f"**Order Date:** {order_info['orderdate']}")
                st.write(f"**Expected Delivery:** {order_info['expecteddelivery']}")
                st.write("**This order was declined by the supplier.**")

    st.success("✅ Archived purchase orders loaded successfully.")
