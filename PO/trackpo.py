import streamlit as st
from PO.po_handler import POHandler

po_handler = POHandler()

def track_po_tab():
    """Enhanced tab for tracking purchase orders."""
    st.header("🚚 Track Purchase Orders")

    # ✅ Fetch all purchase orders
    po_details = po_handler.get_all_purchase_orders()

    if po_details.empty:
        st.info("ℹ️ No purchase orders found.")
        return

    # ✅ Convert POID to string for selection
    po_details["poid"] = po_details["poid"].astype(str)

    # ✅ Dropdown to select a purchase order
    selected_poid = st.selectbox("📋 Select a Purchase Order", po_details["poid"].unique())

    # ✅ Filter details for the selected PO
    selected_po = po_details[po_details["poid"] == selected_poid]

    # ✅ Display Order Info
    st.subheader(f"📦 Order #{selected_poid}")
    
    # ✅ Extract relevant details
    order_status = selected_po.iloc[0]["status"]
    order_date = selected_po.iloc[0]["orderdate"]
    expected_delivery = selected_po.iloc[0]["expecteddelivery"]
    responded_at = selected_po.iloc[0]["respondedat"]
    supplier_name = selected_po.iloc[0]["suppliername"]

    # ✅ Horizontal Progress Tracker
    status_mapping = {
        "Pending": 0, "Accepted": 1, "Declined": 1,
        "Shipping": 2, "Received": 3
    }
    status_stage = status_mapping.get(order_status, 0)
    
    st.progress(status_stage / 3.0)

    st.markdown(f"""
    **📅 Order Date:** {order_date}  
    **📦 Expected Delivery:** {expected_delivery}  
    **🏢 Supplier:** {supplier_name}  
    **⏳ Responded At:** {responded_at if responded_at else "Not yet responded"}  
    **🚦 Current Status:** `{order_status}`
    """)

    st.write("---")

    # ✅ Display Order Items in Card Format
    st.subheader("📦 Ordered Items")
    for _, row in selected_po.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            if row["itempicture"]:
                col1.image(row["itempicture"], width=80)
            else:
                col1.write("📷 No Image")

            col2.write(f"**🏷️ {row['itemnameenglish']}**")
            col3.write(f"🔢 Quantity: `{row['quantity']}`")
            col4.write(f"💰 Est. Price: `{row['estimatedprice'] if row['estimatedprice'] else 'N/A'}`")

    st.write("---")

    # ✅ Optional: Status Update Button
    if order_status != "Received" and st.button("✅ Mark as Received"):
        po_handler.update_order_status(selected_poid, "Received")
        st.success(f"✅ Order #{selected_poid} marked as Received!")

