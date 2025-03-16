import streamlit as st
from PO.po_handler import POHandler
import datetime

po_handler = POHandler()

def manual_po_tab():
    """Tab for creating manual purchase orders."""
    st.header("📝 Create Manual Purchase Order")

    suppliers_df = po_handler.get_suppliers()
    items_df = po_handler.get_items()
    item_supplier_df = po_handler.get_item_supplier_mapping()

    if suppliers_df.empty or items_df.empty or item_supplier_df.empty:
        st.warning("⚠️ No suppliers or items available.")
        return

    supplier_options = suppliers_df.set_index("suppliername")["supplierid"].to_dict()
    selected_supplier_name = st.selectbox("🏢 Select Supplier", list(supplier_options.keys()))
    selected_supplier_id = supplier_options[selected_supplier_name]

    supplier_item_ids = item_supplier_df[item_supplier_df["supplierid"] == selected_supplier_id]["itemid"].tolist()
    filtered_items_df = items_df[items_df["itemid"].isin(supplier_item_ids)]

    if filtered_items_df.empty:
        st.warning("⚠️ No items available for this supplier.")
        return

    st.write("### 📅 Expected Delivery Date and Time")
    col_date, col_time = st.columns(2)
    delivery_date = col_date.date_input("Select Date", min_value=datetime.date.today())
    delivery_time = col_time.time_input("Select Time", value=datetime.time(9, 0))  # Default 9:00 AM

    po_expected_delivery = datetime.datetime.combine(delivery_date, delivery_time)

    st.write("### 🏷️ Select Items for Purchase Order")
    item_options = filtered_items_df.set_index("itemnameenglish")["itemid"].to_dict()
    selected_item_names = st.multiselect("🛒 Select Items", list(item_options.keys()))

    po_items = []
    for item_name in selected_item_names:
        item_id = item_options[item_name]

        st.write(f"**{item_name}**")
        col_qty, col_price = st.columns(2)
        
        quantity = col_qty.number_input(f"Quantity ({item_name})", min_value=1, step=1, key=f"qty_{item_id}")
        estimated_price = col_price.number_input(f"Estimated Price ({item_name})", min_value=0.0, step=0.01, key=f"price_{item_id}")

        po_items.append({
            "item_id": item_id,
            "quantity": quantity,
            "estimated_price": estimated_price if estimated_price > 0 else None
        })

    if st.button("📤 Submit Purchase Order"):
        if not po_items:
            st.error("❌ Please select at least one item.")
        else:
            created_by = st.session_state.get("user_email", "Unknown")
            po_id = po_handler.create_manual_po(selected_supplier_id, po_expected_delivery, po_items, created_by)
            if po_id:
                st.success(f"✅ Purchase Order #{po_id} created successfully by {created_by}!")
            else:
                st.error("❌ Failed to create purchase order. Please try again.")
