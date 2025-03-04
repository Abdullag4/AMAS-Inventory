import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def edit_item_tab():
    """Tab for editing existing items in the inventory."""
    st.header("✏️ Edit Item Details")

    # ✅ Fetch items
    items_df = db.get_items()

    if items_df.empty:
        st.warning("⚠️ No items available for editing.")
        return

    # ✅ Normalize column names to lowercase
    items_df.columns = items_df.columns.str.lower()

    if "itemnameenglish" not in items_df.columns:
        st.error("⚠️ 'ItemNameEnglish' column not found in database.")
        st.stop()

    # ✅ Create dropdown options
    item_options = dict(zip(items_df["itemnameenglish"], items_df["itemid"]))
    
    selected_item_name = st.selectbox("Select an item to edit", list(item_options.keys()))
    selected_item_id = item_options[selected_item_name]

    # ✅ Retrieve selected item details
    selected_item = items_df[items_df["itemid"] == selected_item_id].iloc[0]

    # ✅ Editable fields with unique keys
    updated_data = {}
    for col in selected_item.index:
        if col not in ["itemid", "createdat", "updatedat"]:  # Prevent editing ID and timestamps
            updated_data[col] = st.text_input(
                col.replace("_", " ").title(), 
                value=str(selected_item[col]), 
                key=f"{col}_{selected_item_id}"  # ✅ Unique key to avoid duplicate element IDs
            )

    if st.button("Update Item"):
        db.update_item(selected_item_id, updated_data)
