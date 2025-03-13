import streamlit as st
from PO.po_handler import POHandler
from io import BytesIO

po_handler = POHandler()

def archived_po_tab():
    """Tab displaying archived (completed and rejected) purchase orders."""
    st.header("📦 Archived Purchase Orders")

    # Fetch all archived purchase orders
    archived_orders = po_handler.get_archived_purchase_orders()

    if archived_orders.empty:
        st.info("ℹ️ No archived purchase orders found.")
        return

    completed_orders = archived_orders[archived_orders["status"] == "Completed"]
    rejected_orders = archived_orders[archived_orders["status"] == "Rejected"]

    st.subheader("✅ Completed Orders")
    if not completed_orders.empty:
        for poid, group in completed_orders.groupby("poid"):
            order_info = group.iloc[0]
            with st.expander(f"📦 PO #{poid} - {order_info['suppliername']}"):
                st.write(f"**Order Date:** {order_info['orderdate']}")

                # ✅ Fix: Check if `ActualDelivery` exists before displaying
                actual_delivery = order_info.get("actualdelivery", None)
                if actual_delivery and pd.notna(actual_delivery):
                    st.write(f"**Delivered on:** {actual_delivery}")
                else:
                    st.write("**Delivered on:** Not Recorded")

                for idx, item in group.iterrows():
                    cols = st.columns([1, 3, 2])
                    if item['itempicture']:
                        cols[0].image(BytesIO(item['itempicture']), width=50)
                    else:
                        cols[0].write("No Image")
                    cols[1].write(f"{item['itemnameenglish']}")
                    cols[2].write(f"Received: {item['receivedquantity']}")
    else:
        st.info("No completed orders available.")

    st.subheader("❌ Rejected Orders")
    if not rejected_orders.empty:
        for poid, group in rejected_orders.groupby("poid"):
            order_info = group.iloc[0]
            with st.expander(f"📦 PO #{poid} - {order_info['suppliername']}"):
                st.write(f"**Order Date:** {order_info['orderdate']}")
                st.write(f"**Rejected on:** {order_info['respondedat']}")
                for idx, item in group.iterrows():
                    cols = st.columns([1, 3, 2])
                    if item['itempicture']:
                        cols[0].image(BytesIO(item['itempicture']), width=50)
                    else:
                        cols[0].write("No Image")
                    cols[1].write(f"{item['itemnameenglish']}")
                    cols[2].write(f"Ordered: {item['orderedquantity']}")
    else:
        st.info("No rejected orders available.")
