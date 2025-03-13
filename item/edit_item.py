import streamlit as st
from item.item_handler import ItemHandler
from io import BytesIO

item_handler = ItemHandler()

def edit_item_tab():
    """Tab for editing existing item details, including suppliers and pictures."""
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
        if col not in ["itemid", "createdat", "updatedat", "itempicture"]:  # Exclude non-editable fields
            updated_data[col] = st.text_input(col.replace("_", " ").title(), value=str(selected_item[col]), key=f"edit_{col}")

    # ✅ Display and update item picture
    st.subheader("🖼️ Item Picture")
    if selected_item["itempicture"]:
        image_data = BytesIO(selected_item["itempicture"])
        st.image(image_data, width=150, caption="Current Item Picture")
    else:
        st.info("ℹ️ No image available for this item.")

    uploaded_image = st.file_uploader("Upload a new image (Optional)", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        updated_data["itempicture"] = uploaded_image.getvalue()  # Convert uploaded image to binary

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
        st.rerun()  # Refresh the page to reflect updates
