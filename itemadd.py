import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def itemadd():
    """Page for adding new items to the inventory."""
    st.title("➕ Add New Item")

    # Define item fields dynamically
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

    # Generate input fields dynamically
    item_data = {}
    for key, label in item_fields.items():
        if key == "ShelfLife" or key == "Threshold" or key == "AverageRequired":
            item_data[key] = st.number_input(label, min_value=0, step=1)
        else:
            item_data[key] = st.text_input(label)

    # ✅ Fetch supplier list
    suppliers_df = db.fetch_data("SELECT SupplierID, SupplierName FROM Supplier")

    if suppliers_df.empty:
        st.warning("⚠️ No suppliers available! Please add suppliers first.")
        return  # Stop execution if no suppliers exist

    # ✅ Ensure correct column names
    suppliers_df.columns = suppliers_df.columns.str.lower()
    supplier_options = dict(zip(suppliers_df["suppliername"], suppliers_df["supplierid"]))

    # ✅ Supplier selection (multi-select)
    selected_supplier_names = st.multiselect("Select Supplier(s) *", list(supplier_options.keys()))

    # ✅ Ensure required fields are filled
    required_fields = ["ItemNameEnglish", "ClassCat", "DepartmentCat", "ShelfLife", "Threshold", "AverageRequired"]
    if st.button("Add Item"):
        if any(item_data[field] in [None, ""] for field in required_fields):
            st.error("❌ Please fill in all required fields before adding the item.")
            return

        # ✅ Insert item into the Item table first
        item_id = db.add_item(item_data)  # Ensure add_item() returns the new ItemID

        # ✅ Insert into ItemSupplier for each selected supplier
        if item_id and selected_supplier_names:
            for supplier_name in selected_supplier_names:
                supplier_id = supplier_options[supplier_name]  # Get SupplierID from dictionary
                db.add_item_supplier(item_id, supplier_id)  # ✅ New function to insert

        st.success("✅ Item and supplier(s) linked successfully!")

