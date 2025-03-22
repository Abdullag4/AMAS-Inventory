import streamlit as st
from PO.po_handler import POHandler
from io import BytesIO
import pandas as pd

po_handler = POHandler()

def track_po_tab():
    st.header("🚚 Track Purchase Orders")

    tabs = st.tabs(["📋 Active Orders", "📌 Proposed Adjustments"])

    with tabs[0]:
        po_details = po_handler.get_all_purchase_orders()

        active_po_df = po_details[po_details["proposedstatus"] != "Proposed"]
        if active_po_df.empty:
            st.info("ℹ️ No active purchase orders found.")
        else:
            summary_df = active_po_df[["poid", "suppliername", "status", "expecteddelivery"]].drop_duplicates()
            summary_df.columns = ["PO ID", "Supplier", "Status", "Expected Delivery"]
            st.subheader("📋 **Active Purchase Orders Summary**")
            st.dataframe(summary_df, hide_index=True, use_container_width=True)

    with tabs[1]:
        proposed_po_df = po_details[po_details["proposedstatus"] == "Proposed"]
        if proposed_po_df.empty:
            st.success("✅ No supplier proposals awaiting review.")
        else:
            st.subheader("📌 **Supplier Proposed Adjustments**")
            for poid in proposed_po_df["poid"].unique():
                po_data = proposed_po_df[proposed_po_df["poid"] == poid]
                po_info = po_data.iloc[0]

                st.markdown(f"## 📝 PO #{poid} from {po_info['suppliername']}")
                st.markdown(f"**Supplier Note:** {po_info['suppliernote']}")
                st.markdown(f"**Original Delivery:** {po_info['expecteddelivery'].date()} → **Proposed Delivery:** {po_info['supproposeddeliver'].date()}")

                cols = st.columns([3,2,2,2,2])
                headers = ["Item", "Orig Qty", "Prop Qty", "Orig Price", "Prop Price"]
                for col, header in zip(cols, headers):
                    col.write(f"**{header}**")

                for _, row in po_data.iterrows():
                    cols = st.columns([3,2,2,2,2])
                    cols[0].write(row["itemnameenglish"])
                    cols[1].write(row["orderedquantity"])
                    cols[2].write(row["supproposedquantity"])
                    cols[3].write(f"${row['estimatedprice']:.2f}")
                    cols[4].write(f"${row['supproposedprice']:.2f}")

                col_accept, col_modify, col_decline = st.columns(3)

                if col_accept.button(f"✅ Accept Proposal #{poid}", key=f"accept_{poid}"):
                    new_poid = po_handler.accept_proposed_po(poid)
                    st.success(f"Proposal accepted. New PO #{new_poid} created.")
                    st.rerun()

                if col_decline.button(f"❌ Decline Proposal #{poid}", key=f"decline_{poid}"):
                    po_handler.decline_proposed_po(poid)
                    st.warning(f"Proposal #{poid} declined.")
                    st.rerun()

                if col_modify.button(f"✏️ Modify Proposal #{poid}", key=f"modify_{poid}"):
                    st.info("Modify functionality coming soon!")

                st.markdown("---")
