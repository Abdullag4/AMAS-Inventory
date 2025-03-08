import streamlit as st
from PO.po_handler import POHandler
from io import BytesIO
from PIL import Image

po_handler = POHandler()

def auto_po_tab():
    st.subheader("📦 Automatic Purchase Order")

    # Fetch items near reorder with pictures included
    low_stock_items = po_handler.get_low_stock_items_with_supplier()

    if low_stock_items.empty:
        st.success("✅ All stock levels are sufficient. No orders required.")
        return

    st.write("Review items that need reordering:")

    for idx, row in low_stock_items.iterrows():
        cols = st.columns([1, 2, 1, 2])

        # Safely handle image bytes
        if row['itempicture']:
            try:
                image = Image.open(BytesIO(row['itempicture']))
                cols[0].image(image, width=60)
            except Exception as e:
                cols[0].write("Invalid Image")
        else:
            cols[0].write("No Image")

        cols[1].write(row['itemnameenglish'])
        cols[2].write(f"Required: {int(row['required_quantity'])}")
        cols[3].write(f"Supplier: {row['suppliername']}")

    if st.button("Accept and Send Order"):
        po_handler.send_auto_po(low_stock_items)
        st.success("✅ Purchase orders have been sent successfully!")
