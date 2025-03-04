import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def add_item_tab():
    """Tab for adding a new item to the database with supplier selection."""
    st.header("➕ Add New Item")

    # ✅ Define item fields dynamically
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
        "Threshold": "Minimum Stock Threshold *",
        "AverageRequired": "Average Stock Requirement *"
    }

    # ✅ Generate input fields dynamically
    item_data = {}
    for key, label in item_fields.items():
        if key in ["ShelfLife", "Threshold", "AverageRequired"]:
            item_data[key] = st.number_input(label, min_value=0, step=1)
        else:
            item_data[key] = st.text_input(label)

    # ✅ Fetch and Debug Supplier Data
    suppliers_df = db.get_suppliers()
    
    if not suppliers_df.empty and "SupplierName" in suppliers_df.columns:
        supplier_options = dict(zip(suppliers_df["SupplierName"], suppliers_df["SupplierID"]))  
        selected_supplier_names = st.multiselect("Select Supplier(s) *", list(supplier_options.keys()))

        # ✅ Convert selected names to supplier IDs
        selected_supplier_ids = [supplier_options[name] for name in selected_supplier_names]
    else:
        st.warning("⚠️ No suppliers available or missing SupplierName column in the database.")
        selected_supplier_ids = []

    # ✅ Handle Item Submission
    if st.button("Add Item"):
        required_fields = ["ItemNameEnglish", "ClassCat", "DepartmentCat", "ShelfLife", "Threshold", "AverageRequired"]
        if any(not item_data[field] for field in required_fields):
            st.error("❌ Please fill in all required fields before adding the item.")
            return
        
        if not selected_supplier_ids:
            st.error("❌ Please select at least one supplier.")
            return
        
        # ✅ Add the item and link suppliers
        item_id = db.add_item(item_data, selected_supplier_ids)
        if item_id:
            st.success("✅ Item added successfully and linked to suppliers!")
