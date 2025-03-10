import streamlit as st
from PO.po_handler import POHandler
import datetime

po_handler = POHandler()

def manual_po_tab():
    """Tab for creating manual purchase orders."""
    st.header("📝 Create Manual Purchase Order")

    # ✅ Load suppliers and items
    suppliers_df = po_handler.get_suppliers()
    items_df = po_handler.get_items()

    if suppliers_df.empty or items_df.empty:
        st.warning("⚠️ No suppliers or items available.")
        return

    # ✅ Supplier selection
    supplier_options = suppliers_df.set_index("suppliername")["supplierid"].to_dict()
    selected_supplier_name = st.selectbox("🏢 Select Supplier", list(supplier_options.keys()))
    selected_supplier_id = supplier_options[selected_supplier_name]

    # ✅ Expected delivery date
    po_expected_delivery = st.date_input("📅 Expected Delivery Date", min_value=datetime.date.today())

    # ✅ Item selection with quantities & estimated prices
    st.write("### 🏷️ Select Items for Purchase Order")
    
    item_options = items_df.set_index("itemnameenglish")["itemid"].to_dict()
    selected_item_names = st.multiselect("🛒 Select Items", list(item_options.keys()))

    po_items = []
    for item_name in selected_item_names:
        item_id = item_options[item_name]

        # ✅ Display item details
        st.write(f"**{item_name}**")
        col_qty, col_price = st.columns(2)
        
        quantity = col_qty.number_input(f"Quantity ({item_name})", min_value=1, step=1, key=f"qty_{item_id}")
        estimated_price = col_price.number_input(f"Estimated Price ({item_name})", min_value=0.0, step=0.01, key=f"price_{item_id}")

        po_items.append({
            "item_id": item_id,
            "quantity": quantity,
            "estimated_price": estimated_price if estimated_price > 0 else None
        })

    # ✅ Create Purchase Order button
    if st.button("📤 Submit Purchase Order"):
        if not po_items:
            st.error("❌ Please select at least one item.")
        else:
            po_id = po_handler.create_manual_po(selected_supplier_id, po_expected_delivery, po_items)
            if po_id:
                st.success(f"✅ Purchase Order #{po_id} created successfully!")
            else:
                st.error("❌ Failed to create purchase order. Please try again.")
