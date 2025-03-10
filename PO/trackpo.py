import streamlit as st
from PO.po_handler import POHandler

po_handler = POHandler()

def track_po_tab():
    """Enhanced tab for tracking purchase orders with a summary table and detailed tracking."""
    st.header("📋 Purchase Order Tracking")

    # ✅ Fetch all purchase orders
    po_details = po_handler.get_all_purchase_orders()

    if po_details.empty:
        st.info("ℹ️ No purchase orders found.")
        return

    # ✅ Show Summary Table (Quick Overview)
    st.subheader("📊 Overview of Purchase Orders")
    summary_df = po_details.groupby(["poid", "suppliername", "status", "expecteddelivery"], as_index=False).agg(
        order_date=("orderdate", "first")
    )

    # ✅ Reorder columns for better readability
    summary_df = summary_df[["poid", "suppliername", "status", "expecteddelivery", "order_date"]]
    summary_df.columns = ["PO Number", "Supplier", "Status", "Expected Delivery", "Order Date"]

    st.dataframe(summary_df, use_container_width=True)

    # ✅ Select PO to track
    st.subheader("🚚 Track Purchase Order Details")
    selected_poid = st.selectbox("📌 Select a Purchase Order", summary_df["PO Number"].unique())

    # ✅ Filter selected PO details
    selected_po = po_details[po_details["poid"] == selected_poid]

    if not selected_po.empty:
        # ✅ Display General Information
        order_info = selected_po.iloc[0]
        st.write(f"**📑 Purchase Order #:** {order_info['poid']}")
        st.write(f"**🏢 Supplier:** {order_info['suppliername']}")
        st.write(f"**📅 Order Date:** {order_info['orderdate']}")
        st.write(f"**🚀 Expected Delivery:** {order_info['expecteddelivery']}")
        st.write(f"**📌 Status:** {order_info['status']}")

        # ✅ Show Item Details
        st.subheader("🛒 Items in Purchase Order")
        for idx, row in selected_po.iterrows():
            with st.expander(f"📦 {row['itemnameenglish']} ({row['quantity']} units)"):
                st.write(f"**🔢 Item ID:** {row['itemid']}")
                st.write(f"**📌 Ordered Quantity:** {row['quantity']} units")
                st.write(f"**💰 Estimated Price:** {row['estimatedprice'] if row['estimatedprice'] else 'Not Provided'}")
                
                # ✅ Display image if available
                if row["itempicture"]:
                    st.image(row["itempicture"], width=120, caption=row["itemnameenglish"])
                else:
                    st.write("🖼 No Image Available")
        
        st.success("✅ Purchase Order Tracking Loaded Successfully!")
