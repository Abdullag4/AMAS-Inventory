import streamlit as st
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    st.header("📦 Automatic Purchase Order")

    low_stock_items = po_handler.get_items_below_threshold()

    if not low_stock_items.empty:
        st.write("**Items Recommended for Order:**")

        for idx, row in low_stock_items.iterrows():
            cols = st.columns([1, 2, 1, 2])
            cols[0].image(row['itempicture'], width=60)
            cols[1].write(row['itemnameenglish'])
            cols[2].write(f"Required: {int(row['required_quantity'])}")
            cols[3].write(f"Supplier: {row['suppliername']}")

        if st.button("✅ Accept & Send Purchase Orders"):
            po_handler.create_auto_purchase_orders(low_stock_items)
            st.success("✅ Purchase orders successfully created and sent!")
    else:
        st.success("🎉 All stock levels are sufficient!")
