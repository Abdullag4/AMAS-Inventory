import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def add_item_tab():
    """Page for adding new items to the database, with dropdowns for certain fields."""

    st.subheader("➕ Add New Item")

    # Define item fields that remain text or numeric
    item_fields_text = {
        "ItemNameEnglish": "Item Name (English) *",
        "ItemNameKurdish": "Item Name (Kurdish)",
        "OriginCountry": "Origin Country",
        "Manufacturer": "Manufacturer",
        "Brand": "Brand",
        "Barcode": "Barcode",
        "UnitType": "Unit Type",
        "Packaging": "Packaging",
        "ItemPicture": "Item Picture URL"
    }

    # Numeric fields (ShelfLife, Threshold, AverageRequired, etc.)
    item_fields_numeric = {
        "ShelfLife": "Shelf Life (days) *",
        "Threshold": "Minimum Stock Threshold *",
        "AverageRequired": "Average Required Stock *"
    }

    # Fields that should be dropdowns (linked to the 'Dropdowns' table)
    dropdown_sections = {
        "ClassCat": "Class Category *",
        "DepartmentCat": "Department Category *",
        "SectionCat": "Section Category",
        "FamilyCat": "Family Category",
        "SubFamilyCat": "Sub-Family Category"
    }

    # Prepare item_data dict
    item_data = {}

    # 1️⃣ Handle text fields
    for key, label in item_fields_text.items():
        item_data[key] = st.text_input(label)

    # 2️⃣ Handle numeric fields
    for key, label in item_fields_numeric.items():
        item_data[key] = st.number_input(label, min_value=0, step=1)

    # 3️⃣ Handle dropdown fields from the 'Dropdowns' table
    for section_key, label in dropdown_sections.items():
        # Retrieve possible dropdown values for this section (section_key)
        dropdown_values = db.get_dropdown_values(section_key)
        if not dropdown_values:
            st.warning(f"No dropdown values found for '{section_key}'. Go to 'Manage Dropdowns' to add them.")
            # Let the user pick an empty state or fallback to text
            # For a real fallback, you'd do something like:
            # item_data[section_key] = st.text_input(f"{label} (No dropdowns found!)")
            # but for simplicity we do an empty list:
            selected_val = st.selectbox(label, ["-- No Values --"])
            if selected_val == "-- No Values --":
                item_data[section_key] = ""
            else:
                item_data[section_key] = selected_val
        else:
            selected_val = st.selectbox(label, dropdown_values)
            item_data[section_key] = selected_val

    # ✅ Fetch supplier list
    suppliers_df = db.get_suppliers()
    if suppliers_df.empty:
        st.warning("⚠️ No suppliers available! Please add suppliers first.")
        selected_supplier_ids = []
    else:
        # Convert to dictionary {SupplierName: SupplierID}
        supplier_options = dict(zip(suppliers_df["SupplierName"], suppliers_df["SupplierID"]))
        selected_supplier_names = st.multiselect("Select Supplier(s) *", list(supplier_options.keys()))
        # Convert chosen supplier names to IDs
        selected_supplier_ids = [supplier_options[name] for name in selected_supplier_names]

    # 🔹 Final check for required fields
    required_fields = ["ItemNameEnglish", "ClassCat", "DepartmentCat", "ShelfLife", "Threshold", "AverageRequired"]
    if st.button("Add Item"):
        # Check if required text/numeric fields are filled
        missing = [field for field in required_fields if not item_data.get(field)]
        if missing:
            st.error(f"❌ Please fill in all required fields: {', '.join(missing)}")
            return

        # Check if at least one supplier is selected
        if not selected_supplier_ids:
            st.error("❌ Please select at least one supplier.")
            return

        # Attempt to add the item
        item_id = db.add_item(item_data, selected_supplier_ids)
        if item_id:
            st.success("✅ Item added successfully and linked to suppliers!")
        else:
            st.error("❌ Failed to add the item. Check logs or DB for details.")
