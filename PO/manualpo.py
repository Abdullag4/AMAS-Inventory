import streamlit as st
from PO.po_handler import POHandler
import datetime

po_handler = POHandler()

def manual_po_tab():
    """Tab for creating manual purchase orders."""
    st.header("📜 Create Manual Purchase Order")

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

    # ✅ Select items to add to PO
    st.write("### 🏷️ Select Items for Purchase Order")
    po_items = []
    for _, row in items_df.iterrows():
        cols = st.columns([1, 3, 1, 2])  # ✅ Layout for image, name, quantity, and price
        cols[0].image(row["itempicture"], width=60) if row["itempicture"] else cols[0].write("No Image")
        cols[1].write(row["itemnameenglish"])
        quantity = cols[2].number_input(f"Qty {row['itemnameenglish']}", min_value=0, step=1)
        estimated_price = cols[3].number_input(f"Est. Price {row['itemnameenglish']}", min_value=0.0, step=0.1)
        
        if quantity > 0:
            po_items.append({"item_id": row["itemid"], "quantity": quantity, "estimated_price": estimated_price})

    # ✅ Create Purchase Order button
    if st.button("📤 Create Purchase Order"):
        if not po_items:
            st.error("❌ Please select at least one item.")
        else:
            po_id = po_handler.create_manual_po(selected_supplier_id, po_expected_delivery, po_items)  # ✅ Pass `items`
            if po_id:
                st.success(f"✅ Purchase Order #{po_id} created successfully!")
            else:
                st.error("❌ Failed to create purchase order. Please try again.")
