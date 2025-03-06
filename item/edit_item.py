import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def edit_item_tab():
    st.header("✏️ Edit Item Details")

    items_df = db.get_items()
    if items_df.empty:
        st.warning("⚠️ No items available for editing.")
        return

    # For clarity: let's rename columns to lowercase
    items_df.columns = items_df.columns.str.lower()

    if "itemnameenglish" not in items_df.columns:
        st.error("❌ 'ItemNameEnglish' column not found in 'Item' table.")
        return

    item_options = dict(zip(items_df["itemnameenglish"], items_df["itemid"]))
    selected_item_name = st.selectbox("Select an item to edit", list(item_options.keys()))
    selected_item_id = item_options[selected_item_name]

    selected_item = items_df[items_df["itemid"] == selected_item_id].iloc[0]

    # Editable fields
    updated_data = {}
    for col in selected_item.index:
        if col not in ["itemid", "createdat", "updatedat"]:
            updated_data[col] = st.text_input(col.title(), value=str(selected_item[col]))

    # Supplier multi-select
    suppliers_df = db.get_suppliers()
    if not suppliers_df.empty:
        # => columns = ["supplierid", "suppliername"]
        supplier_names = suppliers_df["suppliername"].tolist()
        # get existing supplier names for this item
        linked_suppliers = db.get_item_suppliers(selected_item_id)
        # multi-select with pre-selected suppliers
        selected_suppliers = st.multiselect("Edit Suppliers", supplier_names, default=linked_suppliers)

        selected_supplier_ids = []
        for sname in selected_suppliers:
            match = suppliers_df[suppliers_df["suppliername"] == sname]
            if not match.empty:
                selected_supplier_ids.append(match.iloc[0]["supplierid"])
    else:
        st.warning("No suppliers found. Please add them first.")
        selected_supplier_ids = []

    # Update button
    if st.button("Update Item"):
        db.update_item(selected_item_id, updated_data)
        db.update_item_suppliers(selected_item_id, selected_supplier_ids)
        st.success("✅ Updated item and suppliers!")
