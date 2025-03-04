import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def edit_item_tab():
    """Tab for editing existing items in the inventory."""
    st.header("✏️ Edit Item Details")

    # ✅ Fetch items
    items_df = db.get_items()

    # ✅ Debugging step - show available columns
    st.write("🔍 Columns in items_df:", items_df.columns.tolist())
    st.dataframe(items_df)  

    # ✅ Normalize column names to lowercase
    items_df.columns = items_df.columns.str.lower()

    if "itemnameenglish" not in items_df.columns:
        st.error("⚠️ 'ItemNameEnglish' column not found in database.")
        st.stop()

    # ✅ Create dropdown options
    item_options = dict(zip(items_df["itemnameenglish"], items_df["itemid"]))
    
    if not item_options:
        st.warning("⚠️ No items available for editing.")
        return

    selected_item_name = st.selectbox("Select an item to edit", list(item_options.keys()))
    selected_item_id = item_options[selected_item_name]

    # ✅ Display item details
    selected_item = items_df[items_df["itemid"] == selected_item_id].iloc[0]

    # Editable fields
    updated_data = {}
    for col in selected_item.index:
        if col not in ["itemid", "createdat", "updatedat"]:  # Prevent editing ID and timestamps
            updated_data[col] = st.text_input(col.replace("_", " ").title(), value=str(selected_item[col]))

    if st.button("Update Item"):
        query = f"""
        UPDATE item SET {", ".join([f"{key} = %s" for key in updated_data.keys()])}, updatedat = CURRENT_TIMESTAMP
        WHERE itemid = %s
        """
        db.execute_command(query, list(updated_data.values()) + [selected_item_id])
        st.success("✅ Item details updated successfully!")
