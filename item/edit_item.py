import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def edit_item_tab():
    """Tab for editing existing items."""
    st.subheader("✏️ Edit Items")

    items_df = db.fetch_data("SELECT ItemID, ItemNameEnglish FROM Item")

    if items_df.empty:
        st.warning("⚠️ No items available for editing.")
        return

    item_options = dict(zip(items_df["ItemNameEnglish"], items_df["ItemID"]))
    selected_item_name = st.selectbox("Select an item to edit", list(item_options.keys()))
    selected_item_id = item_options[selected_item_name]

    item_data = db.fetch_data("SELECT * FROM Item WHERE ItemID = %s", (selected_item_id,))
    if not item_data.empty:
        item_data = item_data.iloc[0].to_dict()

        for key in item_data.keys():
            item_data[key] = st.text_input(key, item_data[key])

        if st.button("Update Item"):
            db.update_item(selected_item_id, item_data)
            st.success("✅ Item updated successfully!")
