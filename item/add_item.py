import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def add_item_tab():
    """Tab for adding new items manually."""
    st.subheader("➕ Add New Item")

    # Define required fields
    item_fields = {
        "ItemNameEnglish": "Item Name (English) *",
        "ItemNameKurdish": "Item Name (Kurdish)",
        "ClassCat": "Class Category *",
        "DepartmentCat": "Department Category *",
        "SectionCat": "Section Category",
        "FamilyCat": "Family Category",
        "SubFamilyCat": "Sub-Family Category",
        "ShelfLife": "Shelf Life (days) *",
        "OriginCountry": "Origin Country",
        "Manufacturer": "Manufacturer",
        "Brand": "Brand",
        "Barcode": "Barcode",
        "UnitType": "Unit Type",
        "Packaging": "Packaging",
        "ItemPicture": "Item Picture URL",
        "Threshold": "Threshold *",
        "AverageRequired": "Average Required *"
    }

    # ✅ Input fields
    item_data = {}
    for key, label in item_fields.items():
        if key in ["ShelfLife", "Threshold", "AverageRequired"]:
            item_data[key] = st.number_input(label, min_value=0, step=1)
        else:
            item_data[key] = st.text_input(label)

    # ✅ Fetch supplier list
    suppliers_df = db.fetch_data("SELECT SupplierID, SupplierName FROM Supplier")

    if suppliers_df.empty:
        st.warning("⚠️ No suppliers available! Please add suppliers first.")
        return  

    # ✅ Supplier selection
    suppliers_df.columns = suppliers_df.columns.str.lower()
    supplier_options = dict(zip(suppliers_df["suppliername"], suppliers_df["supplierid"]))
    selected_supplier_names = st.multiselect("Select Supplier(s) *", list(supplier_options.keys()))

    # ✅ Ensure required fields are filled
    required_fields = ["ItemNameEnglish", "ClassCat", "DepartmentCat", "ShelfLife", "Threshold", "AverageRequired"]
    if st.button("Add Item"):
        if any(item_data[field] in [None, ""] for field in required_fields):
            st.error("❌ Please fill in all required fields before adding the item.")
            return

        item_id = db.add_item(item_data)
        if item_id and selected_supplier_names:
            for supplier_name in selected_supplier_names:
                supplier_id = supplier_options[supplier_name]
                db.add_item_supplier(item_id, supplier_id)

        st.success("✅ Item and supplier(s) linked successfully!")
