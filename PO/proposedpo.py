# proposedpo.py
import streamlit as st
import pandas as pd
from io import BytesIO

def proposed_po_tab(po_handler):
    """
    Displays all POs with ProposedStatus='Proposed',
    and lets the user Accept, Modify, or Decline them.
    """
    st.subheader("📌 **Supplier Proposed Adjustments**")

    # Fetch all relevant data
    all_po = po_handler.get_all_purchase_orders()
    proposed_po_df = all_po[all_po["proposedstatus"] == "Proposed"]

    if proposed_po_df.empty:
        st.success("✅ No supplier proposals awaiting review.")
        return

    # Loop over each Proposed PO
    for poid in proposed_po_df["poid"].unique():
        po_data = proposed_po_df[proposed_po_df["poid"] == poid]
        po_info = po_data.iloc[0]

        st.markdown(f"## 📝 PO #{poid} from {po_info['suppliername']}")
        sup_note = po_info["suppliernote"] or "No note provided"
        st.markdown(f"**Supplier Note:** {sup_note}")

        # Safely handle the proposed date
        sup_date = po_info["supproposeddeliver"]
        if pd.notnull(sup_date):
            orig_date_str = (
                po_info["expecteddelivery"].date().isoformat()
                if pd.notnull(po_info["expecteddelivery"])
                else "N/A"
            )
            prop_date_str = sup_date.date().isoformat()
            st.markdown(
                f"**Original Delivery:** {orig_date_str} → "
                f"**Proposed Delivery:** {prop_date_str}"
            )
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
