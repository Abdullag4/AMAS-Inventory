import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def itemadd():
    """Page for adding new items to the inventory."""
    st.title("➕ Add New Item")

    # ✅ Fetch supplier list
    suppliers_df = db.fetch_data("SELECT SupplierID, SupplierName FROM Supplier")

    if suppliers_df.empty:
        st.warning("⚠️ No suppliers available! Please add suppliers first.")
        return  # Stop execution if no suppliers exist

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
        "Threshold": "Reorder Threshold *",
        "AverageRequired": "Average Required Quantity *"
    }

    # Generate input fields dynamically
    item_data = {}
    for key, label in item_fields.items():
        if key in ["ShelfLife", "Threshold", "AverageRequired"]:
            item_data[key] = st.number_input(label, min_value=1, step=1)
        else:
            item_data[key] = st.text_input(label)

    # ✅ Supplier selection (multi-select)
    supplier_options = dict(zip(suppliers_df["SupplierName"], suppliers_df["SupplierID"]))
    selected_supplier_names = st.multiselect("Select Supplier(s) *", list(supplier_options.keys()))
    
    if st.button("Add Item"):
        # ✅ Check if required fields are filled
        required_fields = ["ItemNameEnglish", "ClassCat", "DepartmentCat", "ShelfLife", "Threshold", "AverageRequired"]
        if any(not item_data[field] for field in required_fields):
            st.warning("⚠️ Please fill all required fields before adding the item.")
            return
        
        # ✅ Ensure at least one supplier is selected
        if not selected_supplier_names:
            st.warning("⚠️ Please select at least one supplier.")
            return

        # ✅ Add the item to the database
        item_id = db.add_item(item_data)  # Returns the newly added ItemID

        if item_id:
            # ✅ Link the item to selected suppliers in ItemSupplier
            for supplier_name in selected_supplier_names:
                supplier_id = supplier_options[supplier_name]
                db.add_item_supplier(item_id, supplier_id)

            st.success(f"✅ Item '{item_data['ItemNameEnglish']}' added successfully and linked to suppliers!")

if __name__ == "__main__":
    itemadd()
