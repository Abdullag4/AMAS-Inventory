import streamlit as st
import pandas as pd
from PO.po_handler import POHandler

po_handler = POHandler()

def manual_po_tab():
    """Allows users to manually create a purchase order."""
    st.header("📝 Create Manual Purchase Order")

    # ✅ Step 1: Select Supplier
    suppliers_df = po_handler.get_suppliers()
    if suppliers_df.empty:
        st.error("❌ No suppliers found. Please add suppliers first.")
        return

    supplier_options = dict(zip(suppliers_df["suppliername"], suppliers_df["supplierid"]))
    selected_supplier = st.selectbox("Select Supplier", list(supplier_options.keys()))

    # ✅ Step 2: Select Items
    items_df = po_handler.get_items()
    if items_df.empty:
        st.error("❌ No items found. Please add items first.")
        return

    # ✅ Show item names & pictures
    item_options = dict(zip(items_df["itemnameenglish"], items_df["itemid"]))
    selected_items = st.multiselect("Select Items", list(item_options.keys()))

    # ✅ Step 3: Enter Quantity & Estimated Price
    po_items = []
    for item_name in selected_items:
        item_id = item_options[item_name]
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.image(items_df[items_df["itemid"] == item_id]["itempicture"].values[0], width=60)

        with col2:
            quantity = st.number_input(f"Quantity for {item_name}", min_value=1, step=1, key=f"qty_{item_id}")

        with col3:
            estimated_price = st.number_input(f"Est. Price for {item_name}", min_value=0.0, step=0.1, key=f"price_{item_id}")

        po_items.append({"item_id": item_id, "quantity": quantity, "estimated_price": estimated_price})

    # ✅ Step 4: Create PO
    if st.button("📩 Create Purchase Order"):
        if not selected_supplier or not po_items:
            st.error("❌ Please select a supplier and at least one item.")
            return

        supplier_id = supplier_options[selected_supplier]

        # ✅ Insert Purchase Order & Link Items
        po_id = po_handler.create_manual_po(supplier_id, po_items)
        if po_id:
            st.success(f"✅ Purchase Order {po_id} created successfully!")
        else:
            st.error("❌ Error creating purchase order. Please try again.")
