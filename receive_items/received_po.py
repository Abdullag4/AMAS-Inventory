import streamlit as st
from receive_items.receive_handler import ReceiveHandler

receive_handler = ReceiveHandler()

def received_po_tab():
    st.header("📥 Received Purchase Orders")

    received_pos = receive_handler.get_received_pos()

    if received_pos.empty:
        st.info("ℹ️ No received purchase orders pending inventory entry.")
        return

    selected_poid = st.selectbox(
        "Select Received Purchase Order",
        options=received_pos["poid"],
        format_func=lambda poid: f"PO #{poid}"
    )

    po_items = receive_handler.get_po_items(selected_poid)

    if po_items.empty:
        st.warning("⚠️ No items found for this PO.")
        return

    inventory_entries = []
    st.write("### Adjust Received Items & Enter Details")
    for idx, item in po_items.iterrows():
        st.subheader(f"{item['itemnameenglish']}")

        col_qty, col_exp, col_loc = st.columns([1, 1, 1])

        quantity = col_qty.number_input(
            "Received Quantity",
            value=item['receivedquantity'] if item['receivedquantity'] else item['orderedquantity'],
            min_value=0,
            key=f"qty_{item['itemid']}"
        )

        expiration_date = col_exp.date_input(
            "Expiration Date",
            key=f"exp_{item['itemid']}"
        )

        storage_location = col_loc.text_input(
            "Storage Location",
            key=f"loc_{item['itemid']}"
        )

        inventory_entries.append({
            "item_id": item["itemid"],
            "quantity": quantity,
            "expiration_date": expiration_date,
            "storage_location": storage_location
        })

    if st.button("Confirm and Add to Inventory"):
        for entry in inventory_entries:
            receive_handler.update_received_quantity(selected_poid, entry["item_id"], entry["quantity"])

        receive_handler.add_items_to_inventory(inventory_entries)
        receive_handler.mark_po_completed(selected_poid)

        st.success(f"✅ PO #{selected_poid} items successfully added to inventory!")
        st.rerun()
