# proposedpo.py
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date, datetime

def proposed_po_tab(po_handler):
    """
    Displays all POs with ProposedStatus='Proposed',
    and lets the user Accept, Modify, or Decline them.
    """
    st.subheader("📌 **Supplier Proposed Adjustments**")

    all_po = po_handler.get_all_purchase_orders()
    proposed_po_df = all_po[all_po["proposedstatus"] == "Proposed"]

    if proposed_po_df.empty:
        st.success("✅ No supplier proposals awaiting review.")
        return

    for poid in proposed_po_df["poid"].unique():
        po_data = proposed_po_df[proposed_po_df["poid"] == poid]
        po_info = po_data.iloc[0]

        st.markdown(f"## 📝 PO #{poid} from {po_info['suppliername']}")
        sup_note = po_info["suppliernote"] or "No note provided"
        st.markdown(f"**Supplier Note:** {sup_note}")

        sup_date = po_info["supproposeddeliver"]
        orig_date = po_info["expecteddelivery"]

        if pd.notnull(sup_date):
            orig_str = orig_date.date().isoformat() if pd.notnull(orig_date) else "N/A"
            prop_str = pd.to_datetime(sup_date).date().isoformat()
            st.markdown(
                f"**Original Delivery:** {orig_str} → "
                f"**Proposed Delivery:** {prop_str}"
            )
        else:
            st.markdown("**Proposed Delivery Date:** Not specified")

        # Compare item-level proposals
        col_title = st.columns([3,2,2,2,2])
        headers = ["Item", "Orig Qty", "Prop Qty", "Orig Price", "Prop Price"]
        for c, h in zip(col_title, headers):
            c.write(f"**{h}**")

        for _, row in po_data.iterrows():
            row_cols = st.columns([3,2,2,2,2])
            row_cols[0].write(row["itemnameenglish"])
            row_cols[1].write(row["orderedquantity"])
            row_cols[2].write(row["supproposedquantity"])
            if pd.notnull(row["estimatedprice"]):
                row_cols[3].write(f"${row['estimatedprice']:.2f}")
            else:
                row_cols[3].write("N/A")
            if pd.notnull(row["supproposedprice"]):
                row_cols[4].write(f"${row['supproposedprice']:.2f}")
            else:
                row_cols[4].write("N/A")

        col_accept, col_modify, col_decline = st.columns(3)

        if col_accept.button(f"✅ Accept Proposal #{poid}", key=f"accept_{poid}"):
            new_poid = po_handler.accept_proposed_po(poid)
            st.success(f"Proposal accepted. New PO #{new_poid} created.")
            st.rerun()

        # --- Modify proposal
        if col_modify.button(f"✏️ Modify Proposal #{poid}", key=f"modify_{poid}"):
            st.session_state[f"show_modify_form_{poid}"] = True

        if st.session_state.get(f"show_modify_form_{poid}", False):
            # Show a form that let's user fully override the date + items
            st.info("Adjust the proposed date and item lines, then click 'Submit Modified Proposal'.")

            # Proposed date
            default_date = date.today()
            if pd.notnull(sup_date):
                default_date = pd.to_datetime(sup_date).date()
            user_date = st.date_input("New Delivery Date", default_date, key=f"user_date_{poid}")

            # Build item-level modifications
            mod_items = []
            st.write("### Edit Item Lines")

            # We'll do a small table approach
            # for each row, let's allow user to override quantity, price
            for idx, row in po_data.iterrows():
                st.write(f"**{row['itemnameenglish']}**")
                c1, c2 = st.columns(2)

                # Proposed quantity
                default_qty = row["supproposedquantity"] or row["orderedquantity"]
                user_qty = c1.number_input(
                    f"Qty (PO{poid}, Item {row['itemid']})", 
                    min_value=1, 
                    value=int(default_qty), 
                    step=1, 
                    key=f"user_qty_{poid}_{row['itemid']}"
                )

                # Proposed price
                default_price = row["supproposedprice"] or row["estimatedprice"] or 0.0
                user_price = c2.number_input(
                    f"Price (PO{poid}, Item {row['itemid']})", 
                    value=float(default_price), 
                    step=0.01, 
                    key=f"user_price_{poid}_{row['itemid']}"
                )

                mod_items.append({
                    "item_id": row["itemid"],
                    "quantity": user_qty,
                    "estimated_price": user_price
                })
            
            if st.button("Submit Modified Proposal", key=f"submit_mod_{poid}"):
                # Call the new method in po_handler
                # Convert user_date to a Python datetime
                user_dt = datetime.combine(user_date, datetime.min.time())

                new_poid = po_handler.modify_proposed_po(
                    proposed_po_id=poid,
                    new_delivery_date=user_dt,
                    new_items=mod_items,
                    user_email=st.session_state.get("user_email", "Unknown")
                )
                st.success(f"✅ New PO #{new_poid} created from modifications. Original PO marked as 'Modified'.")
                st.rerun()

        # --- Decline
        if col_decline.button(f"❌ Decline Proposal #{poid}", key=f"decline_{poid}"):
            po_handler.decline_proposed_po(poid)
            st.warning(f"Proposal #{poid} declined.")
            st.rerun()

        st.markdown("---")
