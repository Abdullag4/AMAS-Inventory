import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def add_item_tab():
    """Tab for adding new items, using dropdowns for some fields."""
    st.subheader("➕ Add New Item")

    # Fetch dropdown values
    dropdown_fields = [
        "ClassCat", "DepartmentCat", "SectionCat", "FamilyCat", "SubFamilyCat",
        "UnitType", "Packaging", "OriginCountry", "Manufacturer", "Brand"
    ]

    dropdown_values = {field: db.get_dropdown_values(field) for field in dropdown_fields}

    # Input fields
    item_name_en = st.text_input("Item Name (English) *")
    item_name_ku = st.text_input("Item Name (Kurdish)")

    class_cat = st.selectbox("Class Category *", [""] + dropdown_values["ClassCat"])
    dept_cat = st.selectbox("Department Category *", [""] + dropdown_values["DepartmentCat"])
    section_cat = st.selectbox("Section Category", [""] + dropdown_values["SectionCat"])
    family_cat = st.selectbox("Family Category", [""] + dropdown_values["FamilyCat"])
    subfam_cat = st.selectbox("Sub-Family Category", [""] + dropdown_values["SubFamilyCat"])

    shelf_life = st.number_input("Shelf Life (days) *", min_value=0, step=1)
    origin_country = st.selectbox("Origin Country", [""] + dropdown_values["OriginCountry"])
    manufacturer = st.selectbox("Manufacturer", [""] + dropdown_values["Manufacturer"])
    brand = st.selectbox("Brand", [""] + dropdown_values["Brand"])
    barcode = st.text_input("Barcode")
    unit_type = st.selectbox("Unit Type", [""] + dropdown_values["UnitType"])
    packaging = st.selectbox("Packaging", [""] + dropdown_values["Packaging"])

    threshold = st.number_input("Threshold *", min_value=0, step=1)
    avg_required = st.number_input("Average Required *", min_value=0, step=1)
    item_picture = st.text_input("Item Picture URL")

    # Fetch suppliers for multi-select (Corrected column names)
    suppliers_df = db.get_suppliers()
    if not suppliers_df.empty:
        supplier_names = suppliers_df["suppliername"].tolist()  # ✅ fixed capitalization
        selected_sup_names = st.multiselect("Select Supplier(s)", supplier_names)

        selected_sup_ids = suppliers_df[
            suppliers_df["suppliername"].isin(selected_sup_names)
        ]["supplierid"].tolist()  # ✅ fixed capitalization
    else:
        st.warning("⚠️ No suppliers available. Please add them first.")
        selected_sup_ids = []

    # Add Item button
    if st.button("Add Item"):
        required_fields = [item_name_en, class_cat, dept_cat, shelf_life, threshold, avg_required]
        if any(not x for x in required_fields):
            st.error("❌ Please fill in all required fields (English Name, ClassCat, DeptCat, ShelfLife, Threshold, AvgRequired).")
            return

        item_data = {
            "ItemNameEnglish": item_name_en,
            "ItemNameKurdish": item_name_ku,
            "ClassCat": class_cat,
            "DepartmentCat": dept_cat,
            "SectionCat": section_cat,
            "FamilyCat": family_cat,
            "SubFamilyCat": subfam_cat,
            "ShelfLife": shelf_life,
            "OriginCountry": origin_country,
            "Manufacturer": manufacturer,
            "Brand": brand,
            "Barcode": barcode,
            "UnitType": unit_type,
            "Packaging": packaging,
            "Threshold": threshold,
            "AverageRequired": avg_required,
            "ItemPicture": item_picture
        }

        item_id = db.add_item(item_data, selected_sup_ids)
        if item_id:
            st.success("✅ Item added successfully!")
        else:
            st.error("❌ Failed to add item. Possibly a duplicate or database issue.")
