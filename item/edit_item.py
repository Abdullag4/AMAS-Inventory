import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def edit_item_tab():
    """Tab for editing existing item details."""
    st.header("✏️ Edit Item Details")

    # ✅ Fetch items
    items_df = db.get_items()

    # ✅ Debugging step - show available columns
    if items_df.empty:
        st.warning("⚠️ No items available for editing.")
        return

    # ✅ Dropdown for selecting an item
    item_options = dict(zip(items_df["itemnameenglish"], items_df["itemid"]))
    selected_item_name = st.selectbox("Select an item to edit", list(item_options.keys()))

    selected_item_id = item_options[selected_item_name]
    selected_item = items_df[items_df["itemid"] == selected_item_id].iloc[0]

    # ✅ Editable fields
    updated_data = {}
    for col in selected_item.index:
        if col not in ["itemid", "createdat", "updatedat"]:  # Prevent editing ID & timestamps
            unique_key = f"{col}_{selected_item_id}"  # Create a unique key for each input
            updated_data[col] = st.text_input(col.replace("_", " ").title(), selected_item[col], key=unique_key)


    if st.button("Update Item"):
        db.update_item(selected_item_id, updated_data)
