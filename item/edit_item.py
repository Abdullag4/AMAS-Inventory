import streamlit as st
from item.item_handler import ItemHandler

item_handler = ItemHandler()

def edit_item_tab():
    """Tab for editing existing item details, including suppliers."""
    st.header("✏️ Edit Item Details")

    # ✅ Fetch items
    items_df = item_handler.get_items()

    if items_df.empty:
        st.warning("⚠️ No items available for editing.")
        return

    # ✅ Select item to edit
    item_options = dict(zip(items_df["itemnameenglish"], items_df["itemid"]))
    selected_item_name = st.selectbox("Select an item to edit", list(item_options.keys()))
    selected_item_id = item_options[selected_item_name]

    # ✅ Fetch item details
    selected_item = items_df[items_df["itemid"] == selected_item_id].iloc[0]

    # ✅ Fetch suppliers linked to this item
    suppliers_df = item_handler.get_suppliers()
    linked_suppliers = item_handler.get_item_suppliers(selected_item_id)

    # ✅ Display editable fields
    updated_data = {}
    for col in selected_item.index:
        if col not in ["itemid", "createdat", "updatedat"]:  # Prevent modifying ID & timestamps
            updated_data[col] = st.text_input(col.replace("_", " ").title(), value=str(selected_item[col]), key=f"edit_{col}")

    # ✅ Supplier selection (multi-select)
    if not suppliers_df.empty:
        supplier_options = dict(zip(suppliers_df["suppliername"], suppliers_df["supplierid"]))
        selected_suppliers = st.multiselect("Edit Suppliers", list(supplier_options.keys()), default=linked_suppliers)
        selected_supplier_ids = [supplier_options[name] for name in selected_suppliers]
    else:
        selected_supplier_ids = []
        st.warning("⚠️ No suppliers available in the database.")

    # ✅ Update Button
    if st.button("Update Item"):
        item_handler.update_item(selected_item_id, updated_data)
        item_handler.update_item_suppliers(selected_item_id, selected_supplier_ids)
        st.success("✅ Item details and suppliers updated successfully!")
