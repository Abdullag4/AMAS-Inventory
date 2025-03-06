import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def add_item_tab():
    """Tab for adding new items, using dropdowns for some fields."""
    st.subheader("➕ Add New Item")

    # 1. Gather dropdown values from the Dropdowns table for each field
    classcat_options = db.get_dropdown_values("ClassCat")
    deptcat_options = db.get_dropdown_values("DepartmentCat")
    sectioncat_options = db.get_dropdown_values("SectionCat")
    familycat_options = db.get_dropdown_values("FamilyCat")
    subfamilycat_options = db.get_dropdown_values("SubFamilyCat")
    unittype_options = db.get_dropdown_values("UnitType")
    packaging_options = db.get_dropdown_values("Packaging")
    origin_options = db.get_dropdown_values("OriginCountry")
    manufacturer_options = db.get_dropdown_values("Manufacturer")
    brand_options = db.get_dropdown_values("Brand")

    # 2. Create input fields
    item_name_en = st.text_input("Item Name (English) *")
    item_name_ku = st.text_input("Item Name (Kurdish)")

    class_cat = st.selectbox("Class Category *", [""] + classcat_options)
    dept_cat = st.selectbox("Department Category *", [""] + deptcat_options)
    section_cat = st.selectbox("Section Category", [""] + sectioncat_options)
    family_cat = st.selectbox("Family Category", [""] + familycat_options)
    subfam_cat = st.selectbox("Sub-Family Category", [""] + subfamilycat_options)

    shelf_life = st.number_input("Shelf Life (days) *", min_value=0, step=1)
    origin_country = st.selectbox("Origin Country", [""] + origin_options)
    manufacturer = st.selectbox("Manufacturer", [""] + manufacturer_options)
    brand = st.selectbox("Brand", [""] + brand_options)
    barcode = st.text_input("Barcode")
    unit_type = st.selectbox("Unit Type", [""] + unittype_options)
    packaging = st.selectbox("Packaging", [""] + packaging_options)

    threshold = st.number_input("Threshold *", min_value=0, step=1)
    avg_required = st.number_input("Average Required *", min_value=0, step=1)
    item_picture = st.text_input("Item Picture URL")

    # 3. Fetch suppliers for multi-select
    suppliers_df = db.get_suppliers()
    if not suppliers_df.empty:
        supplier_names = suppliers_df["SupplierName"].tolist()
        selected_sup_names = st.multiselect("Select Supplier(s)", supplier_names)
        # Convert to SupplierID
        selected_sup_ids = []
        for name in selected_sup_names:
            # row matching name
            matched = suppliers_df[suppliers_df["SupplierName"] == name]
            if not matched.empty:
                selected_sup_ids.append(matched.iloc[0]["SupplierID"])
    else:
        st.warning("⚠️ No suppliers available. Please add them first.")
        selected_sup_ids = []

    # 4. On Add Item button
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

        # Insert item + link to suppliers
        item_id = db.add_item(item_data, selected_sup_ids)
        if item_id:
            st.success("✅ Item added successfully!")
        else:
            st.error("❌ Failed to add item. Possibly a duplicate or database issue.")
