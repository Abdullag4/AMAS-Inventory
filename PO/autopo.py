import streamlit as st
from io import BytesIO
from PIL import Image
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """Automatically generates a purchase order based on low stock levels."""
    st.subheader("📦 Automatic Purchase Order")

    # ✅ Fetch items near reorder with pictures included
    low_stock_items = po_handler.get_low_stock_items_with_supplier()

    if low_stock_items.empty:
        st.success("✅ All stock levels are sufficient. No orders required.")
        return

    st.write("⚠️ These items need restocking:")
    
    # ✅ Display items in a table format with images
    for idx, row in low_stock_items.iterrows():
        cols = st.columns([1, 2, 1, 2])

        # ✅ Convert image from BYTEA to display
        if row["ItemPicture"]:
            try:
                image = Image.open(BytesIO(row["ItemPicture"]))
                cols[0].image(image, width=60)
            except Exception:
                cols[0].write("No Image")
        else:
            cols[0].write("No Image")

        cols[1].write(row["ItemNameEnglish"])
        cols[2].write(f"Required: {int(row['RequiredQuantity'])}")
        cols[3].write(f"Supplier: {row['SupplierName']}")

    # ✅ Accept & Send Purchase Order
    if st.button("Accept and Send Order"):
        # ✅ Group items by supplier
        suppliers = low_stock_items.groupby("SupplierID")

        for supplier_id, items in suppliers:
            supplier_name = items.iloc[0]["SupplierName"]
            expected_delivery = st.date_input(f"📅 Expected Delivery for {supplier_name}")

            po_items = items[["ItemID", "RequiredQuantity"]].to_dict(orient="records")

            # ✅ Create purchase order
            po_id = po_handler.create_purchase_order(supplier_id, expected_delivery, po_items)
            
            if po_id:
                st.success(f"✅ Purchase Order {po_id} sent to {supplier_name}!")

    st.write("---")
