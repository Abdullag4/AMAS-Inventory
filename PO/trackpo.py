import streamlit as st
from PO.po_handler import POHandler
from io import BytesIO
import pandas as pd

po_handler = POHandler()

def track_po_tab():
    """Tab for tracking purchase orders."""
    st.header("🚚 Track Purchase Orders")

    # ✅ We have separate sections for active POs and proposed adjustments
    tabs = st.tabs(["📋 Active Orders", "📌 Proposed Adjustments"])

    # ─────────────────────────────────────────────────────────────
    # Tab 0: Active Orders
    # ─────────────────────────────────────────────────────────────
    with tabs[0]:
        po_details = po_handler.get_all_purchase_orders()

        # Filter out any that are 'Proposed' status, so we show only truly active
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
        # Safely parse these fields
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

    # ─────────────────────────────────────────────────────────────
    # Tab 1: Proposed Adjustments
    # ─────────────────────────────────────────────────────────────
    with tabs[1]:
        # We can re-fetch or reuse the same data:
        all_po = po_handler.get_all_purchase_orders()
        # Filter to show only Proposed
        proposed_po_df = all_po[all_po["proposedstatus"] == "Proposed"]

        if proposed_po_df.empty:
            st.success("✅ No supplier proposals awaiting review.")
            return

        st.subheader("📌 **Supplier Proposed Adjustments**")

        for poid in proposed_po_df["poid"].unique():
            po_data = proposed_po_df[proposed_po_df["poid"] == poid]
            po_info = po_data.iloc[0]

            st.markdown(f"## 📝 PO #{poid} from {po_info['suppliername']}")
            sup_note = po_info["suppliernote"] or "No note provided"
            st.markdown(f"**Supplier Note:** {sup_note}")

            # Safely handle the proposed date
            sup_date = po_info["supproposeddeliver"]
            if pd.notnull(sup_date):
                st.markdown(f"**Original Delivery:** {po_info['expecteddelivery'].date() if pd.notnull(po_info['expecteddelivery']) else 'N/A'} → **Proposed Delivery:** {sup_date.date()}")
            else:
                st.markdown("**Proposed Delivery Date:** Not specified")

            # Compare item-level proposals
            col_title = st.columns([3,2,2,2,2])
            headers = ["Item", "Orig Qty", "Prop Qty", "Orig Price", "Prop Price"]
            for col, header in zip(col_title, headers):
                col.write(f"**{header}**")

            for _, row in po_data.iterrows():
                row_cols = st.columns([3,2,2,2,2])
                row_cols[0].write(row["itemnameenglish"])
                row_cols[1].write(row["orderedquantity"])
                row_cols[2].write(row["supproposedquantity"])
                # Original price
                if pd.notnull(row["estimatedprice"]):
                    row_cols[3].write(f"${row['estimatedprice']:.2f}")
                else:
                    row_cols[3].write("N/A")
                # Proposed price
                if pd.notnull(row["supproposedprice"]):
                    row_cols[4].write(f"${row['supproposedprice']:.2f}")
                else:
                    row_cols[4].write("N/A")

            col_accept, col_modify, col_decline = st.columns(3)

            if col_accept.button(f"✅ Accept Proposal #{poid}", key=f"accept_{poid}"):
                new_poid = po_handler.accept_proposed_po(poid)
                st.success(f"Proposal accepted. New PO #{new_poid} created.")
                st.rerun()

            if col_modify.button(f"✏️ Modify Proposal #{poid}", key=f"modify_{poid}"):
                st.info("Modify functionality coming soon!")
                # Future: show a form to adjust proposed items again

            if col_decline.button(f"❌ Decline Proposal #{poid}", key=f"decline_{poid}"):
                po_handler.decline_proposed_po(poid)
                st.warning(f"Proposal #{poid} declined.")
                st.rerun()

            st.markdown("---")
