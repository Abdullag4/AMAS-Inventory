import streamlit as st
import pandas as pd
from PO.po_handler import POHandler
from io import BytesIO

po_handler = POHandler()

def auto_po_tab():
    st.subheader("📦 Automatic Purchase Order")

    # Fetch items near reorder with pictures included
    low_stock_items = po_handler.get_low_stock_items_with_supplier()

    if low_stock_items.empty:
        st.success("✅ All stock levels are sufficient. No orders required.")
        return

    # Display items
    for idx, row in low_stock_items.iterrows():
        cols = st.columns([1, 2, 1, 2])

        # Convert memoryview to bytes before displaying
        if row['itempicture']:
            image_bytes = BytesIO(row['itempicture']).getvalue()
            cols[0].image(image_bytes, width=60)
        else:
            cols[0].write("No Image")

        cols[1].write(row['itemnameenglish'])
        cols[2].write(f"Required: {int(row['required_quantity'])}")
        cols[3].write(f"Supplier: {row['suppliername']}")

    if st.button("✅ Accept and Send PO"):
        po_handler.send_auto_po(low_stock_items)
        st.success("✅ Purchase Order sent successfully!")
